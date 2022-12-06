from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_ABI,
    printParameters,
    approve,
)
from brownie import UniswapV3Swap, interface, accounts, network, config

import time
from web3 import Web3


def printTxInfo(func):
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)

        if type(result) == network.contract.ProjectContract:
            print(result.tx.info())

        if type(result) == network.transaction.TransactionReceipt:
            print(result.info())

        return result

    return wrap


def balanceIs(account, token=None):
    def balanceIsInner(func):
        def wrap(*args, **kwargs):
            if not token:
                print(Web3.fromWei(account.balance(), "ether"))
            if token:
                token_address = config["networks"][network.show_active()][token]
                token_contract = interface.IERC20(token_address)
                print(
                    f"{token} balance is {Web3.fromWei(token_contract.balanceOf(account.address), 'ether')}"
                )

            result = func(*args, **kwargs)

            if not token:
                print(Web3.fromWei(account.balance(), "ether"))
            if token:
                token_address = config["networks"][network.show_active()][token]
                token_contract = interface.IERC20(token_address)
                print(
                    f"{token} balance is {Web3.fromWei(token_contract.balanceOf(account.address), 'ether')}"
                )

            return result

        return wrap

    return balanceIsInner


# @printTxInfo
def deploy(swapRouter):
    account = get_account(index=-2)
    swapContract = UniswapV3Swap.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


# @printTxInfo
@balanceIs(get_account(index=-2), token="dai")
@balanceIs(get_account(index=-2), token="weth")
def swap(swapContract, amountIn):
    account = get_account(index=-2)
    tx = swapContract.swapExactInputSingle(amountIn, {"from": account})
    tx.wait(1)
    return tx


# @printTxInfo
def approveToken(tokenAddress, approveAddress, amount):
    account = get_account(index=-2)
    token = interface.IERC20(tokenAddress)
    tx = token.approve(approveAddress, amount, {"from": account})
    return tx


def main():
    account = get_account(index=-2)

    swapRouter = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    swapContract = deploy(swapRouter)

    DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    amountIn = 665692897436421072274
    approveToken(DAI, swapContract.address, amountIn)

    swap(swapContract, amountIn)
