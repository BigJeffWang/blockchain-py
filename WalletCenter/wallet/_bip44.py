from wallet.crypto import HDPrivateKey, HDKey, checksum_encode


def test1():
    # master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy '
    master_key = HDPrivateKey.master_key_from_mnemonic('wangye snap patient survey sleep strategy '
                                                       'finger bone real west arch protect', passphrase='')
    root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
    acct_priv_key = root_keys[-1]
    print("acct_priv_key : " + acct_priv_key._key.to_hex())
    print("acct pub key : " + acct_priv_key.public_key.to_b58check())
    print(type(acct_priv_key))
    for j in range(10):
        for i in range(10):
            keys = HDKey.from_path(acct_priv_key, '{change}/{index}'.format(change=j, index=i))
            private_key = keys[-1]
            public_key = private_key.public_key
            print("change %s:" % j)
            print("Index %s:" % i)
            print("  Private key (hex, compressed): " + private_key._key.to_hex())
            print("  Address: " + private_key.public_key.address())
            print("  Public key: " + public_key.to_hex())
            print('  Public key format: ' + public_key.to_b58check())

    # Get Account XPUB
    print("\nGet Account XPUB")
    # master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy finger bone real west arch protect')
    master_key = HDPrivateKey.master_key_from_mnemonic('wangye snap patient survey sleep strategy finger bone real west arch protect')
    root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
    acct_priv_key = root_keys[-1]
    acct_pub_key = acct_priv_key.public_key
    print("Private key (hex, compressed): " + acct_priv_key._key.to_hex())
    print("Address: " + acct_pub_key.address())
    print('Account Master Public Key (Hex): ' + acct_pub_key.to_hex())
    print('XPUB format: ' + acct_pub_key.to_b58check())

    # Get Address from XPUB
    print("\nGet Address from XPUB")
    # acct_pub_key = HDKey.from_b58check('xpub6DKMR7KpgCJbiN4TdzcqcB1Nk84D9bsYUBhbk43EjRqH4RTjz7UgGLZxcQ4JdHBSHDmTUDLApMwYHRQCbbMCPQEtcbVofZEQjFazpGPT1nW')
    acct_pub_key = HDKey.from_b58check('xpub6C86Jgis1uMYSXyvMJCC2YkSN2Lv2ZJbRqeu8ssuHRb5Ya5EkcTV9vvpAEo1QhydcWJM8Nngn2fvVc4NvagskFzVEYSF7QHVSotMqFtKwnJ')
    keys = HDKey.from_path(acct_pub_key, '{change}/{index}'.format(change=0, index=0))
    address = keys[-1].address()
    print('Master Account address: ' + address)

    acct_pub_key = HDKey.from_b58check('xpub6Gdm72AiPaiVzhrtYbGkpULhFBpZTTVjUCrfJeUFX3U9CEWjLG53TuBqNungVHoXnNRQw7gAx2coqJJKa4iZHp4bz4EroniKwRvF8CEkjHw')
    address = acct_pub_key.address()
    print('Subaccount Public key to Account address: ' + address)

    # Get 64 Character Private Key from XPRIV
    print("\nGet 64 Character Private Key from XPRIV")
    print("Private key (hex): " + private_key._key.to_hex())
    print("acct_priv_key (hex): " + acct_priv_key._key.to_hex())


def test2():
    master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy finger bone real west arch protect', passphrase='')
    root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
    acct_priv_key = root_keys[-1]
    print("master_key")
    print(master_key._key.to_hex())
    print(master_key.to_b58check())
    print(master_key.public_key.address())
    print(master_key.public_key.to_hex())
    print(master_key.public_key.to_b58check())
    print("root_keys")

    for i in root_keys:
        acct_priv_key = i
        print("acct_priv_key : " + acct_priv_key._key.to_hex())
        print("acct_priv_key to_b58check : " + acct_priv_key.to_b58check())
        print("acct pub key : " + acct_priv_key.public_key.to_b58check())
        print("acct address : " + acct_priv_key.public_key.address())
        print("acct address to_hex: " + acct_priv_key.public_key.to_hex())
    j = 0
    i_list = [0, 10000, 100000, 1000000, 10000000, 100000000]
    for i in i_list:
        keys = HDKey.from_path(acct_priv_key, '{change}/{index}'.format(change=j, index=i))
        private_key = keys[-1]
        public_key = private_key.public_key
        print("change %s:" % j)
        print("Index %s:" % i)
        print("  Private key (hex, compressed): " + private_key._key.to_hex())
        print("  Address: " + private_key.public_key.address())
        print("  Public key: " + public_key.to_hex())
        print('  Public key format: ' + public_key.to_b58check())


def test3():
    addrstr = '0x4de3bd760b29c02a852ba30435c06a6f2848c664'

    real_addr = checksum_encode(addrstr)

    print(addrstr)
    print(real_addr)


def test4():
    master_key = HDPrivateKey.master_key_from_mnemonic('laundry snap patient survey sleep strategy finger bone real west arch protect', passphrase='')
    root_keys = HDKey.from_path(master_key, "m/44'/60'/0'")
    acct_priv_key = root_keys[-1]
    j = 0
    i = 100000000
    keys = HDKey.from_path(acct_priv_key, '{change}/{index}'.format(change=j, index=i))
    subacct_private_key = keys[-1]

    public_key = subacct_private_key.public_key

    print("  Private key (hex, compressed): " + subacct_private_key._key.to_hex())
    print('  Public key format: ' + public_key.to_b58check())
    print('  Public key address: ' + public_key.address())

    address = "0x4dE3BD760B29C02A852ba30435C06A6F2848C664"
    print("  Public key address: " + address)

    subacct_pub_key = HDKey.from_b58check(public_key.to_b58check())
    subacct_pub_address = subacct_pub_key.address()
    print("  Public key address: " + subacct_pub_address)


if __name__ == "__main__":
    # test2()
    test3()
    # test4()
