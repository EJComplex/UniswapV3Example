import pandas as pd


swapConfig = pd.read_csv(r"config/single_swap_config.csv")


print(swapConfig)
for row in swapConfig.iterrows():
    print(row)


# for row in swapConfig.index:
#     outputdf = singleTest(
#         swapConfig.loc[row, ["Token In"]],
#         swapConfig.loc[row, ["Token Out"]],
#         swapConfig.loc[row, ["Token In Units"]],
#         swapConfig.loc[row, ["Token Out Units"]],
#         swapConfig.loc[row, ["Pool Fee"]],
#     )

# outputdf.to_csv(r"output\SingleSwapTesting.csv")
