# Identification stability over 5 passes

`temperature=0` does not make the backend bit-deterministic. Each cell was
run 5 times; the columns below show how often the correct object was
identified and how much step 1's inferred requirement varied.

| scene | instruction | correct | picked (distinct) | required type (distinct) | part (distinct) |
|---|---|---|---|---|---|
| TV_remote | I want to change the TV channel | **5/5** | remote control×5 | Remote control×5 | sides×5 |
| coke_can | I'm thirsty and I'd like something fizzy to  | **5/5** | soda can×5 | Container for fizzy drink×3, Beverage container×1, Container with fizzy drink×1 | side×5 |
| dishwash_bottle | I need to wash up these dirty dishes | **5/5** | dish soap bottle×5 | Cleaning tool×5 | body×5 |
| metal_spoon | I want to stir sugar into my tea | **5/5** | spoon×5 | Spoon×5 | handle×5 |
| pot_with_handle_and_lid | I want to boil some water for pasta | **5/5** | pot×5 | Pot or Kettle×5 | handle×5 |
| cluster_mug_cokecan | I'd like a hot drink | **5/5** | red mug×5 | Cup or Mug×4, Container×1 | handle×5 |
| cluster_mug_cokecan | I'm thirsty and I'd like something fizzy to  | **5/5** | soda can×4, can×1 | Beverage container×4, Container for fizzy drink×1 | side×5 |
| cluster_mug_cokecan_pot | I'd like a hot drink | **2/5** | pot with lid×3, red mug×2 | Container×2, Cup or Mug×2, Drink preparation appliance or tool×1 | handle×5 |
| cluster_mug_cokecan_pot | I'm thirsty and I'd like something fizzy to  | **5/5** | soda can×5 | Beverage container×2, Container for fizzy drink×2, Container×1 | side×5 |
| cluster_mug_cokecan_pot | I want to boil some water for pasta | **5/5** | pot×5 | Pot or Kettle×4, Pot or kettle×1 | handle×5 |
| cluster_mug_remote_pot | I'd like a hot drink | **4/5** | red mug×4, pot×1 | Container×3, Cup or mug×1, Cup or Mug×1 | handle×5 |
| cluster_mug_remote_pot | I want to change the TV channel | **5/5** | remote control×5 | Remote control×5 | sides×5 |
| cluster_mug_remote_pot | I want to boil some water for pasta | **5/5** | pot×5 | Pot or Kettle×4, Pot or kettle×1 | handle×5 |

**Overall: 61/65 correct (94%) across 13 cells x 5 passes.**

## Cells that were not stable

For each, note whether the wrong pick coincides with a *more generic*
`required_object_type` from step 1 -- that is the propagation path:
an under-specified requirement leaves step 2 without enough constraint
to discriminate, and it selects another object that also satisfies it.

- **cluster_mug_cokecan_pot** — "I'd like a hot drink" (want *mug*)
  - picked: pot with lid×3, red mug×2
  - step-1 requirement: 'Container'×2, 'Cup or Mug'×2, 'Drink preparation appliance or tool'×1
- **cluster_mug_remote_pot** — "I'd like a hot drink" (want *mug*)
  - picked: red mug×4, pot×1
  - step-1 requirement: 'Container'×3, 'Cup or mug'×1, 'Cup or Mug'×1
