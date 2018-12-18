# IncreasingPriceCrowdsale
# Contributors: Binod Nirvan
# This file is released under Apache 2.0 license.
# @dev Extension of Crowdsale contract that increases the price of tokens linearly in time.
# Note that what should be provided to the constructor is the initial and final _rates_, that is,
# the amount of tokens per wei contributed. Thus, the initial rate must be greater than the final rate.
# Ported from Open Zeppelin
# https://github.com/OpenZeppelin
# 
# See https://github.com/OpenZeppelin
# Open Zeppelin tests ported: IncreasingPriceCrowdsale.test.js


#@dev ERC20/223 Features referenced by this contract
contract TokenContract:
    def transfer(_to: address, _value: uint256) -> bool: modifying

# Event for token purchase logging
# @param _purchaser who paid for the tokens
# @param _beneficiary who got the tokens
# @param _value weis paid for purchase
# @param _amount amount of tokens purchased
TokenPurchase: event({_purchaser: indexed(address), _beneficiary: indexed(address), _value: uint256(wei), _amount: uint256})

#IncreasingPriceCrowdsale
initialRate: public(uint256)
finalRate: public(uint256)

#Timed Crowdsale
openingTime: public(timestamp)
closingTime: public(timestamp)

#Crowdsale
# The token being sold
token: public(address)

#Address where funds are collected
wallet: public(address)

#Amount of wei raised
weiRaised: public(uint256(wei))


#IncreasingPriceCrowdsale
@public
@constant
def getCurrentRate() -> uint256:
    """
    @dev Returns the rate of tokens per wei at the present time.
    Note that, as price _increases_ with time, the rate _decreases_.
    @return The number of tokens a buyer gets per wei at a given time
    """

    elapsedTime: timedelta = block.timestamp - self.openingTime
    timeRange: timedelta = self.closingTime - self.openingTime
    rateRange: uint256 = self.initialRate - self.finalRate
    return self.initialRate - (elapsedTime * rateRange / timeRange)

#Timed Crowdsale
@public
@constant
def hasClosed() -> bool:
    return block.timestamp > self.closingTime

#Crowdsale
@public
def __init__(_openingTime: timestamp, _closingTime: timestamp, _wallet: address, _token: address, _initialRate: uint256, _finalRate: uint256):
    """
    @dev Constructor, takes initial and final rates of tokens received per wei contributed.
    @param _openingTime Crowdsale opening time
    @param _closingTime Crowdsale closing time
    @param _wallet Address where collected funds will be forwarded to
    @param _token Address of the token being sold
    @param _initialRate Number of tokens a buyer gets per wei at the start of the crowdsale
    @param _finalRate Number of tokens a buyer gets per wei at the end of the crowdsale
    """

    assert _openingTime >= block.timestamp, "The value for opening time cannot be in the past."
    assert _closingTime >= _openingTime, "The closing time cannot be before opening time."
    assert _wallet != ZERO_ADDRESS, "Invalid wallet address."
    assert _token != ZERO_ADDRESS, "Invalid token address."
    assert _initialRate >= _finalRate, "The initial rate must be greater than final rate."
    assert _finalRate > 0, "The final rate "

    self.openingTime = _openingTime
    self.closingTime = _closingTime
    self.wallet = _wallet
    self.token = _token
    self.initialRate = _initialRate
    self.finalRate = _finalRate

@private
@constant
def getTokenAmount(_weiAmount: uint256) -> uint256:
    currentRate: uint256 = self.getCurrentRate()
    return currentRate * _weiAmount

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
