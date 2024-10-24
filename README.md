[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# headless
A headless World of Warcraft 3.5.5 1235a client library written in Python.

# Example
```python
async def basic_example(user: str, password: str):
    account = "MyAccount"
    character_name = "Demora"
    realm_name = "RealmOfHorse"

    auth_server = ("127.0.0.1", 3724)
    async with headless.open_client(auth_server) as client:
        # Login to auth server
        with trio.fail_after(5):
            await client.login(username, password, os="OSX")

        # Find desired realm
        for realm in await client.realms():
            if realm.name == realm_name:
                break

        # Connect to the world server
        with trio.fail_after(5):
            await client.select_realm(realm)

        # Find desired character
        for character in await client.characters():
            if character.name == account["character"]:
                break

        while True:
            # Enter world with character
            async with client.enter_world(character):
                me = client.world.local_player
                # await me.chat.say('Welcome to garfields house of horror')
                # await me.chat.guild('I am garfield of 4')
                await trio.sleep_forever()

            await trio.sleep(2)
```
