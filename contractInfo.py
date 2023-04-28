from solcx import compile_standard, install_solc
import json

with open("./ChequePayment.sol", "r") as file:
    chequepayment_file = file.read()

install_solc(version="0.8.18")

compiled_file = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ChequePayment.sol": {"content": chequepayment_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.18",
)

# print(compiled_file)

with open("compiled_contract.json", "w") as file:
    json.dump(compiled_file, file)

# Retrieve the bytecode
bytecode = compiled_file["contracts"]["ChequePayment.sol"]["ChequePayment"]["evm"]["bytecode"]["object"]

# Retrieve the abi
abi = compiled_file["contracts"]["ChequePayment.sol"]["ChequePayment"]["abi"]

# print(bytecode)
# print(abi)

GANACHE_CHAIN_ID = 1337
ALFAJORES_CHAIN_ID = 44787