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

# Deploy swap contract
def deploy(contract, swapRouter):
    account = get_account(index=-2)
    swapContract = contract.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


# Perform swap
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
def multiSwap(swapContract, tokenIn, tokenMid, tokenOut, amountIn):
    account = get_account(index=-2)
    tx = swapContract.swapExactInputMultihop(
        tokenIn, tokenMid, tokenOut, amountIn, {"from": account}
    )
    tx.wait(1)
    return tx


# Approve token
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


def singleTest(_tokenIn, _tokenOut, _unitsIn, _unitsOut, _poolFee):
    # Select account
    account = get_account(index=-2)

    swapRouter = config["networks"][network.show_active()]["uniswap_router_v3"]
    swapContract = deploy(UniswapV3Swap, swapRouter)

    # define inputs
    print(_tokenOut)
    tokenOut = config["networks"][network.show_active()][_tokenOut]
    tokenIn = config["networks"][network.show_active()][_tokenIn]
    unitsOut = _unitsOut
    unitsIn = _unitsIn
    poolFee = _poolFee

    # Get pool
    factory = config["networks"][network.show_active()]["uniswap_factory_v3"]
    pool = interface.IUniswapV3Factory(factory).getPool(tokenIn, tokenOut, poolFee)

    # Call approve token function
    max_amount = Web3.toWei(2**64 - 1, "ether")
    approveToken(tokenIn, swapContract.address, max_amount)

    # Call swap function
    token_contract = interface.IERC20(tokenOut)
    outputList = []
    inputList = []
    inputReverseList = []
    outputReverseList = []
    starting_balance = float(
        Web3.fromWei(token_contract.balanceOf(account.address), unitsOut)
    )
    starting_balance_reverse = float(
        Web3.fromWei(token_contract.balanceOf(account.address), unitsIn)
    )
    for i in range(1, 11):
        amountIn = i * Web3.toWei(100, unitsIn)
        # amountIn = 100692897436421072274

        tx = singleSwap(swapContract, tokenIn, tokenOut, amountIn, poolFee)
        outputList.append(
            float(Web3.fromWei(token_contract.balanceOf(account.address), unitsOut))
            - starting_balance
        )

        inputList.append(amountIn)

        tx_reverse = singleSwap(
            swapContract, tokenOut, tokenIn, outputList[-1], poolFee
        )

        outputReverseList.append(
            float(Web3.fromWei(token_contract.balanceOf(account.address), unitsIn))
            - starting_balance_reverse
        )

        inputReverseList.append(outputList[-1])

    df = pd.DataFrame()
    df["amountIn"] = inputList.copy()
    df["amountOut"] = outputList.copy()
    df["amountInReverse"] = inputReverseList.copy()
    df["amountOutReverse"] = outputReverseList.copy()
    df["pool" + _tokenIn + "-" + _tokenOut] = [str(pool)] * len(df)

    return df.copy()


def transferToken(token, contractAddress, amount):
    account = get_account(index=-2)
    tx = interface.IERC20(token).transfer(contractAddress, amount, {"from": account})
    tx.wait(1)
    return tx


def main():
    # Deploy swap contract
    # based on config file swap selected tokens
    # record pool address
    # record implied usdc value after each swap
    # create dataframe with this info
    # create plot to display pool imbalances

    swapConfig = pd.read_csv(r"config/single_swap_config.csv")

    for row in swapConfig.iterrows():
        outputdf = singleTest(
            row[1],
            row[2],
            row[3],
            row[4],
            row[0],
        )

    # for row in swapConfig.index:
    #     outputdf = singleTest(
    #         swapConfig.loc[row, ["Token In"]],
    #         swapConfig.loc[row, ["Token Out"]],
    #         swapConfig.loc[row, ["Token In Units"]],
    #         swapConfig.loc[row, ["Token Out Units"]],
    #         swapConfig.loc[row, ["Pool Fee"]],
    #     )

    outputdf.to_csv(r"output\SingleSwapTesting.csv")
