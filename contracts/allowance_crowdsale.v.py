# AllowanceCrowdsale
# Contributors: Binod Nirvan
# This file is released under Apache 2.0 license.
# @dev Extension of Crowdsale where tokens are held by a wallet, which approves an allowance to the crowdsale.
# Ported from Open Zeppelin
# https://github.com/OpenZeppelin
# 
# See https://github.com/OpenZeppelin
# Open Zeppelin tests ported: AllowanceCrowdsale.test.js


#@dev ERC20/223 Features referenced by this contract
contract TokenContract:
    def transferFrom(_from: address, _to: address, _value: uint256) -> bool: modifying
    def allowance(_owner: address, _spender: address) -> uint256: constant
    

# Event for token purchase logging
# @param _purchaser who paid for the tokens
# @param _beneficiary who got the tokens
# @param _value weis paid for purchase
# @param _amount amount of tokens purchased
TokenPurchase: event({_purchaser: indexed(address), _beneficiary: indexed(address), _value: uint256(wei), _amount: uint256})

#AllowanceCrowdsale
tokenWallet: public(address)

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

#AllowanceCrowdsale
@public
@constant
def getRemainingTokens() -> uint256:
    return TokenContract(self.token).allowance(self.tokenWallet, self)

#Crowdsale
@public
def __init__(_rate: uint256, _wallet: address, _token: address, _tokenWallet: address):
    """
    @dev Initializes this contract
    @param _rate Number of token units a buyer gets per wei
    @param _wallet Address where collected funds will be forwarded to
    @param _token Address of the token being sold
    @param _tokenWallet Address holding the tokens, which has approved allowance to the crowdsale
    """

    assert _rate > 0, "Invalid value supplied for the parameter \"_rate\"."
    assert _wallet != ZERO_ADDRESS, "Invalid wallet address."
    assert _token != ZERO_ADDRESS, "Invalid token address."
    assert _tokenWallet != ZERO_ADDRESS, "Invalid token wallet."

    self.rate = _rate
    self.wallet = _wallet
    self.token = _token
    self.tokenWallet = _tokenWallet

@private
@constant
def getTokenAmount(_weiAmount: uint256) -> uint256:
    return _weiAmount * self.rate


@private
def processTransaction(_sender: address, _beneficiary: address, _weiAmount: uint256(wei)):
    #pre validate
    assert _beneficiary != ZERO_ADDRESS, "Invalid address."
    assert _weiAmount != 0, "Invalid amount received."

    #calculate the number of tokens for the Ether contribution.
    tokens: uint256 = self.getTokenAmount(as_unitless_number(_weiAmount))
    
    self.weiRaised += _weiAmount

    #process purchase
    assert TokenContract(self.token).transferFrom(self.tokenWallet, _beneficiary, tokens), "Could not forward funds due to an unknown error."
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
