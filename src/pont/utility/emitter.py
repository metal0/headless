import inspect
import trio
import pyee

class BaseEmitter:
	def __init__(self, emitter=None, nursery=None, scope=None):
		if emitter is None:
			if nursery is None:
				raise ValueError('Need at least emitter or nursery')
			emitter = pyee.TrioEventEmitter(nursery=nursery)

		self._emitter = emitter
		self._scope = scope
		self._events = {}

	def _append_event(self, event, fn):
		if event not in self._events:
			self._events[event] = [fn]
		else:
			self._events[event].append(fn)

	def remove_listener(self, event, listener):
		self._emitter.remove_listener(event, listener)

	def remove_all_listeners(self, event=None):
		self._emitter.remove_all_listeners(event)

	def emit(self, event, *args, **kwargs):
		self._emitter.emit(event, *args, **kwargs)

	def once(self, event, fn = None):
		def _on(fn):
			target_fn = fn
			async def fn_async(*args, **kwargs):
				await trio.lowlevel.checkpoint()
				return fn(*args, **kwargs)

			if not inspect.iscoroutinefunction(fn):
				target_fn = fn_async

			return self._emitter.once(event, target_fn)

		if fn is None:
			return _on
		else:
			return _on(fn)

	def on(self, event, fn = None):
		def _on(fn):
			target_fn = fn
			async def fn_async(*args, **kwargs):
				await trio.lowlevel.checkpoint()
				return fn(*args, **kwargs)

			if not inspect.iscoroutinefunction(fn):
				target_fn = fn_async

			self._append_event(event, target_fn)
			return self._emitter.on(event, target_fn)

		if fn is None:
			return _on
		else:
			return _on(fn)

class AsyncScopedEmitter(BaseEmitter):
	async def aclose(self):
		for event, fn_list in self._events.items():
			for fn in fn_list:
				if fn in self._emitter.listeners(event):
					self._emitter.remove_listener(event, fn)

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.aclose()

class ScopedEmitter(BaseEmitter):
	def close(self):
		for event, fn_list in self._events.items():
			for fn in fn_list:
				if fn in self._emitter.listeners(event):
					self._emitter.remove_listener(event, fn)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

# def default_transform():
	

# Wait for the given event under an optional condition to occur (once) and return a transform of the event keyword
# arguments.
async def wait_for_event(emitter, event, condition=None, result_transform=None):
	receive_event = trio.Event()
	result = None
	if condition is None:
		condition = lambda *args, **kwargs: True

	if result_transform is None:
		result_transform = lambda *args, **kwargs: tuple(kwargs.values())

	async def on_event(*args, **kwargs):
		if condition(**kwargs):
			nonlocal result
			result = result_transform(**kwargs)
			receive_event.set()

	listener = emitter.on(event, on_event)
	await receive_event.wait()

	emitter.remove_listener(event, listener)
	return result
