from utils.crypto_utils import super_deAES, super_AES

# d = {"private_key": "11CAA2F2F8DB42E3F843C022E8C529FB647CA5F4F933E6266480C54412918374"}
# key = "58696e6469736869313233"
# nonce = "776f62757a686964616f"
# res = super_AES(d, key, nonce)
# print(res)

# d_de = {"private_key": "9cd82f32992b2f7306722513513eb647e025be6f64817958e04908030ae0a99b49562dc275425ca4a65f1770eabd71ba02abdfd078e52a918696f7ff44177cc7cc909cc155efeb8c89bbd32dd7031cda"}
d_de = {"private_key": "fd51f2fc3962f9e7499ab185c7556d77c40e8b657cf1998e7413a9a409cf8e7f4c5cece5865cd39e4351e8cc07c2979b7bb06a5d5d4576fcc478ec1e0624a757db96c654640922a84b6fa96393ce85f9"}
# eth
# key = "58696e6469736869313233"
# nonce = "776f62757a686964616f"

# gather eth
key = "58696e6469736869313233"
nonce = "776f62757a686964616f"
res_de = super_deAES(d_de, key, nonce)
print(res_de)