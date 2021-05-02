from headless.world.warden import check


def test_calculate_hash_resut():
    seed = 338176079955437417738073427705494077517
    hash, client_key, server_key = check.calculate_hash_result(seed)

    assert hash == bytes.fromhex('568c054c781a972a6037a2290c22b52571a06f4e')
    assert client_key == b'\x7f\x96\xee\xfd\xa5\xb6= \xa4\xdf\x8e\x00\xcb\xf4\x83\x04'
    assert server_key == b'\xc2\xb7\xad\xed\xfc\xcc\xa9\xc2\xbf\xb3\xf8V\x02\xba\x80\x9b'

    seed = 66158793613204800533943873583636181425
    # print(check.calculate_hash_result(seed))