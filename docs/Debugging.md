# Debugging

Some debugging notes

## Events
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
