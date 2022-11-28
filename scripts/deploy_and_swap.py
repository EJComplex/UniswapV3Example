from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_ABI,
    printParameters,
    approve,
)
from brownie import UniswapV3Swap, web3, interface, config

import time
from web3 import Web3


def deploy(swapRouter):
    account = get_account()
    swapContract = UniswapV3Swap.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


def main():
    account = get_account()
    swapRouter = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    swapContract = deploy(swapRouter)
    DAI = interface.IERC20("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    # print(config["wallets"]["from_key"])
    approve(DAI, swapContract.address, account.address, config["wallets"]["from_key"])
