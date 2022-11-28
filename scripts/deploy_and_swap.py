from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_ABI,
    printParameters,
)
from brownie import UniswapV3Swap, web3
import time
from web3 import Web3


def deploy():
    account = get_account()
    swapContract = UniswapV3Swap.deploy({"from": account})
    time.sleep(1)
    return swapContract


def main():
    deploy()
