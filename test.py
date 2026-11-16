import hashlib

# 1. Définir la chaîne à hasher (en string)
texte = "123456"

# 2. Encoder la chaîne en octets (bytes), car hashlib travaille sur des octets
texte_encode = texte.encode("utf-8")

# 3. Créer l'objet de hachage (ici sha256) et y passer les octets
hash_objet = hashlib.sha256(texte_encode)

# 4. Récupérer le résultat sous forme hexadécimale
hash_hex = hash_objet.hexdigest()

print(hash_hex)