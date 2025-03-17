import random
import string
import json
import os

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def generate_account_data(num_accounts):
    account_data = {}
    for i in range(num_accounts):
        username = f"joronimo{i}"
        password = generate_random_string(12)
        email = f"{username}@gmail.com"
        account_data[email] = password
    return account_data

def save_account_data_to_json(account_data, filename="accounts.json"):
    try:
        with open(filename, 'w') as f:
            json.dump(account_data, f, indent=4)
        print(f"Account data saved to {filename}")
    except Exception as e:
        print(f"Error saving account data: {e}")

if __name__ == "__main__":
    num_accounts = 5 # number of fake accounts.
    accounts = generate_account_data(num_accounts)
    save_account_data_to_json(accounts)
