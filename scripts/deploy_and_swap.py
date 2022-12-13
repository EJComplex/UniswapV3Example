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

# Decorator to print tx.info() after transaction
def printTxInfo(func):
    def wrap(*args, **kwargs):
        result = func(*args, **kwargs)

        if type(result) == network.contract.ProjectContract:
            print(result.tx.info())

        if type(result) == network.transaction.TransactionReceipt:
            print(result.info())

        return result

    return wrap


# Decorator to print balance before and after transaction.
# ETH by default, token if given.
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


# Deploy swap contract
# @printTxInfo
def deploy(swapRouter):
    account = get_account(index=-2)
    swapContract = UniswapV3Swap.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


# Perform swap
# @printTxInfo
@balanceIs(get_account(index=-2), token="dai")
@balanceIs(get_account(index=-2), token="weth")
def swap(swapContract, tokenIn, tokenOut, amountIn):
    account = get_account(index=-2)
    tx = swapContract.swapExactInputSingle(
        tokenIn, tokenOut, amountIn, {"from": account}
    )
    tx.wait(1)
    return tx


# Approve token
# @printTxInfo
def approveToken(tokenAddress, approveAddress, amount):
    account = get_account(index=-2)
    token = interface.IERC20(tokenAddress)
    tx = token.approve(approveAddress, amount, {"from": account})
    return tx


def main():
    # Select account
    account = get_account(index=-2)

    # Define router contract and amountIn
    DAI = config["networks"][network.show_active()]["dai"]
    WETH = config["networks"][network.show_active()]["weth"]
    USDC = config["networks"][network.show_active()]["usdc"]

    swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    swapContract = deploy(swapRouter)
    amountIn = 665692897436421072274

    # Call approve token function
    approveToken(DAI, swapContract.address, amountIn)

    # Call swap function
    swap(swapContract, DAI, WETH, amountIn)
