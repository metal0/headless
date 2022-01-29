import glob
import os

from headless.world.warden.module import load_crs, ChallengeResponseFile, ChallengeResponse

# cr_file_pattern = re.compile('([A-F0-9]+)\.cr')

def find_keys(path: str):
    with open(path, 'rb') as f:
        try:
            for i in range(30):
                cr_size = os.path.getsize(path) - i
                print(f'{cr_size=} {ChallengeResponse.sizeof()=}')
                if cr_size % ChallengeResponse.sizeof() != 0:
                    print('file size is not a multiple of challenge response size')
                data = f.read()[i:]
                response = ChallengeResponseFile.parse(data)
                crs_file = load_crs(path)
                print(f'found it! {i=} {path=}')
                print(response)
        except Exception as e:
            print(e)

    seed = 338176079955437417738073427705494077517
    reply = int.from_bytes(b'V\x8c\x05Lx\x1a\x97*`7\xa2)\x0c"\xb5%q\xa0oN', 'little')
    client_key = int.from_bytes(bytes.fromhex('7f96eefda5b63d20a4df8e00cbf48304'), 'little')
    server_key = int.from_bytes(bytes.fromhex('c2b7adedfccca9c2bfb3f85602ba809b'), 'little')

    # for cr in crs_file.crs:
    #     print(cr)
    #     if cr.seed == seed:
    #         print(f'Found seed in {cr}')
    #     if cr.reply == reply:
    #         print(f'Found reply in {cr}')
    #     if cr.client_key == client_key:
    #         print(f'Found client_key in {cr}')
    #     if cr.server_key == server_key:
    #         print(f'Found server_key in {cr}')

def test_all_modules():
    mods_path = os.environ.get('PONT_WARDEN_MODS')
    for path in glob.glob(f'{mods_path}/*.cr'):
        try:
            print(f'\nTrying {path}')
            find_keys(path)
        except:
            pass

# def test_module():ca9c2bfb3f85602ba809b'), 'little')