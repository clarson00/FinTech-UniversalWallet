
# Initial import of libraries
import json
import os
import subprocess
import bit
import web3
from pprint import pprint
import time

from bit import wif_to_key, PrivateKeyTestnet
from bit.network import NetworkAPI
#from constants import *
from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware


BTC = 'btc'
ETH = 'eth'
BTCTEST = 'btc-test'
mnemonic = "\"wide dizzy vessel combine profit final shed rookie cry excuse rate abandon\""

#load_dotenv()
#mnemonic = os.getenv('MNEMONIC')

def derive_wallets(mnemonic, coin, num):
    
    command = f'php ./derive -g --mnemonic={mnemonic} --coin {coin} --numderive {num} --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --format=json'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    process_status = process.wait()
    #pprint(output)
    keys = json.loads(output)
    #print(keys)
    
    return keys



def coins():

    coin_dict = {
        'btc-test' : derive_wallets(mnemonic, BTCTEST, 3),
        'eth' : derive_wallets(mnemonic, ETH, 3)
    }
    #pprint(coin_dict)
    return coin_dict


def priv_key_to_account(coin, priv_key):

    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin,account,to,amount):

    if coin == ETH:
        transaction = {'nonce':web3.eth.getTransactionCount(account.address),
        'gasPrice':web3.eth.gasPrice,
        'gas':web3.eth.estimateGas({"from":account.address,"to":to,"value":amount})
        ,'to':to,'from':account,'value':amount}

        return transaction

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address,[(to, amount, BTC)])


def send_tx(coin,account,to,amount):

    raw_tx = create_tx(coin,account,to,amount)

    if coin == ETH:
        signed=account.sign_transaction(raw_tx)
        return web3.eth.sendRawTransaction(signed.raw_tx)

    if coin == BTCTEST:
        signed=account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

    



#derive_wallets(mnemonic, ETH, 3)
#coins()

coins()[ETH][0]['privkey']

btctestacct = priv_key_to_account(BTCTEST,coins()[BTCTEST][0]['privkey'])
btctestrecipient = coins()[BTCTEST][2]['address']
btctest_key_sender = wif_to_key('cMhb1GJJ95LXvafmaJujWCsdRbtRe8Jeoxe5iymi2mbSz9BNCJeZ')
btctest_key_recipient = wif_to_key('cSMtsujGchCPDto1pBrLeWPdf9LtfPiGZKD7CfcgRZWBQpiSkptq')


print()
print()
print(f'Test Sender {btctestacct}')
print(f'Test Recipient {btctestrecipient}')
print()
print(f'Current Balance Sender: {btctest_key_sender.get_balance(BTC)}')
print(f'Current Balance Recipient: {btctest_key_recipient.get_balance(BTC)}')
print()
print("Sending .001 btc from sender to recipient")
send_tx(BTCTEST,btctestacct, btctestrecipient, .001)
print("Sleeping for 10 seconds to allow blockchain mining of transaction")
time.sleep(10)
print()
print(f'New Balance Sender: {btctest_key_sender.get_balance(BTC)}')
print(f'New Balance Recipient: {btctest_key_recipient.get_balance(BTC)}')
