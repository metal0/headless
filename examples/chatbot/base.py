import json
import random
import loguru
import trio

from examples.chatbot.chatbot import Chatbot
from examples.chatbot.plugins.armory import ArmoryPlugin
from examples.chatbot.plugins.shell import ShellPlugin
from pont import auth, world

def load_login(server: str, filename: str):
	with open(filename, 'r') as f:
		user_info = json.load(f)
		return user_info[server]

async def run(server, proxy=None):
	account = server['account']
	try:
		plugins = [ShellPlugin(), ArmoryPlugin()]
		bot = Chatbot(account['character'], server['realm'], server['realmlist'], plugins)
		await bot.run(account['username'], account['password'], proxy=proxy)

	except (Exception, trio.TooSlowError, auth.AuthError, world.WorldError):
		loguru.logger.exception('Error')

async def main():
	login_filename = 'C:\\Users\\Owner\\Documents\\WoW\\servers_config.json'
	acore = load_login('whitemane', login_filename)
	proxy = ('server', 9050)
	# proxy = None

	while True:
		await run(acore, proxy=proxy)
		await trio.sleep(5 + random.random() * 20)

if __name__ == '__main__':
	trio.run(main)
