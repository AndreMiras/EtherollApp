# Deploy Etheroll contract

This is the instructions to deploy the Etheroll contract on the Testnet.

## Prepare
1. copy the [source code of the Etheroll contract](https://etherscan.io/address/0x048717ea892f23fb0126f00640e2b18072efd9d2#code)
2. past it to the [online Remix Solidity IDE](https://remix.ethereum.org/#optimize=true&version=soljson-v0.4.18+commit.9cf6e910.js)
3. edit `queryString1` to update ramdom.org `apiKey` with yours, see [random.org API key](#random.org-API-key) below for details

## Compile
1. make sure compiler version matches the contract one and enable optimizations
2. compile and copy object bytecode

## Deploy
1. go to [MEW Contract tab](https://www.myetherwallet.com/#contracts) and select "Deploy Contract"
2. make sure to be on the Testnet (top-right dropdown)
3. paste the contract bytecode you initially copied
4. "Sign Transaction" and "Deploy Contract"

## Configure
After the smart contract was deployed, we still need to make a couple of adjustments.
1. mandatory: top up the bankroll (e.g. 20 ETH) by making a regular transaction from the owner/treasury address
2. optional: set gas price for the Oracle, e.g. [ownerSetCallbackGasPrice()](https://etherscan.io/tx/0xbdb4b274c5b0dc0fac3693264092ec014f66ba6825d6091985fbef51cd3b2556)
3. optional: have a different treasury, e.g.  [ownerSetTreasury()](https://etherscan.io/tx/0xca2188db6eb06b3a6a58968ce9962b53f103ed1edd2a893e5edb2f55812a6bed)

## Also good to know

### random.org API key
It's not possible to use the same encrypted API key as the Etheroll contract one because of the [replay protection](https://docs.oraclize.it/#ethereum-advanced-topics-encrypted-queries).
> In order to prevent other users from using your exact encrypted query ("replay attacks"), the first contract querying Oraclize with a given encrypted query becomes its rightful "owner".
> Any other contract using that exact same string will receive an empty result. As a consequence, remember to always generate a new encrypted string when re-deploying contracts using encrypted queries.

Hence you can either generate your own encrypted one using `encrypted_queries_tools.py` or go for the plain text version of the debug key.
In this case you have to replace the entire nested `${[decrypt] ...}` datasource by your plain API key, e.g. `00000000-0000-0000-0000-000000000000`

### Contract ABI and bytecode
The contract ABI and bytecode can be generated/retrived from both:
 - <https://remix.ethereum.org/>
 - <https://etherscan.io>
