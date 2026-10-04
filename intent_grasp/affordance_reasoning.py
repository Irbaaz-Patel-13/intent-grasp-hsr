"""
In-Context Affordance Reasoning Module
=======================================
Implements the three-step VLM-based affordance reasoning pipeline from AffordGrasp:
  Step 1: Task Analysis - Extract task goal from implicit user instructions
  Step 2: Object Identification - Identify the most task-relevant object in the scene
  Step 3: Part & Affordance Reasoning - Determine optimal graspable part based on affordances

Uses GPT-4o as the backbone VLM, matching the paper's implementation.

Reference: AffordGrasp, Section III-A: In-Context Affordance Reasoning
"""

import os
import json
import base64
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

import numpy as np

try:
    from openai import OpenAI
except ImportError:
    print("[Warning] openai package not installed. VLM reasoning will use mock mode.")
    OpenAI = None

try:
    from pydantic import BaseModel as PydanticBaseModel
    
    # Pydantic schemas for Structured Outputs (guaranteed JSON via constrained decoding)
    class TaskAnalysisSchema(PydanticBaseModel):
        task_goal: str
        functional_requirements: list[str]
        required_object_type: str
        required_properties: list[str]
    
    class ObjectIdentificationSchema(PydanticBaseModel):
        target_object: str
        object_description: str
        confidence: float
        approximate_location: str
    
    class ConstraintsSchema(PydanticBaseModel):
        keep_clear: list[str]
        keep_clear_reasons: list[str]
        post_grasp_motion: str
        stability_priority: str
        thermal_or_hygiene: Optional[str]

    class AffordanceReasoningSchema(PydanticBaseModel):
        target_object: str
        target_part: str
        constraints: ConstraintsSchema
        rationale: str
        confidence: float

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("[Warning] pydantic not installed. Structured Outputs disabled; using JSON parsing.")

from intent_grasp.config import VLMConfig


@dataclass
class TaskAnalysisResult:
    """Output of Step 1: Task Analysis."""
    task_goal: str
    functional_requirements: list
    required_object_type: str
    required_properties: list
    raw_response: dict


@dataclass
class ObjectIdentificationResult:
    """Output of Step 2: Relevant Object Identification."""
    target_object: str
    object_description: str
    confidence: float
    approximate_location: str
    raw_response: dict


@dataclass
class AffordanceReasoningResult:
    """Output of Step 3: Part & Affordance Reasoning."""
    target_object: str
    target_part: str
    constraints: dict
    rationale: str
    confidence: float
    raw_response: dict


@dataclass
class FullReasoningResult:
    """Combined output from all three reasoning steps."""
    task_analysis: TaskAnalysisResult
    object_identification: ObjectIdentificationResult
    affordance_reasoning: AffordanceReasoningResult
    user_instruction: str


class AffordanceReasoner:
    """
    Three-step in-context affordance reasoning using GPT-4o.
    
    This is the core intelligence module of AffordGrasp. Given a user's
    natural language instruction and an RGB image of the scene, it:
    1. Extracts the implicit task goal
    2. Identifies which object in the cluttered scene is most relevant
    3. Reasons about object parts and affordances to select the optimal grasp region
    
    Usage:
        config = VLMConfig(api_key="sk-...")
        reasoner = AffordanceReasoner(config)
        result = reasoner.reason(
            instruction="I want to drink some coffee",
            scene_image=rgb_array
        )
        print(result.affordance_reasoning.target_part)  # "handle"
    """
    
    def __init__(self, config: VLMConfig):
        self.config = config
        self.client = None
        self.mock_mode = False
        
        if OpenAI is not None and config.api_key:
            self.client = OpenAI(api_key=config.api_key)
        else:
            print("WARNING: No OPENAI_API_KEY found. Running in mock mode --"
                  " VLM will hallucinate objects.")
            print("  Set your API key with:  export OPENAI_API_KEY=sk-...")
            print("  (or set OPENAI_API_KEY in your environment before running)")
            self.mock_mode = True
    
    def reason(
        self,
        instruction: str,
        scene_image: np.ndarray,
        verbose: bool = True,
        target_hint: Optional[str] = None
    ) -> FullReasoningResult:
        """
        Execute the full three-step affordance reasoning pipeline.
        
        Args:
            instruction: User's natural language instruction (e.g., "I want to scoop something")
            scene_image: RGB image of the scene as numpy array (H, W, 3)
            verbose: Print reasoning steps
        
        Returns:
            FullReasoningResult containing all three steps' outputs
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"[AffordanceReasoner] Starting reasoning pipeline")
            print(f"  Instruction: \"{instruction}\"")
            print(f"{'='*60}")
        
        # Step 1: Task Analysis
        if verbose:
            print("\n--- Step 1: Task Analysis ---")
        task_result = self._step1_task_analysis(instruction)
        if verbose:
            print(f"  Task Goal: {task_result.task_goal}")
            print(f"  Required Object: {task_result.required_object_type}")
            print(f"  Requirements: {task_result.functional_requirements}")
        
        # Step 2: Object Identification (uses image)
        if verbose:
            print("\n--- Step 2: Object Identification ---")
        obj_result = self._step2_object_identification(
            scene_image, task_result, target_hint=target_hint
        )
        if verbose:
            print(f"  Target Object: {obj_result.target_object}")
            print(f"  Confidence: {obj_result.confidence:.2f}")
            print(f"  Description: {obj_result.object_description}")
        
        # Step 3: Part & Affordance Reasoning
        if verbose:
            print("\n--- Step 3: Part & Affordance Reasoning ---")
        affordance_result = self._step3_affordance_reasoning(
            instruction, task_result, obj_result
        )
        if verbose:
            print(f"  Target Part: {affordance_result.target_part}")
            print(f"  Constraints: {affordance_result.constraints}")
            print(f"  Rationale: {affordance_result.rationale}")
            print(f"  Confidence: {affordance_result.confidence:.2f}")
        if verbose and affordance_result.target_object:
            step2_obj = obj_result.target_object.lower().strip()
            step3_obj = affordance_result.target_object.lower().strip()
            if step2_obj and step3_obj and not (step2_obj in step3_obj or step3_obj in step2_obj):
                print(f"  NOTE: step3's target_object echo ('{step3_obj}') doesn't match "
                      f"step2's target_object ('{step2_obj}') -- using step2's as authoritative.")

        return FullReasoningResult(
            task_analysis=task_result,
            object_identification=obj_result,
            affordance_reasoning=affordance_result,
            user_instruction=instruction
        )
    
    # =========================================================================
    #  STEP 1: Task Analysis
    # =========================================================================
    
    def _step1_task_analysis(self, instruction: str) -> TaskAnalysisResult:
        """
        Extract the implicit task goal from the user's instruction.
        
        Example:
            "I want to scoop something" -> task_goal: "Use a concave tool to gather material"
        """
        if self.mock_mode:
            return self._mock_task_analysis(instruction)
        
        prompt = self.config.step1_task_analysis_template.format(
            instruction=instruction
        )
        
        schema = TaskAnalysisSchema if PYDANTIC_AVAILABLE else None
        response = self._call_vlm(prompt, image=None, response_schema=schema)
        data = self._parse_json_response(response)
        
        return TaskAnalysisResult(
            task_goal=data.get("task_goal", ""),
            functional_requirements=data.get("functional_requirements", []),
            required_object_type=data.get("required_object_type", ""),
            required_properties=data.get("required_properties", []),
            raw_response=data
        )
    
    # =========================================================================
    #  STEP 2: Relevant Object Identification
    # =========================================================================
    
    def _step2_object_identification(
        self,
        scene_image: np.ndarray,
        task_result: TaskAnalysisResult,
        target_hint: Optional[str] = None
    ) -> ObjectIdentificationResult:
        """
        Identify the most suitable object in the scene for the given task.
        Uses the scene image + task analysis to ground the object visually.

        When n_consensus_samples > 1, queries the VLM multiple times and
        takes the majority-vote object to reduce hallucination risk.
        """
        if self.mock_mode:
            return self._mock_object_identification(task_result, target_hint=target_hint)
        
        prompt = self.config.step2_object_identification_template.format(
            task_goal=task_result.task_goal,
            functional_requirements=", ".join(task_result.functional_requirements),
            required_object_type=task_result.required_object_type
        )
        
        schema = ObjectIdentificationSchema if PYDANTIC_AVAILABLE else None
        n_samples = self.config.n_consensus_samples
        
        if n_samples <= 1:
            # Single query
            response = self._call_vlm(prompt, image=scene_image,
                                      response_schema=schema)
            data = self._parse_json_response(response)
        else:
            # Consensus querying: query n times, take majority vote on object
            all_results = []
            for i in range(n_samples):
                response = self._call_vlm(prompt, image=scene_image,
                                          response_schema=schema)
                data_i = self._parse_json_response(response)
                if data_i.get("target_object"):
                    all_results.append(data_i)
            
            if not all_results:
                print("[AffordanceReasoner] All consensus queries failed.")
                data = {}
            else:
                # Majority vote on target_object
                objects = [r["target_object"].lower().strip() for r in all_results]
                vote = Counter(objects).most_common(1)[0]
                if vote[1] < 2 and n_samples >= 3:
                    print(f"[AffordanceReasoner] Warning: No consensus "
                          f"(objects: {objects}). Using first response.")
                # Pick the first result that matches the majority object
                majority_obj = vote[0]
                data = next(
                    (r for r in all_results
                     if r["target_object"].lower().strip() == majority_obj),
                    all_results[0]
                )
        
        return ObjectIdentificationResult(
            target_object=data.get("target_object", ""),
            object_description=data.get("object_description", ""),
            confidence=float(data.get("confidence", 0.0)),
            approximate_location=data.get("approximate_location", ""),
            raw_response=data
        )
    
    # =========================================================================
    #  STEP 3: Part & Affordance Reasoning
    # =========================================================================
    
    def _step3_affordance_reasoning(
        self,
        instruction: str,
        task_result: TaskAnalysisResult,
        obj_result: ObjectIdentificationResult
    ) -> AffordanceReasoningResult:
        """
        Reasons about the task's implied constraints (what must stay clear,
        what happens after the grasp, stability, thermal/hygiene hazards)
        and names the single best part to grasp given those constraints.
        The raw instruction is passed in directly (not just task_result's
        distilled task_goal/functional_requirements) because a concrete cue
        like "just came out of the microwave" can otherwise be lost in
        step 1's summarization before it ever reaches this step.

        keep_clear is meant to be empty for most tasks (see the prompt
        template) -- only a surface whose obstruction would physically
        prevent the task belongs there, each with a one-line mechanical
        justification in the parallel keep_clear_reasons list. temperature
        is 0 (config.py's VLMConfig) for deterministic per-instruction
        output; there is no response caching anywhere in this class, so
        each call to reason() re-queries the model fresh.

        Example:
            Object: mug, Task: "pour the water into the bowl"
            -> target_part: "body" (or "handle"), constraints.keep_clear
               includes "rim"/"opening" with a matching keep_clear_reasons
               entry (the functional surface), so the rim can never be the
               selected grasp part.
        """
        if self.mock_mode:
            return self._mock_affordance_reasoning(instruction, task_result, obj_result)

        prompt = self.config.step3_affordance_reasoning_template.format(
            instruction=instruction,
            target_object=obj_result.target_object,
            task_goal=task_result.task_goal,
            functional_requirements=", ".join(task_result.functional_requirements)
        )

        schema = AffordanceReasoningSchema if PYDANTIC_AVAILABLE else None
        response = self._call_vlm(prompt, image=None, response_schema=schema)
        data = self._parse_json_response(response)

        # --- semantic contract validation (single retry) ---
        # Pydantic guarantees JSON *shape*, not internal coherence: the
        # 15 Jul grid produced target_part='handle' with keep_clear=['handle']
        # (pan/handover). Catch part-in-keep_clear and list-length mismatch,
        # re-query ONCE with the violation named, log both attempts.
        def _violation(d):
            c = d.get("constraints", {}) or {}
            part = (d.get("target_part") or "").lower()
            kc = [str(s).lower() for s in c.get("keep_clear", [])]
            if part and any(part in s or s in part for s in kc):
                return f"target_part '{part}' appears in keep_clear {kc}"
            if len(c.get("keep_clear", [])) != len(c.get("keep_clear_reasons", [])):
                return "keep_clear and keep_clear_reasons lengths differ"
            return None

        v = _violation(data)
        if v:
            print(f"[AffordanceReasoner] CONTRACT VIOLATION: {v} -- re-querying once")
            retry_prompt = (
                prompt
                + "\n\nYour previous answer was invalid: "
                + v
                + ". The grasped part cannot be a surface that "
                  "must stay clear. Resolve the contradiction and "
                  "answer again in the same JSON format."
            )
            response = self._call_vlm(
                retry_prompt,
                image=None,
                response_schema=schema
            )
            data2 = self._parse_json_response(response)
            v2 = _violation(data2)
            print(
                f"[AffordanceReasoner] retry "
                f"{'still invalid: ' + v2 if v2 else 'resolved'}"
            )
            if not v2:
                data = data2
        # --- end validation ---

        constraints = data.get("constraints", {}) or {}
        return AffordanceReasoningResult(
            target_object=data.get("target_object", ""),
            target_part=data.get("target_part", ""),
            constraints={
                "keep_clear": constraints.get("keep_clear", []),
                "keep_clear_reasons": constraints.get("keep_clear_reasons", []),
                "post_grasp_motion": constraints.get("post_grasp_motion", "none"),
                "stability_priority": constraints.get("stability_priority", "low"),
                "thermal_or_hygiene": constraints.get("thermal_or_hygiene"),
            },
            rationale=data.get("rationale", ""),
            confidence=float(data.get("confidence", 0.0)),
            raw_response=data
        )
    # =========================================================================
    #  VLM API CALLS
    # =========================================================================
    
    def _call_vlm(
        self, prompt: str, image: Optional[np.ndarray] = None,
        response_schema=None
    ) -> str:
        """
        Make a call to GPT-4o with optional image input.
        
        If response_schema is a Pydantic model and config.use_structured_outputs
        is True, uses the Structured Outputs API for guaranteed JSON compliance.
        Otherwise falls back to standard completion with manual JSON parsing.
        """
        messages = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        
        if image is not None:
            image_b64 = self._encode_image(image)
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}",
                            "detail": self.config.image_detail
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        # Use Structured Outputs when available — guarantees valid JSON
        if (response_schema is not None
                and self.config.use_structured_outputs
                and PYDANTIC_AVAILABLE):
            try:
                response = self.client.beta.chat.completions.parse(
                    model=self.config.model_name,
                    messages=messages,
                    response_format=response_schema,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                parsed = response.choices[0].message.parsed
                return json.dumps(parsed.model_dump())
            except Exception as e:
                print(f"[AffordanceReasoner] Structured Output failed: {e}")
                print("  Falling back to standard completion.")
        
        # Standard completion with manual JSON parsing
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content
    
    def _encode_image(self, image: np.ndarray) -> str:
        """Encode a numpy RGB image to base64 PNG string."""
        from PIL import Image
        import io
        
        pil_image = Image.fromarray(image.astype(np.uint8))
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from VLM response, handling markdown code blocks."""
        # Strip markdown code fences if present
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            print(f"[Warning] Failed to parse VLM JSON response: {e}")
            print(f"  Raw response: {response[:200]}...")
            return {}
    
    # =========================================================================
    #  MOCK RESPONSES (for testing without API key)
    # =========================================================================
    
    def _mock_task_analysis(self, instruction: str) -> TaskAnalysisResult:
        """Generate plausible mock task analysis based on instruction keywords."""
        instruction_lower = instruction.lower()
        
        # Mapping of common instructions to task analyses
        mock_db = {
            "drink": {
                "task_goal": "Drink a beverage",
                "functional_requirements": ["container for liquid", "handle for secure grip"],
                "required_object_type": "drinking vessel (cup/mug/glass)",
                "required_properties": ["has handle", "can hold liquid"]
            },
            "scoop": {
                "task_goal": "Scoop and transfer material",
                "functional_requirements": ["concave surface", "long handle for reach"],
                "required_object_type": "spoon or ladle",
                "required_properties": ["has bowl end", "has graspable handle"]
            },
            "hammer": {
                "task_goal": "Drive nails into a surface",
                "functional_requirements": ["heavy striking head", "graspable handle"],
                "required_object_type": "hammer",
                "required_properties": ["weighted head", "long handle"]
            },
            "cut": {
                "task_goal": "Cut or slice objects",
                "functional_requirements": ["sharp blade", "safe handle"],
                "required_object_type": "knife or scissors",
                "required_properties": ["has cutting edge", "has handle away from blade"]
            },
            "tighten": {
                "task_goal": "Tighten screws",
                "functional_requirements": ["flat or cross-head tip", "torque-friendly handle"],
                "required_object_type": "screwdriver",
                "required_properties": ["has tip for screw head", "has cylindrical handle"]
            },
            "cook": {
                "task_goal": "Cook food using cookware",
                "functional_requirements": ["heat-resistant surface", "handle for control"],
                "required_object_type": "pan or pot",
                "required_properties": ["flat cooking surface", "heat-safe handle"]
            },
            "flip": {
                "task_goal": "Flip food while cooking",
                "functional_requirements": ["flat thin blade", "long handle"],
                "required_object_type": "spatula",
                "required_properties": ["thin flat end", "graspable handle"]
            },
        }
        
        # Find best match
        best_match = None
        for key, analysis in mock_db.items():
            if key in instruction_lower:
                best_match = analysis
                break
        
        if best_match is None:
            best_match = {
                "task_goal": f"Complete the task described: {instruction}",
                "functional_requirements": ["appropriate tool for the task"],
                "required_object_type": "task-appropriate object",
                "required_properties": ["functional for the described task"]
            }
        
        return TaskAnalysisResult(
            task_goal=best_match["task_goal"],
            functional_requirements=best_match["functional_requirements"],
            required_object_type=best_match["required_object_type"],
            required_properties=best_match["required_properties"],
            raw_response=best_match
        )
    
    def _mock_object_identification(
        self,
        task_result: TaskAnalysisResult,
        target_hint: Optional[str] = None
    ) -> ObjectIdentificationResult:
        """Generate mock object identification.

        If target_hint is provided (the --target flag from the pipeline), use it
        directly so the mock doesn't hallucinate a wrong object name.
        """
        if target_hint:
            target_object = target_hint
            description = (f"Mock: using --target hint '{target_hint}' "
                           f"for {task_result.task_goal.lower()}")
        else:
            obj_type = task_result.required_object_type
            target_object = obj_type.split("(")[0].strip().split("/")[0].strip()
            description = f"A {obj_type} suitable for {task_result.task_goal.lower()}"

        return ObjectIdentificationResult(
            target_object=target_object,
            object_description=description,
            confidence=0.85,
            approximate_location="center-left of scene",
            raw_response={"mock": True, "target_hint": target_hint}
        )
    
    def _mock_affordance_reasoning(
        self,
        instruction: str,
        task_result: TaskAnalysisResult,
        obj_result: ObjectIdentificationResult
    ) -> AffordanceReasoningResult:
        """Mock mode has no model to reason with -- this is a simple,
        deliberately transparent task-word heuristic so offline testing
        doesn't silently reproduce the old always-the-same-answer mock bug
        this rewrite fixes. NOT used when a real OPENAI_API_KEY is set."""
        instr = instruction.lower()
        target = obj_result.target_object.lower()
        keep_clear = []
        keep_clear_reasons = []
        thermal = None
        motion = "translate"
        if "pour" in instr:
            part = "body"
            keep_clear = ["rim/opening"]
            keep_clear_reasons = ["covering this would block the liquid's exit path"]
            motion = "tilt_pour"
        elif "microwave" in instr or "hot" in instr or "oven" in instr:
            part = "handle"
            thermal = "object is hot from the microwave -- avoid direct body contact"
        elif "handle" in instr:
            part = "handle"
        else:
            part = "body"
        return AffordanceReasoningResult(
            target_object=target,
            target_part=part,
            constraints={
                "keep_clear": keep_clear,
                "keep_clear_reasons": keep_clear_reasons,
                "post_grasp_motion": motion,
                "stability_priority": "med",
                "thermal_or_hygiene": thermal,
            },
            rationale=f"[mock] task-word heuristic for '{instruction}'",
            confidence=0.5,
            raw_response={"mock": True}
        )