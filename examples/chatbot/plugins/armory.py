import argparse
from typing import Optional, IO

import trio

import pont
from examples.chatbot.chatbot import Chatbot
from examples.chatbot.plugins.shell import ShellPlugin
from pont.client.log import logger
from examples.chatbot.plugin import Plugin
from pont.client.world.player import LocalPlayer

class PontParser(argparse.ArgumentParser):
	def print_help(self, file: Optional[IO[str]] = ...) -> None:
		logger.debug(f'print_help!')
		pass

	def error(self, message: str) -> None:
		"""Custom override that applies custom formatting to the error message"""
		lines = message.split('\n')
		linum = 0

		formatted_message = ''
		for line in lines:
			if linum == 0:
				formatted_message = line
			else:
				formatted_message += '\n       ' + line
			linum += 1

		raise RuntimeError(formatted_message)

class ArmoryPlugin(Plugin):
	requirements = [ShellPlugin]

	async def _send_guild(self, text):
		for line in text.split('\n'):
			await self.bot.client.world.local_player.chat.guild(line)

	def __init__(self):
		self.bot: Optional[Chatbot] = None
		self._shell: Optional[ShellPlugin] = None

		self.parser = PontParser()
		self.parser.add_argument('-r', '--realm', type=str, default='Icecrown')
		self.parser.add_argument('name', type=str)

	async def _armory_command(self, message, *args):
		print(f'{message=}')
		me = self.bot.client.world.local_player

		try:
			print(f'{args=}')
			options = self.parser.parse_args(args)

			print(f'{options=}')
			await me.chat.guild(f'{options}')

		except (Exception, SystemExit) as e:
			await me.chat.guild(f'error: {e}')
			logger.error(f'Error parsing command: {e}')

	def load(self, bot):
		self.bot = bot
		self.check_requirements(bot)
		self._shell = bot.plugin(ShellPlugin)
		self._shell.add_command('armory', self._armory_command, help='')

	def unload(self):
		self._shell.remove_command('armory')
		self._shell = None

