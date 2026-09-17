from app.utils.password import hash_password, verify_password


def test_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)


def test_wrong_password_fails():
    hashed = hash_password("correct horse battery staple")
    assert not verify_password("wrong password", hashed)


def test_hashes_are_salted():
    a = hash_password("same password")
    b = hash_password("same password")
    assert a != b


def test_long_password_beyond_bcrypt_limit_still_verifies():
    long_password = "a" * 100 + "tail"
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed)
    # bcrypt only sees the first 72 bytes, so a password that differs only
    # after byte 72 verifies against the same hash.
    also_matches = "a" * 100 + "xxxx"
    assert verify_password(also_matches, hashed)
