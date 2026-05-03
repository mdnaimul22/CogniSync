# Strict JSON parsing fails when AI responses include non-JSON content, causing errors in development mode

## Problem
Strict JSON parsing fails when AI responses include non-JSON content, causing errors in development mode

## Solution
1. Identify the JSON parsing failure point in `src/services/pipeline/extract.py` at line 17 in `_parse_json` function\n2. Implement a regex fallback mechanism to extract JSON content when `json.loads()` fails\n3. Ensure robustness by handling both valid JSON and mixed content responses, especially in development mode (`APP_ENV=development`)
