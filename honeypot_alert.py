import os
import time
import requests
from web3 import Web3
from dotenv import load_dotenv

# Load .env file
load_dotenv()
BASE_RPC = os.getenv("BASE_RPC")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")

# Web3 setup
w3 = Web3(Web3.HTTPProvider(BASE_RPC))
telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram(msg):
    try:
        requests.post(telegram_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        print("Telegram alert sent:", msg)
    except Exception as e:
        print("Telegram error:", e)

def check_honeypot(token_address):
    token_abi = [
        {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
         "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]
    token = w3.eth.contract(address=token_address, abi=token_abi)
    try:
        token.functions.transfer(WALLET_ADDRESS, 1).estimate_gas({'from': WALLET_ADDRESS})
        return True   # Safe token
    except:
        return False  # Honeypot

def detect_new_tokens():
    latest_block = w3.eth.block_number
    print(f"Starting from block: {latest_block}")
    while True:
        block = w3.eth.get_block('latest', full_transactions=True)
        for tx in block.transactions:
            if tx.to is None:  # contract deployment
                receipt = w3.eth.get_transaction_receipt(tx.hash)
                address = receipt.contractAddress

                # Honeypot filter
                if check_honeypot(address):
                    msg = f"Safe Token Detected!\nAddress: {address}\nBlock: {block.number}"
                    send_telegram(msg)
                else:
                    print(f"Skipped Honeypot Token: {address}")
        time.sleep(2)

if __name__ == "__main__":
    detect_new_tokens()
  
