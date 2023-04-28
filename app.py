import os
from web3 import Web3
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
from network import *
from contractInfo import *

# env_path = find_dotenv()
# print(env_path)

load_dotenv()

KEY_OWNER = os.getenv("PRIVATE_KEY_DEPLOYER")
KEY_PAYEE = os.getenv("PRIVATE_KEY_PAYEE")
# print(KEY_OWNER)
# print(KEY_PAYEE)

isTestnet_provider = selectNetwork()
print(isTestnet_provider)

# Gas cost
GAS = 1500000

# Gas price
GASPRICE = 3000000000

# Cheque validity window
VALIDITY_WINDOW_IN_HRS = 1

providers = setUpProvider()
web3 = Web3(providers["local_provider"])
chainId = GANACHE_CHAIN_ID


def checksum(x=str):
    return web3.to_checksum_address(x)


def getNonce(x=str):
    return web3.eth.get_transaction_count(checksum(x))

def convertToWei(x:int):
    return web3.to_wei(x, "gwei")

wallet_owner = Account.create("ENTROPY")
wallet_payee = Account.create("ENTROPY")

# If we're not on testnet, move funds from ganache to local account
if not isTestnet_provider:
    print("Using the local blockchain - Ganache ...")
    accounts = [wallet_owner, wallet_payee]
    for account in accounts:
        hash = web3.eth.send_transaction(
            transaction={
                "from": checksum(web3.eth.accounts[0]),
                "to": account.address,
                "gas": GAS,
                "gasPrice": GASPRICE,
                "nonce": getNonce(web3.eth.accounts[0]),
                "value": web3.to_wei(10000000000, "gwei"),
            }
        )
        receipt = web3.eth.wait_for_transaction_receipt(hash)
        balance = web3.eth.get_balance(account.address)
        print("Balance of account {} :".format(account.address))

# If network is testnet, swap accounts
if isTestnet_provider:
    print("Switching to Celo testnet : (Alfajores) ...")
    chainId = ALFAJORES_CHAIN_ID
    new_wallet_owner = Account.from_key(KEY_OWNER)
    new_wallet_payee = Account.from_key(KEY_PAYEE)
    web3 = Web3(providers["testNet_provider"])

def printLog(x:str):
    print("Invoking {} ...".format(x))

class ChequePayent:
    printLog("ChequePayment constructor")
    print(chainId)

    def __init__(self) -> None:
        self.ChequePayent_contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        deploy_transaction = self.ChequePayent_contract.constructor().build_transaction(
            {
                "chainId": chainId,
                "from": wallet_owner.address,
                "nonce": getNonce(wallet_owner.address),
            }
        )

        signed_trxn = web3.eth.account.sign_transaction(
            deploy_transaction, private_key=wallet_owner.key
        )

        hash = web3.eth.send_raw_transaction(signed_trxn.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(transaction_hash=hash)

        self.contract_address = receipt.contractAddress

        print("ChequePayment deployed to {}\n".format(self.contract_address))
        print("Transaction hash: {}\n".format(web3.to_hex(receipt.transactionHash)))

        self.instance = web3.eth.contract(address=checksum(self.contract_address), abi=abi)
    
    def getOpenCheques(self, funcName:str):
        print("Fetching current opened cheques ...")
        openCheques = self.instance.functions.openCheques().call({'from': wallet_payee.address})
        print("Opened Cheque balance after {0} was called : {1}\n".format(funcName, openCheques));
    
    def drawCheque(self, amount: int, value: int):
        printLog("DrawCheque")
        trxn = self.instance.functions.drawCheque(
            checksum(wallet_payee.address), 
            amount, 
            VALIDITY_WINDOW_IN_HRS
        ).build_transaction(
            {
                'chainId': chainId,
                'from': wallet_owner.address,
                'nonce': getNonce(wallet_owner.address),
                'value': value
            }
        )

        signed_trx = web3.eth.account.sign_transaction(trxn, private_key=wallet_owner.key)
        recpt = web3.eth.wait_for_transaction_receipt(
            web3.eth.send_raw_transaction(signed_trx.rawTransaction)
        )
        print("Transaction hash: {}\n".format(web3.to_hex(recpt.transactionHash)))
        self.getOpenCheques("DrawCheque")

    def increaseCheque(self, amount: int, msgValue: int):
        printLog("Increase")
        trxn = self.instance.functions.increaseChequeValue(
            wallet_payee.address, 
            amount, 
        ).build_transaction(
            {
                'chainId': chainId,
                'from': wallet_owner.address,
                'nonce': getNonce(wallet_owner.address),
                'value': msgValue
            }
        )

        signed_trx = web3.eth.account.sign_transaction(trxn, private_key=wallet_owner.key)
        recpt = web3.eth.wait_for_transaction_receipt(
            web3.eth.send_raw_transaction(signed_trx.rawTransaction)
        )
        print("Transaction hash: {}\n".format(web3.to_hex(recpt.transactionHash)))
        self.getOpenCheques("IncreaseCheque")

    def reduceCheque(self, amount: int):
        printLog("ReduceCheque")
        trxn = self.instance.functions.reduceChequeValue(
            wallet_payee.address, 
            amount
        ).build_transaction(
            {
                'chainId': chainId,
                'from': wallet_owner.address,
                'nonce': getNonce(wallet_owner.address),
            }
        )

        signed_trx = web3.eth.account.sign_transaction(trxn, private_key=wallet_owner.key)
        recpt = web3.eth.wait_for_transaction_receipt(
            web3.eth.send_raw_transaction(signed_trx.rawTransaction)
        )
        print("Transaction hash: {}\n".format(web3.to_hex(recpt.transactionHash)))
        self.getOpenCheques("ReduceCheque")
    
    def cancelCheque(self):
        printLog("CancelCheque")
        trxn = self.instance.functions.cancelDrawnCheque(
            wallet_payee.address
        ).build_transaction(
            {
                'chainId': chainId,
                'from': wallet_owner.address,
                'nonce': getNonce(wallet_owner.address),
            }
        )

        signed_trx = web3.eth.account.sign_transaction(trxn, private_key=wallet_owner.key)
        recpt = web3.eth.wait_for_transaction_receipt(
            web3.eth.send_raw_transaction(signed_trx.rawTransaction)
        )
        print("Transaction hash: {}\n".format(web3.to_hex(recpt.transactionHash)))
        self.getOpenCheques("CancelCheque")

    def cashout(self):
        printLog("Cashout")
        trxn = self.instance.functions.cashout().build_transaction(
            {
                'chainId': chainId,
                'from': wallet_payee.address,
                'nonce': getNonce(wallet_payee.address),
            }
        )

        signed_trx = web3.eth.account.sign_transaction(trxn, private_key=wallet_payee.key)
        recpt = web3.eth.wait_for_transaction_receipt(
            web3.eth.send_raw_transaction(signed_trx.rawTransaction)
        )
        print("Transaction hash: {}\n".format(web3.to_hex(recpt.transactionHash)))
        self.getOpenCheques("Cashout")

# Function values
init_cheque_amount = convertToWei(10000000)
new_cheque_amount = convertToWei(20000000);
msg_value = convertToWei(100000000)
increment = convertToWei(50000000);
decrement = convertToWei(40000000);

# Create an instance of ChequePayment contract
cheque_instance = ChequePayent()

# Invoke the contract functions in order
cheque_instance.drawCheque(init_cheque_amount, msg_value)
cheque_instance.cancelCheque();
cheque_instance.drawCheque(new_cheque_amount, msg_value);
cheque_instance.increaseCheque(increment, msg_value);
cheque_instance.reduceCheque(decrement);
cheque_instance.cashout();
