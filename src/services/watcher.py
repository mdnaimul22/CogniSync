"""File watcher service — monitors brain/<conv-id>/overview.txt in real-time.

Buffers dialogue turns and triggers the pipeline when threshold is met.
Cross-responsibility violations fixed:
  - ConvBuffer moved to src/core/buffer.py
  - Orchestration moved to src/services/orchestrator.py
"""

import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.config import Settings, setup_logger, exists
from src.core import ConvBuffer

logger = setup_logger(Settings.LOG_DIR / "service.log", "daemon.services.watcher")


class OverviewHandler(FileSystemEventHandler):
    """Fires when any file under brain/ is modified."""

    def __init__(
        self,
        buffers: dict[str, ConvBuffer],
        settings: Settings,
    ) -> None:
        self._buffers = buffers
        self._settings = settings

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        path_name = event.src_path.split("/")[-1]
        if path_name != "overview.txt":
            return
        
        parts = event.src_path.split("/")
        if len(parts) >= 4:
            conv_id = parts[-4]
            if conv_id in self._buffers:
                self._buffers[conv_id].ingest_new_lines()

    def on_created(self, event) -> None:
        if event.is_directory:
            return
        path_name = event.src_path.split("/")[-1]
        if path_name != "overview.txt":
            return
        
        parts = event.src_path.split("/")
        if len(parts) >= 4:
            conv_id = parts[-4]
            self._register(event.src_path, conv_id)

    def _register(self, overview_path: str, conv_id: str) -> None:
        if conv_id not in self._buffers:
            self._buffers[conv_id] = ConvBuffer(
                overview_path=overview_path,
                buffer_turns=self._settings.WATCHER_BUFFER_TURNS,
                buffer_timeout=self._settings.WATCHER_BUFFER_TIMEOUT,
            )
            logger.info("  Registered new conversation: %s…", conv_id[:8])


def _flush_ready_buffers(
    buffers: dict[str, ConvBuffer],
    settings: Settings,
) -> None:
    from src.services.orchestrator import process_buffered_dialogue
    for conv_id, buf in list(buffers.items()):
        buf.ingest_new_lines()
        if buf.should_flush():
            dialogue, project = buf.flush()
            if dialogue.strip():
                process_buffered_dialogue(Settings, conv_id, dialogue, project)


def start_watcher(settings: Settings, run_once: bool = False) -> None:
    """Start the real-time file watcher. Called by orchestrator."""
    if not Settings.WATCHER_ENABLED:
        logger.info("Watcher disabled in config.")
        return

    brain_dir = Settings.BRAIN_DIR
    buffers: dict[str, ConvBuffer] = {}

    # Using list_files from src.config instead of .iterdir()
    for conv_dir in list_files(str(brain_dir), "*"):
        if not conv_dir.is_dir() or conv_dir.name == "tempmediaStorage":
            continue
        
        # Construct absolute path to overview.txt
        overview_path = conv_dir / ".system_generated" / "logs" / "overview.txt"
        overview_path_str = str(overview_path)
        
        if exists(overview_path_str):
            buffers[conv_dir.name] = ConvBuffer(
                overview_path=overview_path_str,

                buffer_turns=Settings.WATCHER_BUFFER_TURNS,
                buffer_timeout=Settings.WATCHER_BUFFER_TIMEOUT,
            )


    logger.info("╔══════════════════════════════════════════════╗")
    logger.info("║                 Memory Watcher               ║")
    logger.info("╚══════════════════════════════════════════════╝")
    logger.info("  Brain dir    : %s", brain_dir)
    logger.info("  Watching     : %d existing conversations", len(buffers))
    logger.info("  Buffer turns : %d", Settings.WATCHER_BUFFER_TURNS)
    logger.info("  Timeout      : %ds\n", Settings.WATCHER_BUFFER_TIMEOUT)

    handler = OverviewHandler(buffers, Settings)
    observer = Observer()
    observer.schedule(handler, str(brain_dir), recursive=True)
    observer.start()

    poll = Settings.WATCHER_POLL_SECONDS

    try:
        if run_once:
            time.sleep(2)
            _flush_ready_buffers(buffers, Settings)
            observer.stop()
        else:
            while True:
                time.sleep(poll)
                _flush_ready_buffers(buffers, Settings)
    except KeyboardInterrupt:
        logger.info("Shutting down…")
        observer.stop()

    observer.join()
