from unicodedata import decimal
import os
import json
from brownie import accounts, network, config, web3

# FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
# new comment
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
TESTNET_ENVIRONMENTS = ["goerli"]

token_dict = {"dai": "DAI_ABI.json"}


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")

    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
            or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_contract_address(contractName):
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return config["networks"][network.show_active()][contractName]
    if network.show_active() in TESTNET_ENVIRONMENTS:
        return config["networks"][network.show_active()][contractName]
    else:
        return None


def get_ABI(token_name):
    token = token_dict[token_name]
    f = open(os.path.join(os.getcwd(), "ABI", network.show_active(), token))
    ABI = json.load(f)
    return ABI


def printParameters(token1, token2, AMOUNT_IN):
    print("\n" + "Swap Parameters:" + "\n" + "Token In: " + token1 + "\n" +
          "Token Out: " + token2 + "\n" + "Amount In: " +
          str(web3.fromWei(AMOUNT_IN, "ether")) + "\n")
