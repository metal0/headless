import json
import random
import traceback
import trio
import sys
sys.path.append('C:/Users/Owner/PycharmProjects/pont.client/src')

import pont
from pont.client import auth, world

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
				await client.login(account['username'], account['password'])

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
			# TODO: aenter should start a scope/nursery in which all following in-game tasks run
			#   aexit does the obvious scope.aexit
			# async with client.enter_world(character):
			await client.enter_world(character)
			await trio.sleep_forever()

	except (OSError, trio.TooSlowError, auth.AuthError, world.WorldError):
		traceback.print_exc()

async def main():
	login_filename = 'C:/Users/Owner/Documents/WoW/servers_config.json'
	acore = load_login('acore', login_filename)
	proxy = ('tower', 1665)
	# proxy = None

	while True:
		await run(acore, proxy=proxy)
		await trio.sleep(5 + random.random() * 20)

if __name__ == '__main__':
	trio.run(main)
