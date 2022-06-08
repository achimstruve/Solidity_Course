from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def get_weth(amount):
    """
    Mint WETH by depositing ETH
    """
    # ABI: We get the ABI through the imported interface (IWeth.sol)
    # from https://github.com/PatrickAlphaC/aave_brownie_py/blob/main/interfaces/WethInterface.sol

    # Address WETH (google: weth <network> etherscan | for the kovan network google: weth kovan etherscan
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": amount})
    tx.wait(1)
    print(f"Received {amount} WETH")
    return tx


def get_eth_from_weth_back(amount):
    """
    Mint WETH by depositing ETH
    """
    # ABI: We get the ABI through the imported interface (IWeth.sol)
    # from https://github.com/PatrickAlphaC/aave_brownie_py/blob/main/interfaces/WethInterface.sol

    # Address WETH (google: weth <network> etherscan | for the kovan network google: weth kovan etherscan
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(amount * 10**18, {"from": account})
    tx.wait(1)
    print(f"Received {amount} ETH")
    return tx


def main():
    get_weth(0.05)
    # get_eth_from_weth_back(0.05)
