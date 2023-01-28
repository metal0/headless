import trio
from wlink import cryptography
from wlink.auth import AuthProtocol, Response
from wlink.auth.realm import RealmStatus, RealmType


class MockAuthServerSession:
    def __init__(self):
        pass

    async def handle(self, stream):
        protocol = AuthProtocol(stream)
        challenge_request = await protocol.receive_challenge_request()
        print(challenge_request)

        assert challenge_request.size == 30 + len(challenge_request.account_name)
        assert challenge_request.game == "WoW"
        assert challenge_request.version == "3.3.5"
        assert challenge_request.build == 12340

        generator = 7
        prime = 62100066509156017342069496140902949863249758336000796928566441170293728648119
        server_public = 29690934590145573207593128186052252288614061230055487511226196652110486395787
        salt = 92090571083452222281680040879036827917433471144889767667508809381093896083463
        await protocol.send_challenge_response(
            generator=generator, prime=prime, server_public=server_public, salt=salt
        )

        proof_request = await protocol.receive_proof_request()
        print(proof_request)

        client_private = 143386892073113346271045296825355365119602324795205856098132479049957622403427006810653616896639308669514885320513042624825577275523311345156882292579472806120577841118102290052948040847318515534261288049316514160095147951671405527775489066400222418481863631312167863930538967927022064010646095222765545969242
        srp = cryptography.WoWSrpClient(
            username=challenge_request.account_name,
            password="password",
            prime=prime,
            generator=generator,
            client_private=client_private,
        )

        client_public, session_proof = srp.process(
            server_public=server_public, salt=salt
        )
        actual_session_proof_hash = 0

        await protocol.send_proof_response(
            session_proof_hash=actual_session_proof_hash, response=Response.success
        )
        # req = await protocol.receive_realmlist_request()
        print(await protocol._receive_some())

        realms = [
            dict(
                type=RealmType.pvp,
                status=RealmStatus.online,
                name="PontCore",
                address=("10.179.205.116", 8085),
                population=0,
                num_characters=2,
            )
        ]

        await protocol.send_realmlist_response(realms=realms)


async def new_serve(stream):
    session = MockAuthServerSession()
    print(f"new {session=}")
    await session.handle(stream)


async def start():
    await trio.serve_tcp(new_serve, 3724)


class MockAuthServer:
    def __init__(self):
        pass


if __name__ == "__main__":
    trio.run(start)
