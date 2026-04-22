## Your Job
You receive a raw conversation log between USER and AI (coding assistant).
Compress it into a short, dense, searchable plain-text summary.
This summary will be used to extract memories and solutions in the next step.

## Output Format
Plain text only. No markdown formatting. No introduction. No conclusion.
Maximum 300 words. Minimum 20 words (return "-" if less than 20 words possible).

## Must KEEP
- Technology names, library names, framework names
- File paths, directory paths, config file names
- Port numbers, URLs, API endpoints, IP addresses
- Error messages (compressed, not full stack trace)
- Architecture decisions and the reasoning behind them
- Config values, model names, environment variables
- What was built, what was fixed, what was decided

## Must REMOVE
- Full code blocks
- Full file contents
- Long command outputs
- Search results
- Greetings and small talk
- AI's internal thoughts and reasoning text
- Repetitive content (keep only the final/correct version)
- Tool call results and raw outputs

## Examples

BAD (too much noise):
> User asked me to help with a Python script. I thought about the problem carefully
> and decided to use subprocess. Here is the full code: [200 lines of code]...
> The output was: [50 lines of output]...

GOOD (compressed):
> User building Python script using subprocess to run shell commands.
> Fixed PermissionError by adding sudo prefix. Script saved to /home/user/run.py.

## Rules
- Write in third person ("User is building...", "Fixed by...")
- Do not add your own analysis or suggestions
- Do not invent details not present in the conversation
- If conversation has no meaningful technical content, return: -
