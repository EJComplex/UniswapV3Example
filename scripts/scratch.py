import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import openpyxl

wb = openpyxl.load_workbook(r"./output/SingleSwapTesting.xlsx")
dai_usdc = ["dai_usdc_3000", "dai_usdc_500", "dai_usdc_100"]
dai_weth = ["dai_weth_3000", "dai_weth_500", "dai_weth_100"]

fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
for sheet in dai_usdc:
    df = pd.read_excel(r"./output/SingleSwapTesting.xlsx", sheet_name=sheet)

    fig.add_trace(
        go.Scatter(
            x=df["amountIn"],
            y=df["impliedTokenOutValue"],
            line=dict(width=2),
            name="Pool Fee " + str(int(sheet.split("_")[2]) * 10**-4) + "%",
            connectgaps=True,
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title="DAI-USDC UniswapV3 Pool Fee Comparison",
        xaxis_title="Dai Quantity In",
        yaxis_title="Implied USDC Value ($)",
    )

    fig.write_html(r"./output/dai_usdc.html")
    fig.write_image(r"./output/dai_usdc.png")

fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
for sheet in dai_weth:
    df = pd.read_excel(r"./output/SingleSwapTesting.xlsx", sheet_name=sheet)

    fig.add_trace(
        go.Scatter(
            x=df["amountIn"],
            y=df["impliedTokenOutValue"],
            line=dict(width=2),
            name="Pool Fee " + str(int(sheet.split("_")[2]) * 10**-4) + "%",
            connectgaps=True,
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title="DAI-WETH UniswapV3 Pool Fee Comparison",
        xaxis_title="Dai Quantity In",
        yaxis_title="Implied Weth Value($)",
    )

    fig.write_html(r"./output/dai_weth.html")
    fig.write_image(r"./output/dai_weth.png")

# for sheet in wb.sheetnames:

#     df = pd.read_excel(r"./output/SingleSwapTesting.xlsx", sheet_name=sheet)
#     fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

#     fig.add_trace(
#         go.Scatter(
#             x=df["amountIn"],
#             y=df["amountOut"],
#             line=dict(color="blue", width=2),
#             name=sheet,
#             connectgaps=True,
#         ),
#         secondary_y=False,
#     )

#     fig.add_trace(
#         go.Scatter(
#             x=df["amountIn"],
#             y=df["impliedTokenOutValue"],
#             line=dict(color="red", width=2),
#             name="Implied Value",
#             connectgaps=True,
#         ),
#         secondary_y=True,
#     )

#     # fig.add_trace(go.Scatter(x = df["rex"], y = [0.38]*len(df),line=dict(color='orange', width=2,dash='dash'), name = "Optimal OEE", connectgaps=True ),secondary_y=False)

#     # fig.update_traces(marker=dict(size=3,))
#     fig.update_layout(
#         title="Effects of Uniswap Pool Fee Selection",
#         xaxis_title=sheet + " Quantity In",
#         yaxis_title=sheet + " Quantity Out",
#     )
#     y_title = "tokenIn/tokenOut"
#     # fig.update_layout(yaxis_title=dict(text=y_title,font=dict(color='#FF5000',size=16,family="Source Sans Pro")),secondary_y=True)
#     fig.update_yaxes(title_text=y_title, secondary_y=True)

#     # fig = FormatDisplay(fig,"St Mary's AHU Heating Valve % vs Outside Air Temp","OAT Degrees F","Valve %")
#     # fig = FormatDisplay(fig,"OEE per Master Rex", "Master Rex", "OEE", "Quantity [Gallons]")

#     fig.write_html(r"./output/" + sheet + ".html")
