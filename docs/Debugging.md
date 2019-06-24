# Debugging

Some debugging notes.

## Blockchain
### Events
Events are identified by their definition sha3 signature:
```
>>> events = [
...     b'LogBet(bytes32,address,uint256,uint256,uint256,uint256)',
...     b'LogResult(uint256,bytes32,address,uint256,uint256,uint256,int256,bytes32,uint256)',
...     b'LogRefund(bytes32,address,uint256)',
...     b'LogOwnerTransfer(address,uint256)']
>>> [(keccak(event).hex(), event) for event in events]
... {
... '1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4':
...     b'LogBet(bytes32,address,uint256,uint256,uint256,uint256)',
... '42c501a185f41a8eb77b0a3e7b72a6435ea7aa752f8a1a0a13ca4628495eca91':
...     b'LogOwnerTransfer(address,uint256)',
... '7b6ccf85690b8ce1b7d21a94ca738803a9da7dc74e10140f269efa0d8d6fb851':
...     b'LogRefund(bytes32,address,uint256)',
... 'e9a8d2e9fb2b29de7ef1f9a2e48c217246d46cedcb96ebd5601083b0c1203bc8':
...     b'LogResult(uint256,bytes32,address,uint256,uint256,uint256,int256,bytes32,uint256)'}
```
Use this signature to match the "topic" from Etherscan.

Let's decode LogBet from Etherscan result, keep in mind `LogBet` method definition:
```
event LogBet(bytes32 indexed BetID, address indexed PlayerAddress, uint indexed RewardValue, uint ProfitValue, uint BetValue, uint PlayerNumber)
```
Let's use it to decode the [following transaction](https://etherscan.io/tx/0xd63a4e50dce5232eba4b77b4f9a5fd5d4322633036fe0c015e51ed24dfc2c451#eventlog):
```
Address 0xddf0d0b9914d530e0b743808249d9af901f1bd01
Topics
[0] 0x1cb5bfc4e69cbacf65c8e05bdb84d7a327bd6bb4c034ff82359aefd7443775c4 <- "LogBet" topic signature
[1] 0xb4fd1bd4b0a330a00f1d809c9a29c9aa2bba49e7af45dee70852e1e7e2eed543 <- `BetID`
[2] 0x000000000000000000000000070ba449dba610303f928e35fd6c16c54b25d37a <- `PlayerAddress`
[3] 0x0000000000000000000000000000000000000000000000004fafae93dc4b0000 <- `RewardValue`
Data (Hex)
0000000000000000000000000000000000000000000000002770cff143a90000 <- `ProfitValue` (2842000000000000000 Wei)
000000000000000000000000000000000000000000000000283edea298a20000 <- `BetValue` (2900000000000000000 Wei)
0000000000000000000000000000000000000000000000000000000000000033 <- `PlayerNumber`
```

### Online tool
https://lab.miguelmota.com/ethereum-input-data-decoder/example/

## Android
```
buildozer android adb -- logcat
```
or with filtering:
```
buildozer android adb -- logcat 2>&1 | grep -E '(I python|I service|F DEBUG)'
```
