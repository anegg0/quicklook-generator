
---
title: The Sequencer and Censorship Resistance
description: 'Learn the fundamentals of the Arbitrum Sequencer.'
author: pete-vielhaber
sme: TucksonDev
user_story: As a current or prospective Arbitrum user, I need to learn more about the Sequencer.
content_type: get-started
---

The <a data-quicklook-from="sequencer">Sequencer</a> is a specially designated <a data-quicklook-from="arbitrum">Arbitrum</a> full node which, under normal conditions, is responsible for submitting users’ transactions onto L1. In principle, a chain’s Sequencer can take different forms; as [currently stands](https://docs.arbitrum.foundation/state-of-progressive-decentralization), the Sequencer is a single, centralized entity; eventually, sequencing affordances could be given to a distributed committee of sequencers which come to consensus on ordering. However, regardless of its form, the Sequencer has a fundamental limitation that doesn’t apply to any other part of the system: it must operate under its own security assumptions; i.e., it can’t, in principle, derive security directly from layer 1. This brings up the question of how Arbitrum Rollup maintains its claim to censorship resistance when-and-if the Sequencer misbehaves.

Here we will describe the mechanics of how the Sequencer operates and how any user can bypass the Sequencer entirely to submit any Arbitrum transaction (including one that, say, initiates an L2 to L1 message to withdraw funds) directly from layer 1. Thus, the mechanism thereby preserves censorship resistance even if the Sequencer is completely unresponsive or even malicious.

Clients interact with the Sequencer in exactly the same way they would interact with any full node, for example by giving their wallet software a network URL that happens to point to the Sequencer.

[Currently](https://docs.arbitrum.foundation/state-of-progressive-decentralization), on the Arbitrum One and <a data-quicklook-from="arbitrum-nova">Arbitrum Nova</a> chains, the Sequencer is run by <a data-quicklook-from="offchain-labs">Offchain Labs</a>.

## The Core Inbox

When we talk about “submitting a transaction into an <a data-quicklook-from="arbitrum-chain">Arbitrum chain</a>,” we’re talking about getting it included into the chain’s core Inbox, represented by the `sequencerInboxAccs` byte array in `<a data-quicklook-from="bridge">Bridge</a>`. Once transactions are included in the core Inbox, their ordering is fixed, execution is fully deterministic, and we can trustlessly treat the resultant state as having L1-level finality (see [Transaction Lifecycle](/how-arbitrum-works/02-transaction-lifecycle.mdx)).

When we add a Sequencer, the operation of the inbox changes.

- Only the Sequencer can put new messages directly into the inbox. The Sequencer tags the messages it is submitting with an Ethereum block number and timestamp. (<a data-quicklook-from="arbos">ArbOS</a> ensures that these are non-decreasing, adjusting them upward if necessary to avoid decreases.)
- Anyone else can submit a message, but messages submitted by non-Sequencer nodes will be put into the "delayed inbox" queue, which is managed by an L1 Ethereum contract.
  - Messages in the delayed inbox queue will wait there until the Sequencer chooses to "release" them into the main inbox, where they will be added to the end of the inbox. A well-behaved Sequencer will typically release delayed messages after about ten minutes, for reasons explained below.
  - Alternatively, if a message has been in the delayed inbox queue for longer than a maximum delay interval (currently @arbOneForceIncludePeriodHours@ hours on Arbitrum One) then anyone can force it to be promoted into the main inbox. (This ensures that the Sequencer can only delay messages but can't censor them.)

The Sequencer’s role (or lack thereof) concerns strictly what happens prior; i.e., how a transaction makes its way into the core Inbox. We’ll break down the possible routes a transaction can take into two scenarios: a well-behaved Sequencer, and a faulty Sequencer.

## Happy/Common Case: Sequencer Is Live and Well-behaved

Here, we start by assuming that the Sequencer is fully operational, and is running with the intent of processing users’ transactions in as safe and timely a manner as possible. The Sequencer can receive a user’s transaction two ways — either directly via an RPC request, or via the underlying L1.

If a user is posting a “standard” Arbitrum transaction (i.e., interacting with an L2 native dapp), the user will submit the signed transaction directly to the Sequencer, much like how a user submits a transaction to an Ethereum node when interacting with L1. Upon receiving it, the Sequencer will execute it and nearly instantaneously deliver the user a receipt. Some short time later — [usually no more than a few minutes](https://arbiscan.io/batches) — the Sequencer will include the user’s transaction in a batch and post it on L1 by calling one of the `SequencerInbox`’s `addSequencerL2Batch` methods. Note that only the Sequencer has the authority to call these methods; this assurance that no other party can include a message directly is, in fact, the very thing that gives the Sequencer the unique ability to provide instant, "soft-confirmation" receipts.
Once posted in a batch, the transactions have L1-level finality.

Transactions that go through the delayed inbox will take longer to get finality. Their time to finality will roughly double, because they will have to wait one finality period for promotion, then another finality period for the Ethereum transaction that promoted them to achieve finality.

This is the basic tradeoff of having a Sequencer: if your message uses the Sequencer, finality is faster; but if your message doesn't use the Sequencer, finality will be slower. This is usually a good tradeoff, because most transactions will use the Sequencer; and because the practical difference between instant and 10-minute finality is bigger than the difference between 10-minute and 20-minute finality.

So a Sequencer is generally a win, if the Sequencer is well behaved.

### Cross chain communication

As we mentioned, transactions can be received from L1 and L2. A cross chain message will eventually result in a transaction being executed on the destination chain.

### L1 contracts can submit L2 transactions

An L1 contract can submit an L2 transaction, just like a user would, by calling the Nitro chain's inbox contract on Ethereum. This L2 transaction will run later, producing results that will not be available to the L1 caller. The transaction will execute at L2, but the L1 caller won’t be able to see any results from the L2 transaction.

The advantage of this method is that it is simple and has relatively low latency. The disadvantage, compared to the other method we’ll describe soon, is that the L2 transaction might revert if the L1 caller doesn’t get the L2 gas price and max gas amount right. Because the L1 caller can’t see the result of its L2 transaction, it can’t be absolutely sure that its L2 transaction will succeed.

This would introduce a serious a problem for certain types of L1 to L2 interactions. Consider a transaction that includes depositing a token on L1 to be made available at some address on L2. If the L1 side succeeds, but the L2 side reverts, you've just sent some tokens to the L1 inbox contract that are unrecoverable on either L2 or L1. Not good.

### L1 to L2 ticket-based transactions

Fortunately, we have another method for L1 to L2 calls, which is more robust against gas-related failures, that uses a ticket-based system. The idea is that an L1 contract can submit a “retryable” transaction. The Nitro chain will try to run that transaction. If the transaction succeeds, nothing else needs to happen. But if the transaction fails, Nitro will create a “ticketID” that identifies that failed transaction. Later, anyone can call a special pre-compiled contract at L2, providing the ticketID, to try redeeming the ticket and re-executing the transaction.

When saving a transaction for retry, Nitro records the sender’s address, destination address, callvalue, and calldata. All of this is saved, and the callvalue is deducted from the sender’s account and (logically) attached to the saved transaction.

If the redemption succeeds, the transaction is done, a receipt is issued for it, and the ticketID is canceled and can’t be used again. If the redemption fails, for example because the packaged transaction fails, the redemption reports failure and the ticketID remains available for redemption.

Normally the original submitter will try to cause their transaction to succeed immediately, so it never needs to be recorded or retried. As an example, our "token deposit" use case above should, in the happy, common case, still only require a single signature from the user. If this initial execution fails, the ticketID will still exist as a backstop which others can redeem later.

Submitting a transaction in this way carries a price in ETH which the submitter must pay, which varies based on the calldata size of the transaction. Once submitted, the ticket is valid for about a week. If the ticket has not been redeemed in that period, it is deleted.

When the ticket is redeemed, the pre-packaged transaction runs with sender and origin equal to the original submitter, and with the destination, callvalue, and calldata the submitter provided at the time of submission.

This mechanism is a bit more cumbersome than ordinary L1 to L2 transactions, but it has the advantage that the submission cost is predictable and the ticket will always be available for redemption if the submission cost is paid. As long as there is some user who is willing to redeem the ticket, the L2 transaction will eventually be able to execute and will not be silently dropped.

### L2 to L1 ticket-based calls

Calls from L2 to L1 operate in a similar way, with a ticket-based system. An L2 contract can call a method of the precompiled ArbSys contract, to send a transaction to L1. When the execution of the L2 transaction containing the submission is confirmed at L1 (some days later), a ticket is created in the L1 outbox contract. That ticket can be triggered by anyone who calls a certain L1 outbox method and submits the ticketID. The ticket is only marked as redeemed if the L1 transaction does not revert.

These L2-to-L1 tickets have unlimited lifetime, until they’re successfully redeemed. No rent is required, as the tickets (actually a Merkle hash of the tickets) are recorded in Ethereum storage, which does not require rent. (The cost of allocating storage for the ticket Merkle roots is covered by L2 transaction fees.)

Alternatively, a user can submit their L2 message to the Sequencer by posting it on the underlying L1. This path is necessary if the user wishes to perform some [L1 operation along with the L2](/how-arbitrum-works/10-l1-to-l2-messaging.mdx) message and to preserve atomicity between the two — the textbook example here being a token deposit via a [bridge](/build-decentralized-apps/token-bridging/01-overview.mdx) (escrow on L1, mint on L2). The user does this by publishing an L1 transaction (i.e., sending a normal transaction to an L1 node) that calls one of the relevant methods on the `Inbox` contract; i.e., `sendUnsignedTransaction`. This adds a message onto what we’ll call “the delayed Inbox”, (represented by the `delayedInboxAccs` in the `Bridge` contract), which is effectively a queue that messages wait in before being moved over to the core `Inbox`. The Sequencer will emit an L2 receipt about ~10 minutes after the transaction has been included in the delayed Inbox (the reason for this delay is to minimize the risk of short term L1 reorgs which could in turn cause an L2 reorg and invalidate the Sequencer’s L2 receipts.) Again, the last step is for the Sequencer to include the L2 message in a batch — when calling the batch submission methods, the Sequencer specifies how many messages in the delayed inbox to include — finalizing the transaction.

In sum — in either happy case, the user first delivers their message to the Sequencer, who in turn ensures that it arrives in the core Inbox.

## Unhappy/Uncommon Case: Sequencer Isn’t Doing Its Job

Now let’s suppose the Sequencer, for whatever reason, is entirely failing to carry out its task of submitting messages. A user can still get their transaction included in two steps:

First, they submit their L2 message via L1 into the delayed Inbox as described above: note that although atomic cross-chain messages are the common case for using the delayed Inbox, it can in principle be used to submit _any_ L2 message.

Once in the delayed Inbox, we obviously can’t rely on the Sequencer to include the transaction in a batch. Instead, we can use `SequencerInbox`’s `forceInclusion` method. Once a message has been in the delayed Inbox for a sufficient amount of time, `forceInclusion` can be called to move it from the delayed Inbox into the core Inbox, at which point it’s finalized. Crucially, any account can call `forceInclusion`.

Currently, on Arbitrum One, this delay time between submission and force inclusion is roughly @arbOneForceIncludePeriodHours@ hours, as specified by `maxTimeVariation.delayBlocks` / `maxTimeVariation.delaySeconds`. A force inclusion from L1 would directly affect the state for any unconfirmed L2 transactions; keeping conservatively high delay value ensures it should only be used under extraordinary circumstances.

On top of the delay itself, the `forceInclusion` path has the downside of uncertainty around transaction ordering; i.e., while waiting for a message's max delay to pass, a malicious Sequencer could, in principle, directly post messages in front of it. However, there’s ultimately nothing the Sequencer can do to stop it from being included in the core Inbox, at which point its ordering is finalized.

While the slow, “unhappy” path isn’t optimal, and should rarely, if ever, be necessary, its availability as an option ensures Arbitrum Rollup always preserves its trustless security model, even if the permissioned parts of the system act faulty.

:::info

On Arbitrum One, Offchain Labs [currently](https://docs.arbitrum.foundation/state-of-progressive-decentralization) runs a Sequencer which is well-behaved--we promise!. This will be useful but it's not decentralized. Over time, we'll switch to [decentralized, fair sequencing](#decentralized-fair-sequencing).

:::

## How the Sequencer Publishes the Sequence

So how do nodes get the sequence? The Sequencer publishes it in two ways: a real-time feed, and batches posted on L1 Ethereum.

The real-time feed is published by the Sequencer so that anyone who subscribes to the feed receives instant notifications of each transaction as it is sequenced. Nitro nodes can subscribe to the feed directly from the Sequencer, or through a relay that forwards the feed. The feed represents the Sequencer's promise that it will record transactions in a particular order. If the Sequencer is honest and doesn't have a long downtime, this promise will be kept. So anyone who trusts the Sequencer to keep its promises can rely on the feed to get instant information about the transaction sequence--and they can run the sequenced transactions through the state transition function to learn the results of each transaction immediately. This is "soft finality" for transactions; it's "soft" because it depends on the Sequencer keeping its promises.

The Sequencer also publishes its sequence on the L1 Ethereum chain. Periodically--perhaps every few minutes in production--the Sequencer concatenates the next group of transactions in the feed, compresses them for efficiency, and posts the result as calldata on Ethereum. This is the final and official record of the transaction sequence. As soon as this Ethereum transaction has finality on Ethereum, the Layer 2 Nitro transactions it records will have finality. These transactions are final because their position in the sequence has finality, and the outcome of the transactions is deterministic and knowable to any party. This is "hard finality".

The Sequencer's batches are compressed using a general-purpose data compression algorithm called "brotli", on its highest-compression setting.

## Decentralized fair sequencing

Viewed from 30,000 feet, decentralized fair sequencing isn't too complicated. Instead of being a single centralized server, the Sequencer is a committee of servers, and as long as a large enough supermajority of the committee is honest, the Sequencer will establish a fair ordering over transactions.

How to achieve this is more complicated. Research by a team at Cornell Tech, including Offchain Labs CEO and Co-founder Steven Goldfeder, developed the first-ever decentralized fair sequencing algorithm. With some improvements that are under development, these concepts will form the basis for our longer-term solution, of a fair decentralized Sequencer.
