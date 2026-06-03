import sys
import asyncio

# tenacity 5.x uses @asyncio.coroutine which was removed in Python 3.11.
# mega.py hard-requires tenacity<6, so we can't upgrade — shim it instead.
if sys.version_info >= (3, 11) and not hasattr(asyncio, "coroutine"):
    def _legacy_coroutine(func):
        async def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            result = None
            while True:
                try:
                    awaitable = gen.send(result)
                    result = await awaitable if hasattr(awaitable, "__await__") else awaitable
                except StopIteration as e:
                    return e.value
        return wrapper
    asyncio.coroutine = _legacy_coroutine
