// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@uniswapv2/contracts/interfaces/IWETH.sol";
import "@uniswapv2/contracts/interfaces/IUniswapV2Router02.sol";

//To swap ETH for token
//ETH is wrapped
//WETH is approved
//Tokens swapped
contract UniswapV2Swap is Ownable {
    address public UNISWAP_V2_ROUTER;
    
    constructor(address _swapRouter) {
        UNISWAP_V2_ROUTER = _swapRouter;
    }

    function swap(address _tokenIn, address _tokenOut, uint256 _amountIn, uint256 _amountOutMin, address _to) external payable {
        
        
        
        address [] memory path;
        path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;

        IERC20(_tokenIn).approve(UNISWAP_V2_ROUTER,_amountIn);
        IUniswapV2Router02(UNISWAP_V2_ROUTER).swapExactTokensForTokensSupportingFeeOnTransferTokens( _amountIn, _amountOutMin, path, _to, block.timestamp);
    }

    
}
