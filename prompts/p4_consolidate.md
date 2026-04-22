## Your Job
A new memory candidate conflicts with an existing Knowledge Item (same slug).
Decide what to do.

## Input
You will receive:
- NEW: the new candidate content
- EXISTING_SUMMARY: the current metadata.json summary of the existing KI
- EXISTING_ARTIFACT: the current artifacts/summary.md content (may be truncated)

## Output Format
JSON object only. No other text.

```json
{
  "action": "UPDATE | REPLACE | MERGE | SKIP",
  "reasoning": "one sentence explanation",
  "new_summary": "updated dense summary for metadata.json (if action != SKIP)",
  "new_artifact": "updated full markdown content for artifacts/summary.md (if action != SKIP)"
}
```

## Actions

### UPDATE
New content adds information to existing KI. Both old and new info are valid.
→ Combine them into a more complete KI.

### REPLACE  
New content supersedes existing. Existing info is outdated, wrong, or obsolete.
→ Use new content, discard old.

### MERGE
New and existing are closely related but from different angles.
→ Create a comprehensive unified version.

### SKIP
New content adds nothing new. Existing KI already covers it.
→ Return action=SKIP, leave new_summary and new_artifact empty.

## Decision Guidelines
- If new info directly contradicts existing → REPLACE
- If new info adds details/steps/context → UPDATE  
- If both cover same topic from different angles → MERGE
- If existing already contains the new info → SKIP

## Rules
- new_summary must be ≤ 4 sentences, dense, keyword-rich (this is what RAG injects)
- new_artifact must be valid markdown with ## Problem / ## Solution / ## Example sections
- Never lose important information during REPLACE (add historical note if needed)
- Prefer UPDATE over REPLACE when in doubt
