from solana.rpc import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import transfer
from solana.transaction import AccountInfo, CompiledMessage
from solana.publickey import PublicKey
from bip_utils import Bip39Mnemonic, ElectrumPrivateKey

# Replace with your Solana network endpoint (e.g., devnet, mainnet-beta)
cluster_url = "http://api.devnet.solana.com"
client = Client(cluster_url)

# Seed phrase for keypair generation (replace with your own)
seed_phrase = "replace_with_your_seed_phrase"

# Derive keypair from seed phrase using bip_utils (BIP39 mnemonic)
mnemonic = Bip39Mnemonic(seed_phrase)
keypair = Keypair.from_seed(mnemonic.to_seed())

# Recipient's SPL token address (replace with the address you want to send to)
recipient_address = PublicKey("replace_with_recipient_address")

# SPL token address (replace with the SPL token you want to transfer)
spl_token_address = PublicKey("replace_with_spl_token_address")

# Account information for the SPL token account (optional, can be retrieved from the network)
spl_token_account = None  # Replace with retrieved account info if needed

# Get the associated token program address for the SPL token
associated_token_program_id = PublicKey("ATokenGPXz6uZwGCUh9BgubeLRMu3aSrvzGkvzRJsuTV")
associated_token_account = client.get_associated_token_account(
    spl_token_address, keypair.public_key
)

# Get the mint address (optional, can be retrieved from the network)
mint_address = spl_token_address  # Assuming the SPL token address is also the mint address

# Get the token supply (optional, can be retrieved from the network)
token_supply = None  # Replace with retrieved token supply if needed

# Amount of SPL tokens to transfer (replace with the desired amount)
amount = 100000  # Adjust as needed, considering decimals for the SPL token

# Get minimum balance required to hold an SPL token account (optional)
rent = client.get_minimum_balance_for_rent_exempt_account(80)

# Construct the transaction

# 1. (Optional) Create the associated token account for the recipient if it doesn't exist
if not spl_token_account:
    create_associated_token_ix = client.get_associated_token_account_create_instruction(
        payer=keypair.public_key,
        associated_token=associated_token_account,
        mint=spl_token_address,
        owner=recipient_address,
    )

# 2. Transfer SPL tokens
transfer_ix = transfer(
    from_pubkey=associated_token_account,
    to_pubkey=recipient_address,
    amount=amount,
    owner=keypair.public_key,
)

# 3. (Optional) If the recipient's account balance is below rent exemption, include an instruction to fund it
if client.get_balance(recipient_address) < rent:
    fund_recipient_ix = system_program.transfer(
        from_pubkey=keypair.public_key,
        to_pubkey=recipient_address,
        lamports=rent,
    )

# Combine instructions into a transaction
instructions = [create_associated_token_ix] if not spl_token_account else []
instructions.extend([transfer_ix, fund_recipient_ix if client.get_balance(recipient_address) < rent else None])
transaction = Transaction(fee_payer=keypair.public_key, instructions=instructions)

# Sign the transaction
transaction.sign(keypair)

# Send the transaction
response = client.send_transaction(transaction)

print(f"Transaction sent: {response['result']}")