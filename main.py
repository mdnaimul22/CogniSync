#!/usr/bin/env python3
"""Memory Daemon — Clean Architecture Entry Point.

Usage:
    python3 main.py watch          # Start real-time daemon
    python3 main.py watch --once   # Process pending and exit
    python3 main.py process <id>   # Force process a specific conversation
    python3 main.py status         # Show system status
"""

import argparse
import sys

# Load env variables and config first
from src.config import Settings, setup_logger
from src.core import load_state
from src.services.orchestrator import process_conversation, start_daemon

# Setup logging
logger = setup_logger(Settings.LOG_DIR / "daemon.log", "daemon.main")


def cmd_watch(args) -> None:
    """Start the file watcher."""
    start_daemon(Settings, run_once=args.once)


def cmd_process(args) -> None:
    """Force process a specific conversation."""
    process_conversation(Settings, args.conv_id)


def cmd_status(args) -> None:
    """Show daemon status."""
    logger.info("CogniSync Status")
    logger.info("================")
    logger.info(f"Brain Dir     : {Settings.BRAIN_DIR}")
    logger.info(f"Knowledge Dir : {Settings.KNOWLEDGE_DIR}")
    logger.info(f"LLM Model     : {Settings.LLM_MODEL}")
    
    state = load_state(Settings.STATE_FILE)
    logger.info(f"Processed Convs: {len(state.processed)}")


    # Use src.config utilities instead of direct Path calls
    kb_path = str(Settings.KNOWLEDGE_DIR)
    from src.config import exists, list_files

    if exists(kb_path):
        projects = [d for d in list_files(kb_path, "*") if d.is_dir()]
        logger.info(f"Tracked Projects: {len(projects)}")
        for p in projects[:5]:
            # list_files returns Path objects, we can use them for metadata check
            kis = len(list_files(str(p), "*/metadata.json"))
            logger.info(f"  - {p.name}: {kis} KIs")
    else:
        logger.info("Knowledge Dir not found.")



def main() -> None:
    parser = argparse.ArgumentParser(description="CogniSync")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # watch
    p_watch = subparsers.add_parser("watch", help="Start real-time file watcher")
    p_watch.add_argument("--once", action="store_true", help="Process pending and exit")

    # process
    p_process = subparsers.add_parser("process", help="Force process a conversation")
    p_process.add_argument("conv_id", help="Conversation ID to process")

    # status
    p_status = subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if args.command == "watch":
        cmd_watch(args)
    elif args.command == "process":
        cmd_process(args)
    elif args.command == "status":
        cmd_status(args)


if __name__ == "__main__":
    main()
