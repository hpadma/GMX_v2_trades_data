# GMX_v2_trades_data
Listen for GMX_v2 trade events of WETH,WBTC,LINK,UNI tokens.

## Installation:
#### 1.To get started, clone the repository
#### 2. To run the project using Docker Compose, execute the following commands:
         sudo docker-compose up --build


## Approach:
1. Go through all the chunks of blocks parallelly using ray.
2. Filter out the required trades from the event logs
3. Then save it into the CSV file.

## Components:
### __main__.py :
  Initiates a ray and listens to the blocks parallely.
### web3_utils.py :
  Creates a Web3 instance using the given HTTP provider URL.
### contract_abi.py :
  Returns the smart contract ABI of GMX_v2.
### event_handler.py :
  Handles the event and returns the data of relavant event in formatted manner.
### trades_handler.py :
  Updates the position link and writes the trade data to the CSV file.

