# TimedCrowdsale
# Contributors: Binod Nirvan
# This file is released under Apache 2.0 license.
# @dev Crowdsale accepting contributions only within a time frame.
# Ported from Open Zeppelin
# https://github.com/OpenZeppelin
# 
# See https://github.com/OpenZeppelin
# Open Zeppelin tests ported: Crowdsale.test.js


#@dev ERC20/223 Features referenced by this contract
contract TokenContract:
    def transfer(_to: address, _value: uint256) -> bool: modifying

# Event for token purchase logging
# @param _purchaser who paid for the tokens
# @param _beneficiary who got the tokens
# @param _value weis paid for purchase
# @param _amount amount of tokens purchased
TokenPurchase: event({_purchaser: indexed(address), _beneficiary: indexed(address), _value: uint256(wei), _amount: uint256})

#Timed Crowdsale
openingTime: public(timestamp)
closingTime: public(timestamp)

#Crowdsale
# The token being sold
token: public(address)

#Address where funds are collected
wallet: public(address)

# How many token units a buyer gets per wei.
# The rate is the conversion between wei and the smallest and indivisible token unit.
# So, if you are using a rate of 1 with a DetailedERC20 token with 3 decimals called TOK
# 1 wei will give you 1 unit, or 0.001 TOK.
rate: public(uint256)

#Amount of wei raised
weiRaised: public(uint256(wei))

#Timed Crowdsale
@public
@constant
def hasClosed() -> bool:
    """
    @dev Checks whether the period in which the crowdsale is open has already elapsed.
    @return Whether crowdsale period has elapsed
    """

    return block.timestamp > self.closingTime

#Crowdsale
@public
def __init__( _openingTime: timestamp, _closingTime: timestamp, _rate: uint256, _wallet: address, _token: address):
    """
    @dev Initializes this contract
    @param _openingTime Crowdsale opening time
    @param _closingTime Crowdsale closing time    @param _rate Number of token units a buyer gets per wei
    @param _rate Number of token units a buyer gets per wei
    @param _wallet Address where collected funds will be forwarded to
    @param _token Address of the token being sold
    """

    assert _openingTime >= block.timestamp, "The value for opening time cannot be in the past."
    assert _closingTime >= _openingTime, "The closing time cannot be before opening time."
    assert _rate > 0, "Invalid value supplied for the parameter \"_rate\"."
    assert _wallet != ZERO_ADDRESS, "Invalid wallet address."
    assert _token != ZERO_ADDRESS, "Invalid token address."

    self.openingTime = _openingTime
    self.closingTime = _closingTime
    self.rate = _rate
    self.wallet = _wallet
    self.token = _token

@private
@constant
def getTokenAmount(_weiAmount: uint256) -> uint256:
    return _weiAmount * self.rate


@private
def processTransaction(_sender: address, _beneficiary: address, _weiAmount: uint256(wei)):
    #pre validate
    assert _beneficiary != ZERO_ADDRESS, "Invalid address."
    assert _weiAmount != 0, "Invalid amount received."
    assert block.timestamp >= self.openingTime, "Sorry but the crowdsale has not yet begun."
    assert block.timestamp <= self.closingTime, "Sorry but the crowdsale was already concluded."

    #calculate the number of tokens for the Ether contribution.
    tokens: uint256 = self.getTokenAmount(as_unitless_number(_weiAmount))
    
    self.weiRaised += _weiAmount

    #process purchase
    assert TokenContract(self.token).transfer(_beneficiary, tokens), "Could not forward funds due to an unknown error."
    log.TokenPurchase(_sender, _beneficiary, _weiAmount, tokens)

    #forward funds to the receiving wallet address.
    send(self.wallet, _weiAmount)

    #post validate

@public
@payable
def buyTokens(_beneficiary: address):
    self.processTransaction(msg.sender, _beneficiary, msg.value)

@public
@payable
def __default__():
    self.processTransaction(msg.sender, msg.sender, msg.value)
