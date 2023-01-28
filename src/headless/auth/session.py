import construct
import trio
import wlink
from trio_socks import socks5
from wlink import cryptography
from wlink.auth import AuthStream
from wlink.auth.packets import (
    Response,
    ChallengeResponse,
    ChallengeRequest,
    ProofResponse,
    ProofRequest,
)
from wlink.auth.packets.b12340.challenge import make_challenge_request
from wlink.auth.packets.b12340.proof import make_proof_request
from wlink.auth.packets.b12340.realmlist import (
    make_realmlist_request,
    RealmlistResponse,
    RealmlistRequest,
)
from wlink.log import logger
from typing import Optional, Tuple

from wlink.auth.errors import InvalidLogin, AuthError
from wlink.utility.string import bytes_to_int

from headless import events
from headless.utility.enum import ComparableEnum

# TODO: transitions
class AuthSession:
    def __init__(self, nursery, emitter, proxy: Optional[Tuple[str, int]] = None):
        self.proxy = proxy
        self.stream: Optional[AuthStream] = None
        self._nursery = nursery
        self._emitter = emitter
        self._stream: Optional[trio.abc.HalfCloseableStream] = None
        self._srp: Optional[cryptography.WoWSrpClient] = None
        self._session_key = None
        self._username = None
        self._state = AuthState.not_connected

    @property
    def state(self):
        return self._state

    @property
    def session_key(self):
        return self._session_key

    async def aclose(self):
        if self._stream is not None:
            await self._stream.aclose()
            self._stream = None

        self._state = AuthState.not_connected

    async def connect(self, address=None, proxy=None, stream=None):
        if address is not None:
            if type(address) == str:
                address = (address, 3724)
            logger.info(f"Connecting to {address}...")

        elif stream is not None:
            logger.info(f"Using {stream} as auth stream.")

        if stream is None:
            if address is None:
                raise ValueError("Both stream and address cannot be None!")

            if self.proxy is not None or proxy is not None:
                logger.info(f"Using SOCKS proxy server: {proxy}")
                self._stream = socks5.Socks5Stream(
                    destination=address, proxy=proxy or self.proxy or None
                )
                await self._stream.negotiate()

            else:
                self._stream = await trio.open_tcp_stream(*address)
        else:
            self._stream = stream

        self.stream = AuthStream(stream=self._stream)
        self._state = AuthState.connected
        self._emitter.emit(events.auth.connected)
        logger.info("Connected!")

    async def _get_public_ip(self):
        # return '127.0.0.1'
        async def parse_public_ip(stream):
            await stream.send_all(
                "GET / HTTP/1.1\r\nHost: api.ipify.org\r\n\r\n".encode()
            )
            text = (await stream.receive_some()).decode()
            i = text.rfind("\r\n\r\n")
            my_ip = text[i + 4 :]
            return my_ip

        if self.proxy is not None:
            async with socks5.Socks5Stream(
                destination=("api.ipify.org", 80), proxy=self.proxy
            ) as stream:
                return await parse_public_ip(stream)
        else:
            async with await trio.open_tcp_stream("api.ipify.org", 80) as stream:
                return await parse_public_ip(stream)

    async def authenticate(
        self,
        username,
        password,
        debug=None,
        country="enUS",
        arch="x86",
        os="OSX",
        build=12340,
        version="3.3.5",
    ):
        public_ip = await self._get_public_ip()
        logger.info(
            f"Authenticating with: {username=}, {public_ip=}, {country=}, {arch=}, {os=}, {build=}, {version=}..."
        )
        self._state = AuthState.logging_in
        self._username = username
        self._emitter.emit(events.auth.authenticating)

        await self.stream.send_packet(
            ChallengeRequest,
            make_challenge_request(
                username=username,
                country=country,
                arch=arch,
                os=os,
                build=build,
                ip=public_ip,
                version=version,
            ),
        )

        challenge_response = await self.stream.receive_packet(ChallengeResponse)
        client_private = debug["client_private"] if debug is not None else None

        if challenge_response.response != Response.success:
            raise AuthError(f"Challenge response: {challenge_response.response}")

        self._srp = cryptography.WoWSrpClient(
            username=username,
            password=password,
            prime=challenge_response.rc4.prime,
            generator=challenge_response.rc4.generator,
            client_private=client_private,
        )

        client_public, session_proof = self._srp.process(
            challenge_response.rc4.server_public, challenge_response.rc4.salt
        )
        mac_binary_crc = bytes(
            [
                0xB7,
                0x06,
                0xD1,
                0x3F,
                0xF2,
                0xF4,
                0x01,
                0x88,
                0x39,
                0x72,
                0x94,
                0x61,
                0xE3,
                0xF8,
                0xA0,
                0xE2,
                0xB5,
                0xFD,
                0xC0,
                0x34,
            ]
        )
        checksum = int.from_bytes(
            wlink.cryptography.sha.sha1(
                construct.BytesInteger(32, swapped=True).build(client_public)
                + mac_binary_crc
            ),
            byteorder="little",
        )

        self._session_key = int.from_bytes(self._srp.session_key, byteorder="little")
        await self.stream.send_packet(
            ProofRequest,
            make_proof_request(
                client_public=client_public,
                session_proof=session_proof,
                checksum=checksum,
            ),
        )

        proof_response = await self.stream.receive_packet(ProofResponse)
        if proof_response.session_proof_hash != self._srp.session_proof_hash:
            self._state = AuthState.disconnected
            self._emitter.emit(events.auth.invalid_login)
            self._emitter.emit(events.auth.disconnected, reason="Invalid login")
            raise InvalidLogin("Invalid username or password")

        self._state = AuthState.logged_in
        self._emitter.emit(events.auth.authenticated)
        self._session_key = bytes_to_int(self._srp.session_key)
        logger.info(f"Authenticated!")

    async def realms(self):
        await self.stream.send_packet(RealmlistRequest, make_realmlist_request())
        result = await self.stream.receive_packet(RealmlistResponse)
        realmlist = list(result.realms)
        logger.info(f"{realmlist=}")

        self._state = AuthState.realmlist_ready
        self._emitter.emit(events.auth.realmlist_ready, realmlist=realmlist)
        return realmlist


class AuthState(ComparableEnum):
    disconnected = -1
    not_connected = 0
    connected = 1
    logging_in = 2
    logged_in = 3
    realmlist_ready = 4
