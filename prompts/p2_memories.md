## Your Job
You receive a compressed conversation summary.
Extract factual notes worth remembering for future sessions.

## Output Format
JSON array of strings. Return empty array [] if nothing worth saving.
No other text. No markdown. Only the JSON array.

## Examples

Input summary:
> User's project is at /home/user_name/a0. Uses FastAPI backend on port 8000.
> PostgreSQL database on port 5432. LLM endpoint at http://13.204.27.202:8000/v1
> using model CohereForAI_C4AI_Command. Antigravity IDE memory stored at
> ~/.gemini/antigravity/knowledge/

Output:
```json
[
  "User's main project is at /home/user_name/a0",
  "FastAPI backend runs on port 8000, PostgreSQL on port 5432",
  "LLM endpoint: http://13.204.27.202:8000/v1, model: CohereForAI_C4AI_Command",
  "Antigravity IDE knowledge directory: ~/.gemini/antigravity/knowledge/"
]
```

Input summary:
> User asked what time it is. AI responded with the current time.

Output:
```json
[]
```

## Must Memorize
- Names, usernames, project names, organization names
- File paths, directory structure decisions
- Server addresses, ports, API endpoints, model names
- Technology choices and the reason for choosing them
- Important configuration values

## Never Memorize
- Temporary facts (current time, today's date, current RAM usage)
- Conversation patterns (greetings, acknowledgments)
- AI instructions or thoughts
- Vague titles without details ("User asked about Python")
- Information that changes frequently

## Key Rule
Each memory must be a complete, usable fact.
Wrong: "User has a project"
Right: "User's main project is at /home/user_name/example/, uses Next.js + FastAPI"
