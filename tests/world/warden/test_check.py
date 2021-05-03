from headless.world.warden import check


def test_calculate_hash_resut():
    seed = 338176079955437417738073427705494077517
    id = '79c0768d657977d697e10bad956cced1'
    hash, client_key, server_key = check.calculate_hash_result(seed, id)

    assert hash == bytes.fromhex('568c054c781a972a6037a2290c22b52571a06f4e')
    assert client_key == bytes.fromhex('7f96eefda5b63d20a4df8e00cbf48304')
    assert server_key == bytes.fromhex('c2b7adedfccca9c2bfb3f85602ba809b')

    # seed = 66158793613204800533943873583636181425
    # print(check.calculate_hash_result(seed))