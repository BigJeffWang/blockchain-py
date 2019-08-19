from wallet.crypto import HDPrivateKey, HDPublicKey, HDKey


master_key, mnemonic = HDPrivateKey.master_key_from_entropy()
print('BIP32 Wallet Generated.')
print('Mnemonic Secret: ' + mnemonic)