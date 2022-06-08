from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.05, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork", "kovan"]:
        get_weth(amount)
    # get the aave ABI and contract
    lending_pool = get_lending_pool()
    # Approve sending our ERC20 tokens
    approve_erc20(lending_pool.address, amount, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposited!")
    # how much can we borrow for our deposited WETH, now?
    (availableBorrowsETH, totalDebtETH) = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (
        availableBorrowsETH * 0.5
    )  # converting to ETH/DAI price and multiplying by the 50 % of the maximum borrowable amount
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Next step: borrowing
    borrow_tx = lending_pool.borrow(
        config["networks"][network.show_active()]["dai_token"],
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    (availableBorrowsETH, totalDebtETH) = get_borrowable_data(lending_pool, account)
    # Next repay what I have borrowed
    repay_all(
        Web3.toWei(amount_dai_to_borrow, "ether"),
        lending_pool,
        account,
        config["networks"][network.show_active()]["dai_token"],
    )
    print("Everything has been repaid!")
    get_borrowable_data(lending_pool, account)


def repay_all(amount, lending_pool, account, asset):
    approve_erc20(lending_pool, Web3.toWei(amount, "ether"), asset, account)
    repay_tx = lending_pool.repay(asset, amount, 1, account.address, {"from": account})
    repay_tx.wait(1)


def get_asset_price(price_feed_address):
    # ABI
    # Contract address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    dai_eth_price = dai_eth_price_feed.latestRoundData()[1]
    converted_dai_eth_price = Web3.fromWei(dai_eth_price, "ether")
    print(f"DAI/ETH price: {converted_dai_eth_price}")
    return float(converted_dai_eth_price)


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account.address)
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"You have {totalCollateralETH} worth of ETH deposited.")
    print(f"You have {totalDebtETH} worth of ETH borrowed.")
    print(f"You can borrow {availableBorrowsETH} worth of ETH.")
    return (float(availableBorrowsETH), float(totalDebtETH))


def approve_erc20(spender, amount, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx


def get_lending_pool():
    # ABI: getting this from the interface, since the interface is just telling how we can interact with the contract
    # Address from https://docs.aave.com/developers/v/2.0/deployed-contracts/deployed-contracts
    # the address is stored in the brownie-config.yaml
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
