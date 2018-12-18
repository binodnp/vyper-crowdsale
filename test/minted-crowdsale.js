const { ether } = require('./helpers/ether');
const MintedCrowdsale = artifacts.require('minted_crowdsale.vyper');
const MintableToken = artifacts.require('mintable_token.vyper');
const { ethGetBalance } = require('./helpers/web3');
const BigNumber = web3.BigNumber;

const should = require('chai')
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('MintedCrowdsale', function ([_, investor, wallet, purchaser]) {
  const rate = new BigNumber(1000);
  const value = ether(5);
  const expectedTokenAmount = rate.mul(value);

  describe('using MintableToken', function () {
    beforeEach(async function () {
      this.token = await MintableToken.new(web3.fromAscii("Name"), web3.fromAscii("SYMBOL"), 0, ether(10000000), 18);
      this.crowdsale = await MintedCrowdsale.new(rate, wallet, this.token.address);
      await this.token.transferOwnership(this.crowdsale.address);
    });

    it('should be token owner', async function () {
      const owner = await this.token.owner();
      owner.should.equal(this.crowdsale.address);
    });

    describe('as a minted crowdsale', function () {
        describe('accepting payments', function () {
          it('should accept payments', async function () {
            await this.crowdsale.send(value);
            await this.crowdsale.buyTokens(investor, { value: value, from: purchaser });
          });
        });
    
        describe('high-level purchase', function () {
          it('should log purchase', async function () {
            const { logs } = await this.crowdsale.sendTransaction({ value: value, from: investor });
            const event = logs.find(e => e.event === 'TokenPurchase');
            should.exist(event);
            event.args._purchaser.should.equal(investor);
            event.args._beneficiary.should.equal(investor);
            event.args._value.should.be.bignumber.equal(value);
            event.args._amount.should.be.bignumber.equal(expectedTokenAmount);
          });
    
          it('should assign tokens to sender', async function () {
            await this.crowdsale.sendTransaction({ value: value, from: investor });
            const balance = await this.token.balanceOf(investor);
            balance.should.be.bignumber.equal(expectedTokenAmount);
          });
    
          it('should forward funds to wallet', async function () {
            const pre = await ethGetBalance(wallet);
            await this.crowdsale.sendTransaction({ value, from: investor });
            const post = await ethGetBalance(wallet);
            post.minus(pre).should.be.bignumber.equal(value);
          });
        });
      });
  });
});
