import trio

from pont.utility.emitter import wait_for_event
from tests.mock.emitter import MemoryEmitter


async def test_base_emitter():
    async with trio.open_nursery() as n:
        emitter = MemoryEmitter(nursery=n)
        assert len(emitter.memory) == 0

        emitter.emit('horse', arg1='testo', arg2=2)
        assert 'horse' in emitter.memory
        assert emitter.memory['horse'][0].kwargs == dict(arg1='testo', arg2=2)


async def test_wait_for_event():
    async with trio.open_nursery() as n:
        emitter = MemoryEmitter(nursery=n)
        assert len(emitter.memory) == 0

        async def emit_soon():
            emitter.emit('test_wait', arg='the', arg1='horse', arg2='leaved')

        n.start_soon(emit_soon)
        kwargs = await wait_for_event(emitter, 'test_wait')
        assert kwargs == dict(arg='the', arg1='horse', arg2='leaved')
