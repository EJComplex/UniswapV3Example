from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_ABI,
    printParameters,
    approve,
)
from brownie import UniswapV3Swap, web3, interface, config, chain, history, accounts

import time
from web3 import Web3


def deploy(swapRouter):
    # account = get_account()
    account = accounts[-1]
    swapContract = UniswapV3Swap.deploy(swapRouter, {"from": account})
    time.sleep(1)
    # print(swapContract.tx.info())
    return swapContract


def swap(swapContract, amountIn):
    account = accounts[-1]
    tx = swapContract.swapExactInputSingle(amountIn, {"from": account})
    tx.wait(1)
    # print(tx.info())


def main():
    # account = get_account()
    # for acc in accounts:
    #    print(acc)
    account = accounts[-1]

    swapRouter = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    swapContract = deploy(swapRouter)
    DAI = interface.IERC20("0x6B175474E89094C44Da98b954EedeAC495271d0F")
    # print(config["wallets"]["from_key"])
    # These transactions are signed by the testpass private key, not account
    # tx = approve(DAI, swapRouter, account.address, config["wallets"]["from_key"])
    # tx = approve(DAI, swapContract, account.address, config["wallets"]["from_key"])
    # print(tx.info())
    # print(DAI.balanceOf(account.address))
    amountIn = 665692897436421072274
    # DAI.Approval(account.address,swapRouter.address, amountIn)
    DAI.approve(swapContract.address, amountIn, {"from": account})
    print(Web3.fromWei(DAI.balanceOf(account.address), "ether"))
    swap(swapContract, amountIn)
    print(Web3.fromWei(DAI.balanceOf(account.address), "ether"))
    print(Web3.fromWei(account.balance(), "ether"))
