"""Main Entrypoint for PRISM IDS Agent Daemon."""

import asyncio
import signal
import sys
import structlog
from agent.services.lifecycle import AgentLifecycleManager

logger = structlog.get_logger("prism_agent.main")


async def main() -> None:
    """Agent daemon entrypoint."""
    lifecycle = AgentLifecycleManager()
    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        logger.info("Received termination signal")
        shutdown_event.set()

    # Register OS signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Signal handling on Windows selector loop fallback
            pass

    try:
        await lifecycle.initialize_and_start()
        await shutdown_event.wait()
    except Exception as exc:
        logger.critical("Fatal error in agent daemon loop", error=str(exc))
    finally:
        await lifecycle.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
