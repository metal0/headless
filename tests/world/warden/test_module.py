import glob
import hashlib
import re

from headless.world.warden.module import load_crs

cr_file_pattern = re.compile('([A-F0-9]+)\.cr')

def find_keys(path: str):
    crs_file = load_crs(path)

    seed = 338176079955437417738073427705494077517
    reply = int.from_bytes(bytes.fromhex('568c054c781a972a6037a2290c22b52571a06f4e'), 'little')
    client_key = int.from_bytes(bytes.fromhex('7f96eefda5b63d20a4df8e00cbf48304'), 'little')
    server_key = int.from_bytes(bytes.fromhex('c2b7adedfccca9c2bfb3f85602ba809b'), 'little')

    for cr in crs_file.crs:
        if cr.seed == seed:
            print(f'Found seed in {cr}')
        if cr.reply == reply:
            print(f'Found reply in {cr}')
        if cr.client_key == client_key:
            print(f'Found client_key in {cr}')
        if cr.server_key == server_key:
            print(f'Found server_key in {cr}')

def test_all_modules():
    for path in glob.glob('/home/fure/Documents/vmangos-warden_modules/*.cr'):
        try:
            print(f'Trying {path}')
            find_keys(path)
        except:
            pass

# def test_module():ca9c2bfb3f85602ba809b'), 'little')