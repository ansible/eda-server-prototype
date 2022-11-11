import asyncio
import logging
import time

logger = logging.getLogger("eda_server.batch")


class Batcher:
    def __init__(self, processor_fn, max_batch_size=10000, batch_timeout=1):
        self.queue = asyncio.Queue()
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout
        self.processor_fn = processor_fn

    def start(self, get_db_session_factory):
        self.get_db_session_factory = get_db_session_factory
        _ = asyncio.get_event_loop()
        asyncio.create_task(self._batcher())

    async def _batcher(self):
        while True:
            timeout = time.time() + self.batch_timeout
            while (
                time.time() < timeout
                and self.queue.qsize() <= self.max_batch_size
            ):
                await asyncio.sleep(0.1)
            else:
                if self.queue.qsize() > 0:
                    logger.info("Processing batch %s", self.queue.qsize())
                    await self.processor_fn(
                        self.queue, self.get_db_session_factory()
                    )
            await asyncio.sleep(0.1)
