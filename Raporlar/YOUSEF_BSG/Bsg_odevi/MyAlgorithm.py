import random

# ===============================
# 1. Key Generation (64 bit)
# ===============================
def Anahtar_Uret():
    return [random.randint(0, 255) for _ in range(8)]


# ===============================
# 2. S-Box Definition
# ===============================
S_BOX = list(range(256))
random.shuffle(S_BOX)

INV_S_BOX = [0] * 256
for i, v in enumerate(S_BOX):
    INV_S_BOX[v] = i


# ===============================
# 3. Encryption Function
# ===============================
def Sifrele(duz_metin, anahtar):
    cipher = []

    for i in range(len(duz_metin)):
        x = ord(duz_metin[i])           # ASCII
        x = x ^ anahtar[i % 8]          # XOR
        x = S_BOX[x]                    # Substitution
        cipher.append(x)

    return cipher


# ===============================
# 4. Decryption Function
# ===============================
def Desifrele(sifreli_metin, anahtar):
    plain = ""

    for i in range(len(sifreli_metin)):
        x = INV_S_BOX[sifreli_metin[i]] # Reverse Substitution
        x = x ^ anahtar[i % 8]          # XOR
        plain += chr(x)

    return plain


# ===============================
# 5. Tests
# ===============================
key = Anahtar_Uret()
text = "HELLO"

cipher = Sifrele(text, key)
result = Desifrele(cipher, key)

print("Original Text:", text)
print("Encrypted:", cipher)
print("Decrypted:", result)

# Test 2: Key Sensitivity
key2 = key.copy()
key2[0] ^= 1  # change 1 bit

wrong = Desifrele(cipher, key2)
print("Decryption with wrong key:", wrong)
