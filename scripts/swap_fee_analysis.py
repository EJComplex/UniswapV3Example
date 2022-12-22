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
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Decorator to print balance before and after transaction.
# ETH by default, token if given.
def balanceIs(account, token=None, units="ether"):
    def balanceIsInner(func):
        def wrap(*args, **kwargs):
            if not token:
                print(Web3.fromWei(account.balance(), units))
            if token:
                token_address = config["networks"][network.show_active()][token]
                token_contract = interface.IERC20(token_address)
                print(
                    f"{token} balance is {Web3.fromWei(token_contract.balanceOf(account.address), units)}"
                )

            result = func(*args, **kwargs)

            if not token:
                print(Web3.fromWei(account.balance(), units))
            if token:
                token_address = config["networks"][network.show_active()][token]
                token_contract = interface.IERC20(token_address)
                print(
                    f"{token} balance is {Web3.fromWei(token_contract.balanceOf(account.address), units)}"
                )

            return result

        return wrap

    return balanceIsInner


# Deploy swap contract
def deploy(contract, swapRouter):
    account = get_account(index=-2)
    swapContract = contract.deploy(swapRouter, {"from": account})
    time.sleep(1)
    return swapContract


# Perform swap
@balanceIs(get_account(index=-2), token="dai")
@balanceIs(get_account(index=-2), token="usdc", units="mwei")
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
    # print(_tokenOut)
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
    approveToken(tokenOut, swapContract.address, max_amount)

    # Call swap function
    token_contract_out = interface.IERC20(tokenOut)
    token_contract_in = interface.IERC20(tokenIn)
    outputList = []
    inputList = []
    inputReverseList = []
    outputReverseList = []
    starting_balance = float(
        Web3.fromWei(token_contract_out.balanceOf(account.address), unitsOut)
    )

    for i in range(1, 21):
        amountIn = i * Web3.toWei(100, unitsIn)
        # amountIn = 100692897436421072274

        print(
            "Swapping "
            + str(Web3.fromWei(amountIn, unitsIn))
            + " "
            + _tokenIn
            + " for "
            + _tokenOut
        )
        tx = singleSwap(swapContract, tokenIn, tokenOut, amountIn, poolFee)
        outputList.append(
            float(Web3.fromWei(token_contract_out.balanceOf(account.address), unitsOut))
            - starting_balance
        )

        inputList.append(Web3.fromWei(amountIn, unitsIn))

        print("Swapping " + str(outputList[-1]) + " " + _tokenOut + " for " + _tokenIn)
        starting_balance_reverse = float(
            Web3.fromWei(token_contract_in.balanceOf(account.address), unitsIn)
        )
        tx_reverse = singleSwap(
            swapContract,
            tokenOut,
            tokenIn,
            Web3.toWei(outputList[-1], unitsOut),
            poolFee,
        )

        outputReverseList.append(
            float(Web3.fromWei(token_contract_in.balanceOf(account.address), unitsIn))
            - starting_balance_reverse
        )

        inputReverseList.append(outputList[-1])

    df = pd.DataFrame()
    df["amountIn"] = inputList.copy()
    df["amountOut"] = outputList.copy()
    df["amountInReverse"] = inputReverseList.copy()
    df["amountOutReverse"] = outputReverseList.copy()
    df["impliedTokenOutValue"] = df["amountIn"].astype(float) / df["amountOut"].astype(
        float
    )
    df["pool " + _tokenIn + "-" + _tokenOut] = [str(pool)] * len(df)

    return df.copy()


def transferToken(token, contractAddress, amount):
    account = get_account(index=-2)
    tx = interface.IERC20(token).transfer(contractAddress, amount, {"from": account})
    tx.wait(1)
    return tx


def ToExcel(Dict: dict, path: str, file: str):
    with pd.ExcelWriter(os.path.join(path, file)) as writer:
        for key, df in Dict.items():
            df.to_excel(writer, sheet_name=key)


def main():
    # Deploy swap contract
    # based on config file swap selected tokens
    # record pool address
    # record implied usdc value after each swap
    # create dataframe with this info
    # create plot to display pool imbalances

    # Add some Weth to account for slippage
    account = get_account(index=-2)
    value = Web3.toWei(1, "ether")
    tx = interface.IWETH9(config["networks"][network.show_active()]["weth"]).deposit(
        {"from": account, "value": value}
    )

    swapConfig = pd.read_csv(r"config/single_swap_config.csv")

    outputDict = {}
    for index, row in swapConfig.iterrows():
        outputdf = singleTest(
            row["Token In"],
            row["Token Out"],
            row["Token In Units"],
            row["Token Out Units"],
            row["Pool Fee"],
        )
        outputDict[
            row["Token In"] + "_" + row["Token Out"] + "_" + str(row["Pool Fee"])
        ] = outputdf.copy()

    # Save output to excel
    ToExcel(outputDict, r"./output/", "SingleSwapTesting.xlsx")
