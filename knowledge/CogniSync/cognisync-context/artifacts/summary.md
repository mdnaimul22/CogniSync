# Cognisync — Context Notes

## Facts
- Project uses Python design patterns: Singleton, Factory, Observer, Strategy, and concurrency techniques: Threading, Multiprocessing, Async/Await
- Python code in `src/` follows Pythonic naming conventions and uses `Pydantic` for type safety
- Type hints are used in functions throughout the `src/` directory
- Debug logs for `daemon.services.pipeline.extract` show regex fallback when JSON parsing fails
- JSON parsing failure occurs in `src/services/pipeline/extract.py` at line 17 in `_parse_json` function due to strict `json.loads()`
- Regex fallback implemented to handle non-JSON content in AI responses, especially in development mode
- Fixed issue in `watcher.py` to search for conversations in the external `BRAIN_DIR` location (`~/.gemini/...`) instead of the internal `brain/` folder
- Watcher now correctly detects and outputs existing conversations: `Watching : 3 existing conversations`
- Decorators (function and class-based) are implemented in the project