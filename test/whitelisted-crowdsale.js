const { ether } = require('./helpers/ether');
const { expectThrow } = require('./helpers/expectThrow');
const { shouldBehaveLikeOwnable } = require('./ownable.behavior.js');

const BigNumber = web3.BigNumber;

require('chai')
  .should();

const WhitelistedCrowdsale = artifacts.require('whitelisted_crowdsale.vyper');
const SimpleToken = artifacts.require('erc20_standard_token.vyper');

contract('WhitelistedCrowdsale', function ([_, wallet, authorized, unauthorized, anotherAuthorized]) {
  const rate = 1;
  const value = ether(42);
  const tokenSupply = new BigNumber('1e22');

  describe('single user whitelisting', function () {
    beforeEach(async function () {
      this.token = await SimpleToken.new(web3.fromAscii("Name"), web3.fromAscii("SYMBOL"), tokenSupply, 18);
      this.crowdsale = await WhitelistedCrowdsale.new(rate, wallet, this.token.address);
      this.ownable = this.crowdsale;
      
      await this.token.transfer(this.crowdsale.address, tokenSupply);
      await this.crowdsale.addAddressToWhitelist(authorized);
    });

    shouldBehaveLikeOwnable([_, wallet, authorized, unauthorized, anotherAuthorized]);

    describe('accepting payments', function () {
      it('should accept payments to whitelisted (from whichever buyers)', async function () {
        await this.crowdsale.sendTransaction({ value, from: authorized });
        await this.crowdsale.buyTokens(authorized, { value: value, from: authorized });
        await this.crowdsale.buyTokens(authorized, { value: value, from: unauthorized });
      });

      it('should reject payments to not whitelisted (from whichever buyers)', async function () {
        await expectThrow(this.crowdsale.sendTransaction({ value, from: unauthorized }));
        await expectThrow(this.crowdsale.buyTokens(unauthorized, { value: value, from: unauthorized }));
        await expectThrow(this.crowdsale.buyTokens(unauthorized, { value: value, from: authorized }));
      });

      it('should reject payments to addresses removed from whitelist', async function () {
        await this.crowdsale.removeAddressFromWhitelist(authorized);
        await expectThrow(this.crowdsale.buyTokens(authorized, { value: value, from: authorized }));
      });
    });

    describe('reporting whitelisted', function () {
      it('should correctly report whitelisted addresses', async function () {
        const isAuthorized = await this.crowdsale.whitelist(authorized);
        isAuthorized.should.equal(true);
        const isntAuthorized = await this.crowdsale.whitelist(unauthorized);
        isntAuthorized.should.equal(false);
      });
    });
  });

  describe('many user whitelisting', function () {
    const tokenSupply = new BigNumber('1e22');

    beforeEach(async function () {
      this.token = await SimpleToken.new(web3.fromAscii("Name"), web3.fromAscii("SYMBOL"), tokenSupply, 18);
      this.crowdsale = await WhitelistedCrowdsale.new(rate, wallet, this.token.address);
      await this.token.transfer(this.crowdsale.address, tokenSupply);
      await this.crowdsale.addAddressesToWhitelist(2, [authorized, anotherAuthorized]);
    });

    describe('accepting payments', function () {
      it('should accept payments to whitelisted (from whichever buyers)', async function () {
        await this.crowdsale.buyTokens(authorized, { value: value, from: authorized });
        await this.crowdsale.buyTokens(authorized, { value: value, from: unauthorized });
        await this.crowdsale.buyTokens(anotherAuthorized, { value: value, from: authorized });
        await this.crowdsale.buyTokens(anotherAuthorized, { value: value, from: unauthorized });
      });

      it('should reject payments to not whitelisted (with whichever buyers)', async function () {
        await expectThrow(this.crowdsale.send(value));
        await expectThrow(this.crowdsale.buyTokens(unauthorized, { value: value, from: unauthorized }));
        await expectThrow(this.crowdsale.buyTokens(unauthorized, { value: value, from: authorized }));
      });

      it('should reject payments to addresses removed from whitelist', async function () {
        await this.crowdsale.removeAddressFromWhitelist(anotherAuthorized);
        await this.crowdsale.buyTokens(authorized, { value: value, from: authorized });
        await expectThrow(this.crowdsale.buyTokens(anotherAuthorized, { value: value, from: authorized }));
      });
    });

    describe('reporting whitelisted', function () {
      it('should correctly report whitelisted addresses', async function () {
        const isAuthorized = await this.crowdsale.whitelist(authorized);
        isAuthorized.should.equal(true);
        const isAnotherAuthorized = await this.crowdsale.whitelist(anotherAuthorized);
        isAnotherAuthorized.should.equal(true);
        const isntAuthorized = await this.crowdsale.whitelist(unauthorized);
        isntAuthorized.should.equal(false);
      });
    });
  });
});
