import os
import hashlib
import base58
import secrets
from Crypto.PublicKey import ECC
from github import Github
import datetime

# Specific wallet address to check for a match
user_input_address = "13zb1hQbWVsc2S7ZTZnP2G4undNNpdh5so"

def generate_private_key(start_range, end_range):
    lower_limit = int(start_range, 16)
    upper_limit = int(end_range, 16)
    private_key = secrets.randbelow(upper_limit - lower_limit) + lower_limit
    return private_key

def generate_public_key(private_key):
    key = ECC.construct(curve='P-256', d=private_key)
    return key.public_key().export_key(format='DER').hex()

def generate_wallet_address(public_key):
    sha256_hash = hashlib.sha256(bytes.fromhex(public_key)).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    binary_address = b'\x00' + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(binary_address).digest()).digest()[:4]
    binary_address += checksum
    wallet_address = base58.b58encode(binary_address).decode()
    return wallet_address

def check_wallet_address_match(generated_address, user_input_address):
    return generated_address == user_input_address

def export_to_file(private_key, public_key, wallet_address):
    with open('bitcoin_details.txt', 'w') as file:
        file.write(f"Private Key: {hex(private_key)}\n")
        file.write(f"Public Key: {public_key}\n")
        file.write(f"Wallet Address: {wallet_address}\n")

def main():
    # Specify the start and end range
    start_range = "0000000000000000000000000000000000000000000000020000000000000000"
    end_range = "000000000000000000000000000000000000000000000003ffffffffffffffff"

    iteration_count = 1

    while True:
        private_key = generate_private_key(start_range, end_range)
        public_key = generate_public_key(private_key)
        wallet_address = generate_wallet_address(public_key)

        print(f"Iteration {iteration_count}: {wallet_address}")

        match_result = check_wallet_address_match(wallet_address, user_input_address)

        if match_result:
            print("\nGenerated Bitcoin Details:")
            print(f"Private Key: {hex(private_key)}")
            print(f"Public Key: {public_key}")
            print(f"Wallet Address: {wallet_address}\n")
            export_to_file(private_key, public_key, wallet_address)
            print("Details exported to bitcoin_details.txt.")

            github_username = "paranomicvibes"
            github_repo_name = "X"
            github_access_token = "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"

            g = Github(github_access_token)
            repo = g.get_user().get_repo(github_repo_name)

            branch_name = f"match_found_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo.get_branch('main').commit.sha)

            file_name = "bitcoin_details.txt"
            file_path = os.path.join(os.getcwd(), file_name)
            content = open(file_path, 'rb').read()

            try:
                contents = repo.get_contents(file_name, ref=branch_name)
                repo.update_file(contents.path, f"Upload {file_name}", content, contents.sha, branch=branch_name)
                print(f"File '{file_name}' updated on GitHub in branch '{branch_name}'.")
            except Exception:
                repo.create_file(file_name, f"Upload {file_name}", content, branch=branch_name)
                print(f"File '{file_name}' created on GitHub in branch '{branch_name}'.")

            break
        iteration_count += 1

if __name__ == "__main__":
    main()
