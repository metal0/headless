import json
import random
import loguru
import trio
import pont

from pont.client import auth, world
from pont.client.world.chat.message import MessageType
from pont.client.world.language import Language
from pont.client.world.net import Opcode


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

			while True:
				# Enter world with character
				async with client.enter_world(character):
					me = client.world.local_player
					await me.chat.guild('hello!')

					await client.world.protocol.send_CMSG_GUILD_ROSTER()
					roster = await client.world.wait_for_packet(Opcode.SMSG_GUILD_ROSTER)
					print(roster)

					# await me.chat.whisper('Hey!', 'Meow')

					# if me.guild is not None:

					await trio.sleep_forever()
					# await trio.sleep(2)
				await trio.sleep(2)

	except (Exception, trio.TooSlowError, auth.AuthError, world.WorldError):
		loguru.logger.exception('Error')

async def main():
	login_filename = '/home/fure/work/pont/servers_config.json'
	acore = load_login('acore', login_filename)
	proxy = ('server', 1069)
	# proxy = None

	while True:
		await run(acore, proxy=proxy)
		await trio.sleep(5 + random.random() * 20)

if __name__ == '__main__':
	trio.run(main)
