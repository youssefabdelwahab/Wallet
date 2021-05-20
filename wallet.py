from constants import *

import json 

import subprocess
import os

from web3 import Web3
import bit
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI


from dotenv import load_dotenv

from web3.middleware import geth_poa_middleware 

from eth_account import Account 

from getpass import getpass

load_dotenv()

m_key = os.getenv('m_key')

alt_coins = [BTC , ETH , BTCTEST]
 
def smart_wallet():
    coins = {}
    for x in alt_coins: 
    
        command = f'php ./derive -g --mnemonic="{m_key}" --coin={x} --numderive=3 --format=json -g'
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        p_status= p.wait()
        (output, err) = p.communicate()
        keys = json.loads(output)
        coins[x] = keys

    return coins

all_wallets = smart_wallet()

# print(all_wallets)







w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



def priv_key_to_account(coin , priv_key ): 

    if coin == ETH: 
        return Account.privatekeyToAccount(priv_key)
    if coin == BTCTEST: 
        return PrivateKeyTestnet(priv_key)


def create_tx(coin , account , to , amount): 

    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(

            {'from': account.address, 'to': to , 'value': amount}
        ) 

        return { 

            'chainId': w3.eth.chain_id,
            'from': account.address,
            'to': to, 
            'value': amount, 
            'gasPrice': w3.eth.generateGasPrice(), 
            'gas': gasEstimate, 
            'nonce': w3.eth.getTransactionCount(w3.toChecksumAddress(account.address))

        } 

    if coin == BTCTEST: 

        return PrivateKeyTestnet.prepare_transaction(account.address, [(to,amount,BTC)])


def send_tx(coin , account , to , amount):

    tx_raw = create_tx(coin , account , to , amount)
    signed = account.sign_transaction(tx_raw)

    if coin == ETH:
        eth_trans = w3.eth.send_raw_transaction(signed.rawTransaction)
        return eth_trans.hex()

    if coin == BTCTEST:
        btc_trans = NetworkAPI.broadcast_tx_testnet(signed)
        return btc_trans



def send_tx_2(coin , to="mz4wxeuBJSqKGZ1h1y3Xoa6Y9Fkf7f9otE" , amount= 0.00000001, priv_key="cUgqg4WXK9WnDeQ3xXfCuL5mLnRcxcvpQASEadhWrx7ixPZQxS1Z"): 
    converted_account = priv_key_to_account(coin, priv_key)
    process_tx = send_tx(coin, converted_account, to, amount)
    return process_tx

print(send_tx_2(BTCTEST))
# print("-"*64)
# print(json.dumps(all_wallets[BTCTEST], indent=4))
# #n4fYt3sNbMLDxswiWbp59CrihURRYCAMqw

