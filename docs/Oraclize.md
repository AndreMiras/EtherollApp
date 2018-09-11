# Oraclize notes

Some note taking about how Etheroll random number are being generated, plus Oraclize tips and tricks.


## random.org
It's using `generateSignedIntegers` method from random.org.
First go to [random.org Request Builder](https://api.random.org/json-rpc/1/request-builder) to give it a try.
To make the request looks like the one Etheroll is using, we need to set a couple of things.
1. in the "API Method" dropdown select "generateSignedIntegers"
2. set "n" to "1"
3. set "max" to "100"

We can leave the default value on the other fields. At the end the "Request Body" should look like this:
```javascript
{"jsonrpc":"2.0","method":"generateSignedIntegers","params":{"apiKey":"00000000-0000-0000-0000-000000000000","n":1,"min":1,"max":100,"replacement":true,"base":10},"id":15234}
```
After clicking "Send Request", the response ("Response Body") should look like this:
```javascript
{"jsonrpc":"2.0","result":{"random":{"method":"generateSignedIntegers","hashedApiKey":"oT3AdLMVZKajz0pgW/8Z+t5sGZkqQSOnAi1aB8Li0tXgWf8LolrgdQ1wn9sKx1ehxhUZmhwUIpAtM8QeRbn51Q==","n":1,"min":1,"max":100,"replacement":true,"base":10,"data":[42],"completionTime":"2018-08-04 10:04:12Z","serialNumber":31337},"signature":"3BQWz+YS7nUkAzfmWeba+S9hzYsTceuPSFKqt45tJ3v3F0I5XJmq6Z2Fxyz3/iRXkJrbI+51IDU8FRnufgbAkbgGW4ZHef5cBMDm2wbhU4d26K8Z28L2AiTE13CN4xuFQL+BencG0bJkjnwjKhZqVzUPyxIsGVaukQnslUBkDsZCX1CIlGsEiN+AHIcUtKi0owCq24KaWS/4bu16nYDNm8oRjZ74ibPqmnFhFQX8CTtEcn6YTRv0aeSe+fjYUBYgyJZshVOXzlmdIxBfb3Iy58yOlIxES7WofZFj7GWIX4LRva+4bHsncxeZXQh8eChcoMvLToBNi0LIxpittfMWY3b37MtVdbh+NejciBjg2oFGLxE80rwBjdxeYzwCZnw1uQFK3PZhzO6aVp/2oxKgzZgk2eg9aJjq+ns63pnV+ohvNftuftvFI6UCpZQ7wip9dgz5PLoAMxxCpHmk4ynSZ04Jk0XPAtTkFmUwLLxlL6J8VaS1NoIzBW6NaG0wSw6d6qL2BuIVHol7QBcdejZxUNGWbHOz1W60C40ebDg7IP9SCpKwjpyp5ZqUEUs7Dn3rwW8oadP6OnfIgt6BIQTP0oAW31plXSTcytDaGV8wyhMFq31Z8IZXPjVsdT9h1tD1mZiE8RlDs87wTu7+/S+JRftmhzcLoSWNI2lYdxHtRE8=","bitsUsed":7,"bitsLeft":1918697,"requestsLeft":396391,"advisoryDelay":840},"id":15234}
```
Etheroll will only use "serialNumber" for debugging and "data" our actual roll result.
So next is to build the same through the oracle to send that request. The response is received via the `__callback()` where the result is parsed in the solidity code.

## Oraclize.it
Now let's integrate that to the oracle. In the similar fashion random.org has a request builder, [Oraclize has a test query tool](http://app.oraclize.it/home/test_query).
For sending request to random.org we're using [nested queries](https://docs.oraclize.it/#data-sources-nested). So on the online test query, we need to select [nested](http://app.oraclize.it/home/test_query#bmVzdGVk:) query type.
So remember we have a payload to send to random.org and we want to keep "serialNumber" and "data", so here is the nested query:
Then we fill the payload with the following:
```javascript
[URL] ['json(https://api.random.org/json-rpc/1/invoke).result.random["serialNumber","data"]', '\n{"jsonrpc":"2.0","method":"generateSignedIntegers","params":{"apiKey":"00000000-0000-0000-0000-000000000000","n":1,"min":1,"max":100,"replacement":true,"base":"10"},"id":"1"}']
```
The response should contain `[serialNumber, [data]]`, e.g.:
```javascript
[31337, [42]]
```

That reponse is later parsed in the `__callback()` method of the Etheroll contract to extract both "serialNumber" and "data".
