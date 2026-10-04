# Object identification from intent alone

The instruction never names the target object: step 1 infers the required
object type, step 2 must find it in the scene. Cluster rows reuse the SAME
image under different intents — that is the discrimination test.

| scene | objects present | instruction | inferred type needed | picked | conf | correct | part | keep_clear |
|---|---|---|---|---|---|---|---|---|
| TV_remote | remote | I want to change the TV channel | Remote control | **remote control** | 0.95 | ✓ | sides | front panel |
| coke_can | can | I'm thirsty and I'd like something fizzy to drink | Beverage container | **soda can** | 0.95 | ✓ | side | - |
| dishwash_bottle | bottle | I need to wash up these dirty dishes | Cleaning tool | **dish soap bottle** | 0.95 | ✓ | body | nozzle |
| metal_spoon | spoon | I want to stir sugar into my tea | Spoon | **spoon** | 0.95 | ✓ | handle | - |
| pot_with_handle_and_lid | pot | I want to boil some water for pasta | Pot or kettle | **pot** | 0.95 | ✓ | handle | - |
| cluster_mug_cokecan | mug;can | I'd like a hot drink | Container | **red mug** | 0.95 | ✓ | handle | rim |
| cluster_mug_cokecan | mug;can | I'm thirsty and I'd like something fizzy to drink | Beverage container | **can** | 0.95 | ✓ | side | - |
| cluster_mug_cokecan_pot | mug;can;pot | I'd like a hot drink | Container | **pot with lid** | 0.90 | ✗ (want mug) | handle | - |
| cluster_mug_cokecan_pot | mug;can;pot | I'm thirsty and I'd like something fizzy to drink | Beverage container | **soda can** | 0.95 | ✓ | side | - |
| cluster_mug_cokecan_pot | mug;can;pot | I want to boil some water for pasta | Pot or Kettle | **pot** | 0.95 | ✓ | handle | - |
| cluster_mug_remote_pot | mug;remote;pot | I'd like a hot drink | Cup or Mug | **red mug** | 0.95 | ✓ | handle | - |
| cluster_mug_remote_pot | mug;remote;pot | I want to change the TV channel | Remote control | **remote control** | 0.95 | ✓ | sides | - |
| cluster_mug_remote_pot | mug;remote;pot | I want to boil some water for pasta | Pot or Kettle | **pot** | 0.95 | ✓ | handle | - |

**Intent-only identification: 12/13 correct.**

## Discrimination within a single image

- **cluster_mug_cokecan** (2 intents): picked 'red mug', 'can' — all distinct
- **cluster_mug_cokecan_pot** (3 intents): picked 'pot with lid', 'soda can', 'pot' — all distinct
- **cluster_mug_remote_pot** (3 intents): picked 'red mug', 'remote control', 'pot' — all distinct

## Rationales

- **TV_remote / remote**: Grasping the sides of the remote control allows access to the front panel where the buttons and IR sensor are located, which are necessary for changing the TV channel. The task does not require moving the remote, so stability is not a high priority.
- **coke_can / can**: For drinking from a soda can, the side is the most natural part to grasp as it allows easy access to the top for opening and drinking. There are no surfaces that must remain clear to perform the task, as the can is simply being moved to a position for drinking. The stability priority is low because the can is not being tilted or poured, just translated. There are no thermal or hygiene concerns specific to this task.
- **dishwash_bottle / bottle**: For applying dish soap, the bottle needs to be tilted to pour the soap out. Grasping the body allows for easy tilting while keeping the nozzle clear for dispensing. The stability priority is medium as the bottle needs to be controlled during pouring to avoid spills.
- **metal_spoon / spoon**: Grasping the handle allows the spoon to reach the bottom of the cup and move in a circular motion without obstructing any functional part of the spoon. The task involves stirring, which requires translation motion, and the handle is safe for contact with food and hot liquids.
- **pot_with_handle_and_lid / pot**: Grasping the handle allows for safe manipulation of the pot without obstructing any functional surfaces. The handle is designed for this purpose, ensuring stability and avoiding contact with hot surfaces. The task involves translating the pot to the stove, requiring a stable grip to prevent tipping or spilling.
- **cluster_mug_cokecan / mug**: Grasping the handle allows for safe handling and pouring of the hot liquid without obstructing the rim, which is necessary for pouring. The handle provides a stable grip, minimizing the risk of slipping or tipping, and avoids direct contact with the hot surface of the mug.
- **cluster_mug_cokecan / can**: For the task of quenching thirst with a fizzy drink, the can needs to be easily opened and safe to drink from. Grasping the side of the can allows for easy handover to a person who can then open it. There are no surfaces that need to remain clear for the task to be completed, as the opening will be used after the handover. The stability priority is low because the can is not being tilted or poured by the robot, and there are no thermal or hygiene concerns with grasping the side of the can.
- **cluster_mug_cokecan_pot / mug**: Grasping the handle allows for safe handling of the pot, which is necessary due to the hot liquid inside. The handle is designed to be grasped without obstructing any functional part of the pot, such as the lid or spout. The task involves heating and containing the liquid, so stability is a priority to prevent spills. The handle is also thermally insulated, making it safe to touch despite the pot's hot surface.
- **cluster_mug_cokecan_pot / can**: Grasping the side of the soda can allows for easy handover without obstructing the top, which needs to remain clear for opening and drinking. The side provides a stable grip for the handover task, and there are no thermal or hygiene concerns with touching the can's exterior.
- **cluster_mug_cokecan_pot / pot**: Grasping the handle allows for safe manipulation of the pot without obstructing any functional surfaces. The handle is designed to be grasped and provides stability during movement. The pot will be heated, so the body will become hot, making the handle the safest contact point.
- **cluster_mug_remote_pot / mug**: Grasping the handle allows for safe handling and pouring of the hot liquid without obstructing any functional part of the mug. The handle is designed to be grasped without direct contact with the hot surface of the mug, ensuring safe handling. The task involves tilting the mug to pour, so the handle provides a stable grip for this motion.
- **cluster_mug_remote_pot / remote**: Grasping the sides of the remote control allows access to all buttons, which is necessary for changing the TV channel. There are no surfaces that must remain clear to perform this task, as the buttons are accessible from the top. The task does not require any post-grasp motion beyond pressing buttons, and stability is not a major concern since the remote is typically used in a stationary position. There are no thermal or hygiene concerns associated with this task.
- **cluster_mug_remote_pot / pot**: Grasping the handle allows for safe manipulation of the pot without obstructing any functional surfaces. The handle is designed to be grasped and provides stability during movement. The pot will be placed on a stove, so the surface will become hot, making the handle the safest part to grasp.
