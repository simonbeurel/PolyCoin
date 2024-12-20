# PolyCoin
## Team members:
- BEUREL Simon 
- DUMANOIS Arnaud 
- LIQUORI Luigi

## Description
The PolyCoin project is the result of a 6-month research work carried out by Simon BEUREL and Arnaud DUMANOIS on the subject presented by Mr Liquori LUIGI: (Semi)Decentralized Digital Currencies and Mutable Smart Contracts for Permissioned Blockchains Distributed Ledgers for the European Area.

The goal of this project is to propose a blockchain allowing to permanently monitor the evolution of ethereum smart contracts published by different companies. Thanks to this project, it is also possible to find the different managers of a smart contract thanks to the cryptographic signature mechanism.

If you need more details, you can find the state of the art carried out at the beginning of this project here: [State of the art](doc/Etat_de_lart_DUMANOIS_BEUREL.pdf)


## Blockchain's architecture 
This blockchain is made up of two types of blocks with their own characteristics.

The first type of block is called the "IDENTIFIER" block. This block allows you to reference a legal/physical entity within the blockchain such as a company, an independent developer, a government agency, etc. This block has several mandatory attributes such as:
- A unique name
- A digital certificate issued by a certification authority
- An Ethereum address

The second type of block is called the "CODE" block. This block allows you to reference a smart contract intended to be deployed on the Ethereum blockchain. This block has several mandatory attributes such as:
- The source code of the contract (.sol file)
- The cryptographic signatures of each "IDENTIFIER" entity that took part in the creation of this block

## Programming aspects

This project was developed using Python 3.10 technology. The different libraries used are indicated in the requirements.txt file

To install the libraries:
```shell
pip3 install -r requirements.txt
```

To launch the project:
```shell
python3 app.py
```
