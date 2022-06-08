from brownie import OurToken, accounts
from scripts.helpful_scripts import get_account


def deploy_token():
    init_supply = 1000000 * 10**18
    account = get_account()
    ourToken = OurToken.deploy(init_supply, {"from": account})
    print(ourToken, ourToken.name())


def main():
    deploy_token()
