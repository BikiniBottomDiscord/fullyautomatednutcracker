import asyncio
import logging
import datetime
import traceback


logger = logging.getLogger(__name__)
handler = logging.FileHandler('../logs/{}.log'.format(str(datetime.datetime.now()).replace(' ', '_').replace(':', 'h', 1).replace(':', 'm').split('.')[0][:-2]))
formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(name)s::%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class AsyncTimer:
    def __init__(self, timeout, callback, args=None):
        self._timeout = timeout
        self._callback = callback
        self._args = args
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        try:
            if self._args:
                await self._callback(self._args)
            else:
                await self._callback()
        except Exception as ex:
            logger.info(f"UNHANDLED ERROR IN ASYNC TIMER: {str(self._callback)} {str(ex)}")
            logger.info(''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))

    def cancel(self):
        self._task.cancel()
