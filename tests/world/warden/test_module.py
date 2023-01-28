import os
import trio

from headless.world.warden.cr import ChallengeResponseFile


async def find_cr(data: bytes):
    for i in range(len(data)):
        try:
            crf = ChallengeResponseFile.parse(data[i:])
            await trio.lowlevel.checkpoint()
            for cr in crf.crs:
                if (
                    hex(cr.seed)
                    in [
                        "0x9a263596f26b84528146147ddbfdde14",
                        "0x4d808d2c77d905c41a6380ec08586afe",
                    ]
                    or hex(cr.reply) == "0x568c054c781a972a6037a2290c22b52571a06f4e"
                ):
                    print(f"Found {i=} {cr=}")
                    return i
            assert False
        except Exception as e:
            pass
            # print(f'{e=}')


async def find_keys(path: str):
    with open(path, "rb") as f:
        data = f.read()
        print(f"{len(data)=}")
        try:
            # i = await find_cr(data)
            response = ChallengeResponseFile.parse(data)
            print(f"found it! {path=}")
            print(response)
        except Exception as e:
            print(e)


async def test_all_modules():
    mods_path = os.environ.get("PONT_WARDEN_MODS")
    # for path in glob.glob(f'{mods_path}/*.cr'):
    with trio.fail_after(2):
        for path in [
            "0DBBF209A27B1E279A9FEC5C168A15F7.cr",
        ]:
            try:
                print(f"\nCheck: {path}")
                await find_keys(f"{mods_path}/{path}")
            except:
                pass


# def test_module():ca9c2bfb3f85602ba809b'), 'little')
