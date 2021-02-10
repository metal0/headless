import inspect
import shlex
import uuid
from enum import Enum
from typing import Optional

import trio

from examples.chatbot.plugin import Plugin
from pont.client import events
from pont.client.log import logger
from pont.client.world.chat import ChatMessage, MessageType


class ShellEvents(Enum):
	shell_command = uuid.uuid4()

class PontShell:
	def __init__(self, nursery: trio.Nursery, prefix, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._nursery = nursery
		self._command_map = {}
		self.prefix = prefix

	def default(self, line: str) -> bool:
		pass

	def help(self, *args):
		pass

	def add_command(self, name, handler, help=''):
		self._command_map[name] = {
			'handler': handler,
			'help': help
		}

	def remove_command(self, name):
		self._command_map.pop(name)

	def handle_command(self, message) -> bool:
		text = message.text.strip()
		i = text.find(self.prefix)
		if i == -1:
			return False

		args = shlex.split(text[i:])

		try:
			fn = self._command_map[args[0]]['handler']
			logger.debug(f'{fn=}')

			if inspect.iscoroutinefunction(fn):
				self._nursery.start_soon(fn, message, *args)
			else:
				self._nursery.start_soon(trio.to_thread.run_sync, fn, message, *args)

		except KeyError:
			self.default(args)

class ShellPlugin(Plugin):
	def __init__(self, prefix='$'):
		super().__init__()
		self.prefix = prefix

		self.bot = None
		self._shell: Optional[PontShell] = None
		self._listener = None

	def _test(self, *args, **kwargs):
		print(f'{args=} {kwargs=}')

	def is_command(self, text: str):
		return text[0].lstrip() == self.prefix

	def add_command(self, name, handler, help=''):
		self._shell.add_command(name, handler, help)

	def remove_command(self, name):
		self._shell.remove_command(name)

	def handle_command(self, message):
		self._shell.handle_command(message)

	def _check_message(self, message):
		if message.type == MessageType.guild:
			if self.is_command(message.text):
				self.handle_command(message)

	def load(self, bot):
		self.bot = bot
		self._shell = PontShell(bot.client.nursery, self.prefix)
		self._listener = bot.on(events.world.received_chat_message, self._check_message)

	def unload(self):
		if self._listener is not None:
			self.bot.remove_listener(self._listener)

		self._shell = None
