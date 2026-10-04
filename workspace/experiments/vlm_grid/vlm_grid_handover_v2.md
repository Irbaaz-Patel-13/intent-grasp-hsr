# Handover ablation: contract v1 (task-mechanics only) vs v2 (receiver-aware)

| object | v1 part | v1 keep_clear | v2 part | v2 keep_clear | v2 reasons | thermal | changed |
|---|---|---|---|---|---|---|---|
| mug | handle | [] | body | handle | The handle must be unobstructed for the receiver to grasp it easily. | The mug may be hot if it contains a hot beverage. | YES |
| bottle | neck | [] | body | neck | The neck must be clear for the human to grasp the bottle easily. | - | YES |
| hammer | handle | [] | head | handle | The handle must be unobstructed for the receiver to grasp it. | - | YES |
| knife | handle | [] | blade spine | handle | The handle must be unobstructed for the receiver to grasp and control the knife safely. | - | YES |
| bowl | rim | [] | rim | interior | The interior must remain unobstructed to allow the receiver to use the bowl for holding or serving contents. | - | YES |
| pan | handle | [] | handle | handle | The handle must be unobstructed for the receiver to grasp it safely. | The pan may be hot, so the handle is the safest part to grasp. | YES |

## v2 rationales

- **mug**: For a handover task, the handle should be kept clear so the receiver can easily grasp it. The body of the mug is a stable part to grasp, and it allows the handle to be presented towards the receiver. The mug may be hot, so the robot should be cautious when grasping the body.
- **bottle**: For handing over a bottle, the robot should grasp the body to leave the neck clear for the human to easily take hold of it. This ensures the bottle is presented in a way that is natural for the receiver to grasp. The stability priority is medium as the bottle needs to be securely held but not against significant forces.
- **hammer**: For a handover task, the hammer's handle must be clear for the receiver to grasp it naturally. The robot should grasp the head to ensure the handle is presented towards the receiver. This also controls the potentially hazardous head, ensuring it is not directed towards the person.
- **knife**: For handing over a knife, the robot should grasp the blade spine to ensure the handle is unobstructed and safely presented to the receiver. This allows the receiver to easily and safely grasp the handle to use the knife for cutting or slicing.
- **bowl**: For handing over a bowl, grasping the rim allows the receiver to easily take hold of the bowl by its sides or base. The interior must remain clear to ensure it can hold contents immediately upon receipt.
- **pan**: For handing over a pan, the handle is the safest and most natural part for the receiver to grasp. The robot should hold the pan by the body, leaving the handle clear for the person. This ensures safe handling, especially if the pan is hot.
