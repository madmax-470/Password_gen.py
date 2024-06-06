import sqlite3
import hashlib
import random
import string
import os

def setup_database():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT NOT NULL,
            passphrase TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    hash_object = hashlib.sha256(password.encode())
    hash_hex = hash_object.hexdigest()
    return hash_hex

def store_hash_and_passphrase(hash_hex, passphrase):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('INSERT INTO passwords (hash, passphrase) VALUES (?, ?)', (hash_hex, passphrase))
    conn.commit()
    conn.close()

def store_cleartext_password(password, hash_hex, passphrase):
    with open('cleartext_passwords.txt', 'a') as file:
        file.write(f"Password: {password}, Hash: {hash_hex}, Passphrase: {passphrase}\n")

def retrieve_hash(passphrase):
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('SELECT hash FROM passwords WHERE passphrase=?', (passphrase,))
    row = c.fetchone()
    conn.close()
    if row:
        hash_hex = row[0]
        return hash_hex
    else:
        return None

def retrieve_cleartext_password(passphrase):
    if os.path.exists('cleartext_passwords.txt'):
        with open('cleartext_passwords.txt', 'r') as file:
            for line in file:
                if f"Passphrase: {passphrase}" in line:
                    parts = line.strip().split(", ")
                    password = parts[0].split(": ")[1]
                    return password
    return None

def main():
    setup_database()
    
    action = input("Do you want to generate a password, input a password, or retrieve? (generate/input/retrieve): ").strip().lower()
    
    if action == "generate":
        length = int(input("Enter the desired password length (10-15 characters): "))
        if length < 10 or length > 15:
            print("Invalid length. Please choose a length between 10 and 15 characters.")
            return
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        hash_hex = hash_password(password)
        passphrase = input("Enter a passphrase for this password: ").strip()
        store_hash_and_passphrase(hash_hex, passphrase)
        store_cleartext_password(password, hash_hex, passphrase)
        print("Generated password:", password)
        print("SHA-256 hash:", hash_hex)
    elif action == "input":
        password = input("Enter your password: ").strip()
        hash_hex = hash_password(password)
        passphrase = input("Enter a passphrase for this password: ").strip()
        store_hash_and_passphrase(hash_hex, passphrase)
        store_cleartext_password(password, hash_hex, passphrase)
        print("Input password:", password)
        print("SHA-256 hash:", hash_hex)
    elif action == "retrieve":
        passphrase = input("Enter the passphrase: ").strip()
        retrieved_hash = retrieve_hash(passphrase)
        if retrieved_hash:
            print("Retrieved hash:", retrieved_hash)
            dehash_action = input("Do you want to dehash the password? (yes/no): ").strip().lower()
            if dehash_action == "yes":
                cleartext_password = retrieve_cleartext_password(passphrase)
                if cleartext_password:
                    print("Cleartext password:", cleartext_password)
                else:
                    print("Passphrase not found in cleartext storage!")
        else:
            print("Passphrase not found!")
    else:
        print("Invalid action!")

if __name__ == "__main__":
    main()
