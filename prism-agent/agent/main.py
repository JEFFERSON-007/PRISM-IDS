"""Main Entrypoint for PRISM IDS Agent Daemon with Optimized Multithreaded Executor Policy."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import signal
import sys
import structlog
from agent.services.lifecycle import AgentLifecycleManager

logger = structlog.get_logger("prism_agent.main")


async def main() -> None:
    """Agent daemon entrypoint with tuned thread pool executor for high-throughput parallel execution."""
    # Configure multithread worker pool tuned for CPU cores
    cpu_cores = os.cpu_count() or 4
    max_workers = min(32, cpu_cores * 4)
    executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="PrismWorker")
    
    loop = asyncio.get_running_loop()
    loop.set_default_executor(executor)

    logger.info(
        "Multithreaded execution pool configured",
        cpu_cores=cpu_cores,
        worker_threads=max_workers,
    )

    lifecycle = AgentLifecycleManager()
    shutdown_event = asyncio.Event()

    def signal_handler(sig_num: int = 0, frame: Any = None) -> None:
        logger.info("Received termination signal", signal=sig_num)
        shutdown_event.set()

    # Register OS signal handlers for Windows and POSIX compatibility
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except (NotImplementedError, AttributeError):
            signal.signal(sig, lambda s, f: loop.call_soon_threadsafe(shutdown_event.set))

    try:
        await lifecycle.initialize_and_start()
        await shutdown_event.wait()
    except Exception as exc:
        logger.critical("Fatal error in agent daemon loop", error=str(exc))
    finally:
        await lifecycle.shutdown()
        executor.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
