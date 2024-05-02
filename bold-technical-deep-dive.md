
## Overview

Under the hood, BoLD can offer time-bounded, permissionless validation because a correct Arbitrum state assertion is not tied to a single validator or entity. Instead, claims are tied to deterministic Merkle proofs and hashes that will be proven on Ethereum. Any party can bond on the correct state and, through interactive fraud proofs, prove their claim is correct. This means that a single honest party bonding on the correct state assertion will always win disputes, guaranteed.

To put it simply, Arbitrum’s current dispute protocol assumes that any assertion that gets challenged must be defended against by each unique challenger. It is similar to a 1-vs-1 tournament, where the honest party may participate in one or more concurrent tournaments at any time. BoLD, on the other hand, enables an all-vs-all battle royal between two categories: Good vs Evil, where there must and will always be a single winner in the end.

Validators on Arbitrum can post their claim on the validity of state roots, known as **assertions**. Ethereum, of course, does not know anything about the validity of these Arbitrum state roots, but it _can_ help prove their correctness. _Anyone_ in the world can then initiate a challenge over any unconfirmed assertion to start the protocol’s game.

The assertions being disputed concern block hashes of an Arbitrum chain at a given batch/inbox position. Given that Arbitrum chains are deterministic, there is only one correct history for all parties running the standard Nitro software. Using the notion of one-step proof, Ethereum can check whether someone is making a fraudulent assertion.

If a claim is honest, it can be confirmed on Ethereum after a 6.4-day period (although the DAO can change this period). If a claim is malicious, anyone who knows the correct Arbitrum state can successfully challenge it within that 6.4-day window _and always win_ within a challenge period.

The current implementation of BoLD involves both on-chain and off-chain components:

1. Rollup contracts to be deployed on Ethereum.

2. New challenge management contracts to be deployed on Ethereum.

3. [Honest validator software](https://github.com/offchainlabs/bold) equipped to submit assertions and perform challenge moves on any assertions it disagrees with. The honest validator is robust enough to win against malicious entities and always ensures honest assertions are the only ones confirmed on-chain.

### Key terminology

- **Arbitrum Rollup Contracts:** The set of smart contracts on Ethereum L1 that serve as both the data availability layer for Arbitrum and for confirming the rollup's state assertions after a challenge period has passed for each assertion made

- **Assertions:** A claim posted to the Arbitrum Rollup contracts on Ethereum L1 about the Arbitrum L2 execution state. Each claim consumes messages from the Arbitrum Rollup inbox contract. Each assertion can be confirmed after a period of 6.4 days, and anyone can challenge it during that period. A BoLD challenge will add an additional upper bound of 6.4 days to confirm an assertion. If an assertion is challenged near the end of 6.4 days, an additional 6.4 days will be needed to complete the challenge. Gaining the right to post assertions requires placing a large, one-time bond, which can get taken away in the case of losing a challenge to a competing assertion. Opening challenges requires opening smaller “mini-bonds” each time.

- **Validating Bridge:** The smart contract that leverages Ethereum's security and censorship-resistance to unlock bridged assets from L2 back to L1. Assets can be unlocked after an assertion has been posted and confirmed after a challenge period has passed

- **Fraud Proofs:** Proofs of a single step of `WAVM` execution of Arbitrum's state transition function, which are submitted to Ethereum and verified in the EVM via a smart contract. These proofs allow Ethereum to be the final arbiter of disagreements over assertions in the Rollup contracts, which cannot be falsified by any parties as there is only a single, correct result of executing a WASM instruction on a pre-state.
