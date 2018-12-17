# IndividuallyCappedCrowdsale
# Contributors: Binod Nirvan
# This file is released under Apache 2.0 license.
# @dev Crowdsale with per-user caps.
# Ported from Open Zeppelin
# https://github.com/OpenZeppelin
# 
# See https://github.com/OpenZeppelin
# Open Zeppelin tests ported: IndividuallyCappedCrowdsale.test.js, Ownable.test.js, Ownable.behaviour.js

#@dev ERC20/223 Features referenced by this contract
contract TokenContract:
    def transfer(_to: address, _value: uint256) -> bool: modifying

#Ownable
OwnershipRenounced: event({_previousOwner: indexed(address)})
OwnershipTransferred: event({_previousOwner: indexed(address), _newOwner: indexed(address)})

#Crowdsale

# Event for token purchase logging
# @param _purchaser who paid for the tokens
# @param _beneficiary who got the tokens
# @param _value weis paid for purchase
# @param _amount amount of tokens purchased
TokenPurchase: event({_purchaser: indexed(address), _beneficiary: indexed(address), _value: uint256(wei), _amount: uint256})

#Individually Capped Crowdsale
contributions: public(map(address, uint256))
caps: public(map(address, uint256))


#Ownable
owner: public(address)

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


#Ownable
# This feature is ported from Open Zeppelin. 
# The ownable feature provides basic authorization control functions 
# and simplifies the implementation of "user permissions".
@public
def renounceOwnership():
    """
    @dev Allows the current owner to relinquish control of the contract.
    @notice Renouncing to ownership will leave the contract without an owner.
    It will not be possible to call the functions with the `onlyOwner`
    modifier anymore.
    """

    assert msg.sender == self.owner, "Access is denied."

    log.OwnershipRenounced(msg.sender)
    self.owner = ZERO_ADDRESS

@public 
def transferOwnership(_newOwner: address):
    """
    @dev Allows the current owner to transfer control of the contract to a newOwner.
    @param _newOwner The address to transfer ownership to.
    """
    assert msg.sender == self.owner, "Access is denied."
    assert _newOwner != ZERO_ADDRESS, "Invalid owner supplied."

    log.OwnershipTransferred(msg.sender, _newOwner)
    self.owner = _newOwner

#Individually Capped Crowdsale
@public
def setUserCap(_beneficiary: address, _cap: uint256):
    """
    @dev Sets a specific user's maximum contribution.
    @param _beneficiary Address to be capped
    @param _cap Wei limit for individual contribution
    """

    assert msg.sender == self.owner, "Access is denied."
    self.caps[_beneficiary] = _cap

@public
def setGroupCap(_totalItems: int128, _beneficiaries: address[50], _cap: uint256):
    """
    @dev Sets a group of users' maximum contribution.
    @param _totalItems The count of total beneficiaries in this group. Should be less than or equal to 50.
    @param _beneficiaries List of addresses to be capped.
    @param _cap Wei limit for individual contribution
    """

    assert msg.sender == self.owner, "Access is denied."

    for i in range(50):
        if(i >= _totalItems):
            break
        self.caps[_beneficiaries[i]] = _cap


@public
@constant
def getUserCap(_beneficiary: address) -> uint256:
    """
    @dev Returns the cap of a specific user.
    @param _beneficiary Address whose cap is to be checked
    @return Current cap for individual user
    """

    return self.caps[_beneficiary]

@public
@constant
def getUserContribution(_beneficiary: address) -> uint256:
    """
    @dev Returns the amount contributed so far by a sepecific user.
    @param _beneficiary Address of contributor
    @return User contribution so far
    """

    return self.contributions[_beneficiary]

#Crowdsale
@public
def __init__(_rate: uint256, _wallet: address, _token: address):
    """
    @dev Initializes this contract
    @param _rate Number of token units a buyer gets per wei
    @param _wallet Address where collected funds will be forwarded to
    @param _token Address of the token being sold
    """
    assert _rate > 0, "Invalid value supplied for the parameter \"_rate\"."
    assert _wallet != ZERO_ADDRESS, "Invalid wallet address."
    assert _token != ZERO_ADDRESS, "Invalid token address."

    self.rate = _rate
    self.wallet = _wallet
    self.token = _token
    self.owner = msg.sender

@private
@constant
def getTokenAmount(_weiAmount: uint256) -> uint256:
    return _weiAmount * self.rate


@private
def processTransaction(_sender: address, _beneficiary: address, _weiAmount: uint256(wei)):
    #pre validate
    assert _beneficiary != ZERO_ADDRESS, "Invalid address."
    assert _weiAmount != 0, "Invalid amount received."
    assert self.contributions[_beneficiary] + as_unitless_number(_weiAmount) \
        <= self.caps[_beneficiary], "Maximum user funding cap exceeded."

    #calculate the number of tokens for the Ether contribution.
    tokens: uint256 = self.getTokenAmount(as_unitless_number(_weiAmount))
    
    self.weiRaised += _weiAmount

    #process purchase
    assert TokenContract(self.token).transfer(_beneficiary, tokens), "Could not forward funds due to an unknown error."
    log.TokenPurchase(_sender, _beneficiary, _weiAmount, tokens)

    #forward funds to the receiving wallet address.
    send(self.wallet, _weiAmount)

    self.contributions[_beneficiary] += as_unitless_number(_weiAmount)

@public
@payable
def buyTokens(_beneficiary: address):
    self.processTransaction(msg.sender, _beneficiary, msg.value)

@public
@payable
def __default__():
    self.processTransaction(msg.sender, msg.sender, msg.value)

