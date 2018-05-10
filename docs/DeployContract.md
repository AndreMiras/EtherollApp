# Deploy a contract on the Testnet

This is the instructions to deploy the Etheroll contract on the Testnet.

## Deploy
1. go to [MEW Contract tab](https://www.myetherwallet.com/#contracts)
2. make sure to be on the Testnet (top-right dropdown)
3. copy paste the [contract bytecode](https://etherscan.io/address/0xddf0d0b9914d530e0b743808249d9af901f1bd01#code) (see [Contract ABI and bytecode](#contrat-abi-and-bytecode))
4. "Sign Transaction" and "Deploy Contract"

## Configure
After the smart contract was deployed, we still need to update gas price and treasury address.
See an example with [0x048717ea892f23fb0126f00640e2b18072efd9d2 contract](https://etherscan.io/address/0x048717ea892f23fb0126f00640e2b18072efd9d2) below:
1. [create contract tx](https://etherscan.io/tx/0x647b8c7851e1a560629e121a64d49ea4dc3c72dcca58df5c83a18e1b0140b66d)
2. [ownerSetCallbackGasPrice()](https://etherscan.io/tx/0xbdb4b274c5b0dc0fac3693264092ec014f66ba6825d6091985fbef51cd3b2556)
3. [ownerSetTreasury()](https://etherscan.io/tx/0xca2188db6eb06b3a6a58968ce9962b53f103ed1edd2a893e5edb2f55812a6bed)

## Contract ABI and bytecode
The contract ABI and bytecode can be generated/retrived from both:
 - <https://remix.ethereum.org/>
 - <https://etherscan.io>
