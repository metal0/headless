import json

import trio
from loguru import logger

from headless import events


async def load_server_config(server: str, path: str):
    async with await trio.open_file(path) as f:
        data = ""
        for line in [l async for l in f]:
            data += line
        servers_config = json.loads(data)
        return servers_config[server]


class EmittingValue:
    def __init__(self, event, default, emitter):
        self.event = event
        self.value = default
        self.__emitter = emitter

    def get(self):
        return self.value

    def set(self, value):
        previous_value = self.value
        self.value = value
        self.__emitter.emit(self.event, old=previous_value, new=self.value)


def _internal_name(name: str):
    return name.replace(".", "_")


# TODO: Config with modular hierarchy
class Config:
    def __init__(self, emitter, **named_args):
        self.__emitter = emitter
        self.__config_names = named_args.keys()

        for name, arg in named_args.items():
            self.__make_property(_internal_name(name), default=arg)

    def __getattr__(self, item):
        return super().__getattribute__(_internal_name(item))

    def __str__(self):
        result = {}
        for name in self.__config_names:
            result[_internal_name(name)] = str(
                self.__getattribute__(_internal_name(name))
            )
        return json.dumps(result)

    def __make_property(self, name: str, default):
        try:
            config_events = events.config
            event = getattr(config_events, f"{name}_changed")
            emitting_value = EmittingValue(
                event=event, default=default, emitter=self.__emitter
            )

            def setter(self, value):
                emitting_value.set(value)

            def getter(self):
                return emitting_value.get()

            setattr(Config, _internal_name(name), property(fget=getter, fset=setter))

        except AttributeError as e:
            logger.error(
                f"Attribute Error (probably as a result of eval in Config.make_property): {e}"
            )
            pass

    async def load(self, path: str):
        file_data = ""
        async with await trio.open_file(path, "r") as f:
            async for line in f:
                file_data += line + "\r\n"

        print(file_data)
        config = json.loads(file_data)
        logger.debug(f"load {path=}: {config=}")
        for name in self.__config_names:
            self.__setattr__(
                _internal_name(name), json.loads(config[_internal_name(name)])
            )

    async def save(self, path: str):
        logger.debug(f"save {path=}")
        async with await trio.open_file(path, "w") as f:
            result = {}
            for name in self.__config_names:
                result[_internal_name(name)] = json.dumps(
                    self.__getattribute__(_internal_name(name))
                )
            await f.write(json.dumps(result))
