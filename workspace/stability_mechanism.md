# Where identification failures come from

Each pass pairs step 1's inferred `required_object_type` with the object
step 2 then selected. A requirement is called *specific* if it names an
object category (mug, pot, remote, ...) and *generic* otherwise.

## Contingency: requirement specificity vs outcome

| step-1 requirement | correct | wrong | accuracy |
|---|---|---|---|
| specific (names a category) | 43 | 1 | 98% |
| generic | 18 | 3 | 86% |

## Per-pass detail for cells that varied

### cluster_mug_cokecan_pot — "I'd like a hot drink"  (expected *mug*)

| pass | step-1 required type | specific? | picked | correct |
|---|---|---|---|---|
| 1 | Container | **no** | pot with lid | ✗ |
| 2 | Container | **no** | pot with lid | ✗ |
| 3 | Cup or Mug | yes | red mug | ✓ |
| 4 | Drink preparation appliance or tool | yes | pot with lid | ✗ |
| 5 | Cup or Mug | yes | red mug | ✓ |

### cluster_mug_remote_pot — "I'd like a hot drink"  (expected *mug*)

| pass | step-1 required type | specific? | picked | correct |
|---|---|---|---|---|
| 1 | Cup or mug | yes | red mug | ✓ |
| 2 | Container | **no** | pot | ✗ |
| 3 | Cup or Mug | yes | red mug | ✓ |
| 4 | Container | **no** | red mug | ✓ |
| 5 | Container | **no** | red mug | ✓ |

## Does a generic requirement always fail?

| scene | generic requirement → correct | → wrong |
|---|---|---|
| cluster_mug_cokecan | 6 | 0 |
| cluster_mug_cokecan_pot | 5 | 2 |
| cluster_mug_remote_pot | 2 | 1 |
| coke_can | 5 | 0 |

A generic requirement is only harmful when the scene contains a
competing object that also satisfies it — which is why the same generic
requirement succeeds in the two-object scene and fails once a pot is added.

## Summary

- 61/65 passes correct (94%)
- 11/13 cells stable across every pass
- failures confined to 2 cell(s)

