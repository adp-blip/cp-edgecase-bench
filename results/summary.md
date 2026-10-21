# Results

**base** = passes the sample tests from the problem statement. **plus** = also passes edge cases, 40 random tests checked against a reference, and max-size stress tests.

| model | base pass@1 | plus pass@1 | base - plus |
|---|---|---|---|
| `allam-2-7b` | 25% | 0% | 25 pts |
| `openai_gpt-oss-120b` | 100% | 100% | 0 pts |
| `openai_gpt-oss-20b` | 100% | 100% | 0 pts |
| `qwen_qwen3.8-27b` | 100% | 92% | 8 pts |

## Per problem

| problem | `allam-2-7b` | `openai_gpt-oss-120b` | `openai_gpt-oss-20b` | `qwen_qwen3.8-27b` |
|---|---|---|---|---|
| max_subarray | ⚠️ edge (wrong_answer) | ✅ | ✅ | ✅ |
| count_inversions | ❌ base | ✅ | ✅ | ✅ |
| merge_intervals | ❌ base | ✅ | ✅ | ✅ |
| longest_unique_substring | ❌ base | ✅ | ✅ | ✅ |
| valid_brackets | ❌ base | ✅ | ✅ | ✅ |
| min_coins | ❌ base | ✅ | ✅ | ✅ |
| spiral_order | ❌ base | ✅ | ✅ | ✅ |
| count_primes | ❌ base | ✅ | ✅ | ✅ |
| count_pairs_with_sum | ⚠️ edge (wrong_answer) | ✅ | ✅ | ✅ |
| lis_length | ⚠️ edge (runtime_error) | ✅ | ✅ | ✅ |
| to_roman | ❌ base | ✅ | ✅ | ✅ |
| running_median | ❌ base | ✅ | ✅ | ⚠️ random (wrong_answer) |

## Where base-passing solutions broke

- `allam-2-7b`: edge: wrong_answer x2, edge: runtime_error x1
- `openai_gpt-oss-120b`: nothing
- `openai_gpt-oss-20b`: nothing
- `qwen_qwen3.8-27b`: random: wrong_answer x1
