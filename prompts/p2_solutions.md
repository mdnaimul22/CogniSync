## Your Job
You receive a compressed conversation summary.
Extract successful technical solutions that were applied and confirmed working.

## Output Format
JSON array of objects. Return empty array [] if no solutions found.
No other text. No markdown. Only the JSON array.

Each object must have:
- "slug": lowercase-hyphenated-identifier (max 5 words)
- "problem": clear description of the problem
- "solution": step-by-step instructions to reproduce the solution
- "tags": array of relevant technology keywords

## Example

Input summary:
> User had zram swap not persisting after reboot. Fixed by creating systemd service
> at /etc/systemd/system/zram-setup.service with ExecStart=/usr/local/bin/setup-zram.sh.
> Enabled with systemctl enable zram-setup. Script sets zram0 size to 8G, algorithm lz4.

Output:
```json
[
  {
    "slug": "zram-swap-persist-reboot",
    "problem": "zram swap configuration does not persist after system reboot",
    "solution": "1. Create script /usr/local/bin/setup-zram.sh with zram setup commands (size=8G, algo=lz4)\\n2. Create systemd service /etc/systemd/system/zram-setup.service with ExecStart pointing to the script\\n3. Run: systemctl enable zram-setup && systemctl start zram-setup",
    "tags": ["zram", "systemd", "swap", "linux"]
  }
]
```

## Only Include Solutions That Are
- Successfully executed and confirmed working in the conversation
- Reproducible (contain enough detail to repeat)
- Non-trivial (require more than 1 obvious step)

## Never Include
- Solutions that were attempted but failed
- Speculative solutions not confirmed in the conversation
- Simple operations: "create a file", "install a package" (unless there were complications)
- Conversation patterns, greetings, general Q&A
- Solutions without a clear problem statement

## Slug Rules
- lowercase-hyphenated only: "fix-postgres-timeout", "deploy-fastapi-docker"
- Describes the problem being solved, not the solution
- Max 5 words
