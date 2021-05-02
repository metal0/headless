import json
import os
import random

import trio
import headless
from headless import auth, world
from wlink.log import logger

def load_login(server: str, filename: str):
	with open(filename, 'r') as f:
		user_info = json.load(f)
		return user_info[server]

async def basic_example(server, proxy=None):
	account = server['account']
	try:
		client: headless.Client
		async with headless.open_client(auth_server=server['realmlist'], proxy=proxy) as client:
			# Login to auth server
			with trio.fail_after(5):
				await client.login(account['username'], account['password'], os='OSX')

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

			while True:
				# Enter world with character
				async with client.enter_world(character):
					me = client.world.local_player
					await me.chat.say('Welcome to garfields house of horror')
					await me.chat.guild('I am garfield of 4')
					await trio.sleep_forever()

				await trio.sleep(2)

	except KeyboardInterrupt:
		logger.info('yes!')

	except (Exception, trio.TooSlowError, auth.AuthError, world.WorldError):
		logger.exception('Error')

async def main():
	login_filename = os.environ.get('PONT_CREDS')
	server = load_login('warmane', login_filename)
	proxy = ('server', 9050)
	# proxy = None

	while True:
		await basic_example(server, proxy=proxy)
		await trio.sleep(5 + random.random() * 20)

if __name__ == '__main__':
	trio.run(main)
