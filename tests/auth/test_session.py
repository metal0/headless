import json
import os

import trio
from wlink import cryptography
from wlink.auth import AuthStream
from wlink.auth.packets import (
    ChallengeRequest,
    ProofRequest,
    RealmlistRequest,
    Response,
)
from wlink.auth.packets.b12340.challenge import (
    make_challenge_response,
    ChallengeResponse,
)
from wlink.auth.packets.b12340.proof import make_proof_response, ProofResponse
from wlink.auth.packets.b12340.realmlist import (
    make_realmlist_response,
    RealmlistResponse,
)
from wlink.auth.realm import RealmType, RealmStatus
from wlink.utility.string import bytes_to_int

import headless
from headless.auth import AuthState

logins_filename = os.environ.get("PONT_CREDS")
with open(logins_filename) as f:
    test_servers = json.load(f)

tc_login = test_servers["trinity-core-3.3.5"]["account"]


async def auth_server(stream):
    auth = AuthStream(stream)
    challenge_request = await auth.receive_packet(ChallengeRequest)
    print(challenge_request)

    assert challenge_request.size == 30 + len(challenge_request.account_name)
    assert challenge_request.game == "WoW"
    assert challenge_request.version == "3.3.5"
    assert challenge_request.build == 12340

    generator = 7
    prime = (
        62100066509156017342069496140902949863249758336000796928566441170293728648119
    )
    server_public = (
        29690934590145573207593128186052252288614061230055487511226196652110486395787
    )
    salt = 92090571083452222281680040879036827917433471144889767667508809381093896083463
    await auth.send_packet(
        ChallengeResponse,
        make_challenge_response(
            generator=generator, prime=prime, server_public=server_public, salt=salt
        ),
    )

    proof_request = await auth.receive_packet(ProofRequest)
    print(proof_request)

    client_private = 143386892073113346271045296825355365119602324795205856098132479049957622403427006810653616896639308669514885320513042624825577275523311345156882292579472806120577841118102290052948040847318515534261288049316514160095147951671405527775489066400222418481863631312167863930538967927022064010646095222765545969242
    srp = cryptography.WoWSrpClient(
        username=tc_login["username"],
        password=tc_login["password"],
        prime=prime,
        generator=generator,
        client_private=client_private,
    )

    client_public, session_proof = srp.process(server_public=server_public, salt=salt)
    assert client_public == proof_request.client_public
    assert session_proof == proof_request.session_proof

    actual_session_proof_hash = 1022273791007009790071844123884488983605182042497
    assert bytes_to_int(srp.session_proof_hash) == actual_session_proof_hash

    await auth.send_packet(
        ProofResponse,
        make_proof_response(
            session_proof_hash=actual_session_proof_hash, response=Response.success
        ),
    )
    realmlist_request = await auth.receive_packet(RealmlistRequest)
    print(realmlist_request)

    realms = [
        dict(
            type=RealmType.pvp,
            status=RealmStatus.online,
            name="PontCore",
            address=("127.0.0.1", 8085),
            population=0,
            num_characters=2,
        )
    ]

    await auth.send_packet(RealmlistResponse, make_realmlist_response(realms))


async def client_login(auth_address, stream):
    auth_debug = dict(
        client_private=143386892073113346271045296825355365119602324795205856098132479049957622403427006810653616896639308669514885320513042624825577275523311345156882292579472806120577841118102290052948040847318515534261288049316514160095147951671405527775489066400222418481863631312167863930538967927022064010646095222765545969242
    )

    async with headless.open_client() as client:
        assert client.auth.state == AuthState.not_connected
        await client.auth.connect(auth_address, stream=stream)
        await client.auth.authenticate(
            tc_login["username"], tc_login["password"], debug=auth_debug
        )
        assert client.auth.state >= AuthState.logged_in

        realmlist = await client.auth.realms()
        assert client.auth.state == AuthState.realmlist_ready
        assert realmlist[0].type == RealmType.pvp
        assert realmlist[0].status == RealmStatus.online
        assert realmlist[0].name == "PontCore"
        assert realmlist[0].address == ("127.0.0.1", 8085)
        # assert realmlist[0].populaton == 0
        assert realmlist[0].num_characters == 2


async def test_session():
    (client_stream, server_stream) = trio.testing.memory_stream_pair()
    with trio.fail_after(2):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(client_login, None, client_stream)
            nursery.start_soon(auth_server, server_stream)
