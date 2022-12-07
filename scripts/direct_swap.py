from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_ABI,
    printParameters,
    approve,
)
from brownie import UniswapV3Swap, interface, accounts, network, config, chain

import time
from web3 import Web3


def main():
    # Select unlocked account with DAI
    account = get_account(index=-2)

    # Define swapRouter
    swapRouter = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    swapRouterContract = interface.ISwapRouter(swapRouter)

    # Define swap params
    DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    WETH9 = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    poolFee = 3000
    sender = account.address
    block = chain.time() + 1000
    amountIn = 665692897436421072274

    # Define DAI token and approve
    token = interface.IERC20(DAI)
    tx = token.approve(swapRouter, amountIn, {"from": account})

    # UniswapV3 exactInputSingelSwap
    tx = swapRouterContract.exactInputSingle(
        [
            DAI,
            WETH9,
            poolFee,
            sender,
            block,
            amountIn,
            0,
            0,
        ],
        {"from": account},
    )
    tx.wait(1)
