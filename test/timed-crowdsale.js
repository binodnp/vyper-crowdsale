const { ether } = require('./helpers/ether');
const { advanceBlock } = require('./helpers/advanceToBlock');
const { increaseTimeTo, duration } = require('./helpers/increaseTime');
const { latestTime } = require('./helpers/latestTime');
const { expectThrow } = require('./helpers/expectThrow');
const { EVMRevert } = require('./helpers/EVMRevert');

const BigNumber = web3.BigNumber;

require('chai')
  .use(require('chai-bignumber')(BigNumber))
  .should();

const TimedCrowdsale = artifacts.require('timed_crowdsale.vyper');
const SimpleToken = artifacts.require('erc20_standard_token.vyper');

contract('TimedCrowdsale', function ([_, investor, wallet, purchaser]) {
  const rate = new BigNumber(1);
  const value = ether(42);
  const tokenSupply = new BigNumber('1e22');

  before(async function () {
    // Advance to the next block to correctly read time in the solidity "now" function interpreted by ganache
    await advanceBlock();
  });

  beforeEach(async function () {
    this.openingTime = (await latestTime()) + duration.weeks(1);
    this.closingTime = this.openingTime + duration.weeks(1);
    this.afterClosingTime = this.closingTime + duration.seconds(1);
    this.token = await SimpleToken.new(web3.fromAscii("Name"), web3.fromAscii("SYMBOL"), tokenSupply, 18);
    this.crowdsale = await TimedCrowdsale.new(this.openingTime, this.closingTime, rate, wallet, this.token.address);
    await this.token.transfer(this.crowdsale.address, tokenSupply);
  });

  it('should be ended only after end', async function () {
    let ended = await this.crowdsale.hasClosed();
    ended.should.equal(false);
    await increaseTimeTo(this.afterClosingTime);
    ended = await this.crowdsale.hasClosed();
    ended.should.equal(true);
  });

  describe('accepting payments', function () {
    it('should reject payments before start', async function () {
      await expectThrow(this.crowdsale.send(value), EVMRevert);
      await expectThrow(this.crowdsale.buyTokens(investor, { from: purchaser, value: value }), EVMRevert);
    });

    it('should accept payments after start', async function () {
      await increaseTimeTo(this.openingTime);
      await this.crowdsale.send(value);
      await this.crowdsale.buyTokens(investor, { value: value, from: purchaser });
    });

    it('should reject payments after end', async function () {
      await increaseTimeTo(this.afterClosingTime);
      await expectThrow(this.crowdsale.send(value), EVMRevert);
      await expectThrow(this.crowdsale.buyTokens(investor, { value: value, from: purchaser }), EVMRevert);
    });
  });
});
