from web3 import Web3

LOCAL_HTTPPROVIDER_URL = "http://127.0.0.1:8545"

# Celo URI
# ALFAJORES_URL = "wss://alfajores-forno.celo-testnet.org/ws"
ALFAJORES_URL = "https://alfajores-forno.celo-testnet.org"


def setUpProvider():
    # To connncet to Ganache, we will set the HttpsProvider url to http://127.0.0.1 which run on port 8545
    local_provider = Web3.HTTPProvider(LOCAL_HTTPPROVIDER_URL);
    testNet_provider = Web3.HTTPProvider(ALFAJORES_URL)
    result = {"testNet_provider": testNet_provider, "local_provider": local_provider}

    return result

def selectNetwork():
    isTestnet_provider = False
    try:
        selected = int(input("Enter: \n 0 to run in Ganache ... \n 1 on Alfajores ... "))
        if selected == 0:
            isTestnet_provider = isTestnet_provider
        else:
            isTestnet_provider = True
    except ValueError:
        print("ERROR: You need to enter an integer 0 or 1")
    return isTestnet_provider
