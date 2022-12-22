from scripts.helpful_scripts import get_account
from brownie import (
    UniswapV3Swap,
    UniswapV3MultiSwap,
    interface,
    network,
    config,
    UniswapV2Swap,
)

import time
from web3 import Web3
import pandas as pd
import numpy as np

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
def deploy(contract, swapRouter):
    account = get_account(index=-2)
    swapContract = contract.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


# Perform swap
# @printTxInfo
@balanceIs(get_account(index=-2), token="dai")
@balanceIs(get_account(index=-2), token="weth")
def singleSwap(swapContract, tokenIn, tokenOut, amountIn, poolFee):
    account = get_account(index=-2)
    tx = swapContract.swapExactInputSingle(
        tokenIn, tokenOut, amountIn, poolFee, {"from": account}
    )
    tx.wait(1)
    return tx


def singleSwapV2(swapContract, tokenIn, tokenOut, amountIn):
    account = get_account(index=-2)
    tx = swapContract.swap(tokenIn, tokenOut, amountIn, 100, account.address)
    tx.wait(1)
    return tx


# Perform swap
# @printTxInfo
@balanceIs(get_account(index=-2), token="dai")
@balanceIs(get_account(index=-2), token="weth")
def multiSwap(swapContract, tokenIn, tokenMid, tokenOut, amountIn):
    account = get_account(index=-2)
    tx = swapContract.swapExactInputMultihop(
        tokenIn, tokenMid, tokenOut, amountIn, {"from": account}
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


def multiTest():
    # Select account
    account = get_account(index=-2)

    # Define router contract and amountIn
    DAI = config["networks"][network.show_active()]["dai"]
    WETH = config["networks"][network.show_active()]["weth"]
    USDC = config["networks"][network.show_active()]["usdc"]

    swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    swapContract = deploy(UniswapV3MultiSwap, swapRouter)
    # amountIn = 300692897436421072274

    # Call approve token function
    max_amount = Web3.toWei(2**64 - 1, "ether")
    approveToken(DAI, swapContract.address, max_amount)

    # Call swap function
    token_contract = interface.IERC20(WETH)
    outputList = []
    for i in range(1, 11):
        amountIn = i * Web3.toWei(100, "ether")
        # amountIn = 100692897436421072274

        tx = multiSwap(swapContract, DAI, USDC, WETH, amountIn), "ether"
        outputList.append(
            float(Web3.fromWei(token_contract.balanceOf(account.address), "ether"))
        )

    return outputList


def singleTest(_tokenOut, _tokenIn, _unitsOut, _unitsIn, _poolFee):
    # Select account
    account = get_account(index=-2)

    # Define router contract and amountIn
    # DAI = config["networks"][network.show_active()]["dai"]
    # WETH = config["networks"][network.show_active()]["weth"]
    # USDC = config["networks"][network.show_active()]["usdc"]

    swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    swapContract = deploy(UniswapV3Swap, swapRouter)
    # amountIn = 300692897436421072274

    # define inputs
    tokenOut = config["networks"][network.show_active()][_tokenOut]
    tokenIn = config["networks"][network.show_active()][_tokenIn]
    unitsOut = _unitsOut
    unitsIn = _unitsIn
    poolFee = _poolFee

    # Get pool
    # feeList = [3000, 500, 100]
    # for fee in feeList:
    #     # fee = 50
    #     factory = config["networks"][network.show_active()]["uniswap_factory_v3"]
    #     pool = interface.IUniswapV3Factory(factory).getPool(tokenIn, tokenOut, fee)
    #     print("Pool Fee = " + str(fee) + "\n")
    #     print("Pool = " + str(pool))

    # Call approve token function
    max_amount = Web3.toWei(2**64 - 1, "ether")
    approveToken(tokenIn, swapContract.address, max_amount)

    # Call swap function
    token_contract = interface.IERC20(tokenOut)
    outputList = []
    starting_balance = float(
        Web3.fromWei(token_contract.balanceOf(account.address), unitsOut)
    )
    for i in range(1, 11):
        amountIn = i * Web3.toWei(100, unitsIn)
        # amountIn = 100692897436421072274

        tx = singleSwap(swapContract, tokenIn, token_contract, amountIn, poolFee)
        outputList.append(
            float(Web3.fromWei(token_contract.balanceOf(account.address), unitsOut))
            - starting_balance
        )

    return outputList


def transferToken(token, contractAddress, amount):
    account = get_account(index=-2)
    tx = interface.IERC20(token).transfer(contractAddress, amount, {"from": account})
    tx.wait(1)
    return tx


def v2SingleTest():
    # Select account
    account = get_account(index=-2)

    # Define router contract and amountIn
    DAI = config["networks"][network.show_active()]["dai"]
    WETH = config["networks"][network.show_active()]["weth"]
    USDC = config["networks"][network.show_active()]["usdc"]

    swapRouter = config["networks"][network.show_active()]["uniswap_router_v2"]
    swapContract = deploy(UniswapV2Swap, swapRouter)

    max_amount = Web3.toWei(2**64 - 1, "ether")
    approveToken(DAI, swapContract.address, max_amount)

    # Call swap function
    token_contract = interface.IERC20(USDC)
    outputList = []
    starting_balance = float(
        Web3.fromWei(token_contract.balanceOf(account.address), "mwei")
    )
    for i in range(1, 11):
        amountIn = i * Web3.toWei(100, "ether")
        # amountIn = 100692897436421072274
        tx1 = transferToken(DAI, swapContract.address, amountIn)

        tx2 = singleSwapV2(swapContract, DAI, token_contract, amountIn)
        outputList.append(
            float(Web3.fromWei(token_contract.balanceOf(account.address), "mwei"))
            - starting_balance
        )

    return outputList


def main():
    output = singleTest("usdc", "dai", "mwei", "ether", 100)

    # output = v2SingleTest()

    df = pd.DataFrame()
    df["Ether"] = output.copy()
    df.to_csv(r"output\SingleEtherBalances.csv")

    # Select single or multi
    multi = True

    # if multi:
    #     # Select account
    #     account = get_account(index=-2)

    #     # Define router contract and amountIn
    #     DAI = config["networks"][network.show_active()]["dai"]
    #     WETH = config["networks"][network.show_active()]["weth"]
    #     USDC = config["networks"][network.show_active()]["usdc"]

    #     swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    #     swapContract = deploy(UniswapV3MultiSwap, swapRouter)
    #     amountIn = 300692897436421072274

    #     # Call approve token function
    #     approveToken(DAI, swapContract.address, amountIn)

    #     # Call swap function
    #     multiSwap(swapContract, DAI, USDC, WETH, amountIn)
    # else:
    #     # Select account
    #     account = get_account(index=-2)

    #     # Define router contract and amountIn
    #     DAI = config["networks"][network.show_active()]["dai"]
    #     WETH = config["networks"][network.show_active()]["weth"]
    #     USDC = config["networks"][network.show_active()]["usdc"]

    #     swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    #     swapContract = deploy(UniswapV3Swap, swapRouter)
    #     amountIn = 200692897436421072274

    #     # Call approve token function
    #     approveToken(DAI, swapContract.address, amountIn)

    #     # Call swap function
    #     singleSwap(swapContract, DAI, WETH, amountIn)
