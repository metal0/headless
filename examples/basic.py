import json
import random

import loguru
import trio

import pont
from pont import auth, world
from pont.world.chat.message import MessageType
from pont.world.language import Language


def load_login(server: str, filename: str):
	with open(filename, 'r') as f:
		user_info = json.load(f)
		return user_info[server]

async def run(server, proxy=None):
	account = server['account']
	try:
		client: pont.Client
		async with pont.open_client(auth_server=server['realmlist'], proxy=proxy) as client:
			# Login to auth server
			with trio.fail_after(5):
				await client.login(account['username'], account['password'], os='Win')

			# Find desired realm
			for realm in await client.realms():
				if realm.name == server['realm']:
					break

			# Connect to the world server
			with trio.fail_after(5):
				await client.select_realm(realm)

			# Find desired character
			for character in await client.characters():
				if character.name == account['character']:
					break

			# Enter world with character
			async with client.enter_world(character):
				await client.world.chat.send_message('bongour, brother', MessageType.guild, Language.universal)
				await trio.sleep_forever()

				# await trio.sleep(2)
				# await client.logout()

	except (Exception, trio.TooSlowError, auth.AuthError, world.WorldError):
		loguru.logger.exception('Error')

async def main():
	login_filename = 'C:/Users/dinne/Documents/Projects/pont/servers_config.json'
	acore = load_login('dalaran-wow', login_filename)
	# proxy = ('tower', 1664)
	proxy = None

	while True:
		await run(acore, proxy=proxy)
		await trio.sleep(5 + random.random() * 20)

if __name__ == '__main__':
	trio.run(main)
