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


def main():
    account = get_account(index=-2)
    pool = config["networks"][network.show_active()]["usdc_dai_pool"]
    poolContract = interface.IUniswapV3PoolState(pool)
    liquidity = poolContract.liquidity()
    # print(Web3.fromWei(liquidity, "ether"))
    slot0 = poolContract.slot0()
    for item in slot0:
        print(item)
