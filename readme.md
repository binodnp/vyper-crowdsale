# Vyper Crowdsale Contracts

Welcome to Vyper Crowdsale contracts.

You will find several Vyper crowdsale contract implementations in this project. We've also ported some Open Zeppelin tests with minimum changes.

## Before You Clone This Repository ...

This project requires the the following dependencies to be present before you can actually start developing and contributing to this repository.

**Prerequisites**

- Python3
- NodeJS
- Truffle
- Ganache

Since Vyper compiler is a beta software, there could be some breaking changes in the future. We, therefore, strongly encourage you to keep a close eye on [the official Vyper documentation](https://vyper.readthedocs.io/en/v0.1.0-beta.5/installing-vyper.html) if things go south.

## Setting up the Development Environment

**Clone the Project**

Since you've already installed the dependencies, you can now clone the project from GitHub.

```bash
cd path/to/a/desired/directory
git clone http://github.com/binodnp/vyper-crowdsale
cd vyper-crowdsale
```

**Create a Virtual Environment**
```bash
virtualenv -p python3 --no-site-packages env
source env/bin/activate
```


**Clone and Make Vyper**

```bash
git clone https://github.com/ethereum/vyper.git
cd vyper
make
make test
```  

If you see some error messages here, you might have missed to activate the virtual environment. Type:

```bash
source env/bin/activate
```



**Restore NPM Packages**

NPM is needed to write and run truffle tests (in JavaScript of course).
```bash
npm install
```

## How to's?

**How to Run Vyper to Build a Contract?**

On the project root, type the following in the terminal:

```bash
vyper ./contracts/crowdsale.v.py
```

The above command will compile the burnable token contract.

**What does Truper Actually Do?**

Instead of using *Vyper*, you could use **truper** to compile contracts and generate the build outputs to the `build` directory. This helps you write, run, and migrate **truffle tests** in JavaScript.

> Note that for truper to work properly, Vyper contract files must end with `.v.py` file extension(s). Also note that truper will generate the build artifacts (files) to have `.vyper.json` extension.

Open the terminal panel and type `truper` to build contracts.

**Truffle Tests**

Open the terminal panel and type `truffle test` to see the test results.

> Please note that you would need to first compile the contracts using the command `truper` before you can run your tests. 

**Contracts**
- Crowdsale
- Individually Capped Crowdsale

**License**

Apache 2.0

**Additional Links**

- [Vyper Documentation](https://vyper.readthedocs.io/en/v0.1.0-beta.5/installing-vyper.html)
- [Vyper ERC20 Contracts](http://github.com/binodnp/vyper-erc20)
- [Vyper ERC721 Non Fungible Tokens](https://github.com/maurelian/erc721-vyper)
- [Truper Repository](https://github.com/maurelian/truper)
- [Online Vyper Compiler](http://vyper.online/)
- [Open Zeppelin Solidity](https://github.com/OpenZeppelin/openzeppelin-solidity)
- [Truffle Suite of Tools](https://truffleframework.com)
