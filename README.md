# Tamarin examples

Small learning models exploring man-in-the-middle attacks on unauthenticated
Diffie–Hellman, and how the assumptions in a security property affect its meaning.
These are symbolic exercises, not production protocol designs or implementation audits.

The original models credit code from **David Wong's
[Tamarin Prover Introduction](https://www.cryptologie.net/posts/tamarin-prover-introduction/)**.
That attribution is retained in each model. Jim Miller's examples and later
clarifications build on that introduction. No new license is asserted over the inherited code.

## Start here

| Model | What to inspect |
| --- | --- |
| [`Basic.spthy`](Diffie-Hellman/Basic.spthy) | Unauthenticated key exchange; the `MITM` claim is expected to have a counterexample. |
| [`EasyFixMITM.spthy`](Diffie-Hellman/EasyFixMITM.spthy) | Identity announcements and conditional claims about matching keys. The historical filename is retained. |

**`EasyFixMITM` does not implement an authenticated protocol.** `AnnounceIdentity`
records an event for the lemmas to inspect; receive rules still accept public keys
from the network. `FixedMITM` assumes the received keys match announcements.
`OriginalMITM` omits that assumption and remains vulnerable. An implementation
would need a real mechanism to authenticate the peer's key.

The lemmas' conclusion is `not (K(key1) & K(key2))`: the attacker cannot learn
**both** keys in the specified traces. It does not say that neither key can leak,
nor does it establish authentication, agreement, or forward secrecy.

## Reproduce the checks

Verified toolchain: **Tamarin 1.12.0** and **Maude 3.5.1**. Follow the
[official installation instructions](https://tamarin-prover.com/manual/master/book/002_installation.html).
Graphviz is useful for interactive trace graphs. The Python runner requires
Python 3.13 or newer and has no third-party runtime dependencies.

```sh
tamarin-prover --version
GHCRTS='-N2 -M2G' python3 check_models.py
```

The command limits the Haskell runtime to two cores and a 2 GiB heap. The runner
gives each model a ten-minute limit, saves full output under `results/`,
rejects warnings or incomplete/missing results, and compares every lemma with the
expectations below. A falsified security lemma is an expected successful check
when the point of the example is to exhibit an attack.

To inspect the theories directly:

```sh
tamarin-prover --prove Diffie-Hellman/Basic.spthy
tamarin-prover --prove Diffie-Hellman/EasyFixMITM.spthy
tamarin-prover interactive Diffie-Hellman
```

| Model | Lemma | Observed result (2026-10-31) |
| --- | --- | --- |
| Basic | `HonestRun` | verified, 8 steps (exists-trace) |
| Basic | `MITM` | falsified, attack trace found in 8 steps |
| EasyFixMITM | `HonestRun` | verified, 7 steps (exists-trace) |
| EasyFixMITM | `OriginalMITM` | falsified, attack trace found in 8 steps |
| EasyFixMITM | `FixedMITM` | verified, 9 steps |
| EasyFixMITM | `MITMAlternate` | verified, 11 steps |

**Verification status:** both models passed parsing and all well-formedness checks;
all six lemma outcomes matched the regression specification. These are results for
the stated symbolic models, with the limitations below. See
[VALIDATION.md](VALIDATION.md) for model hashes, tool checks, and environment caveats.

`HonestRun` was added to each model to check reachability and guard against
vacuous results; the second also reaches the key-binding assumptions. Existing
protocol rules and security formulas are unchanged. Comments now distinguish
assumptions from checks performed by a protocol.

## Modeling limits

- The adversary controls the public network; there is no key-compromise rule.
- Identity secrets are reused, rather than fresh per session.
- Identities are not restricted to one key, and sessions have no fresh identifier.
- The client receive rule has no pending-session state. These models do not prove
  that every accepted response corresponds to a particular initiated session.
- A proof concerns only the stated model and property. Even a verified
  `HonestRun` does not establish that the model captures an intended real protocol.

Useful references: the Tamarin manual's
[first example](https://tamarin-prover.com/manual/master/book/003_example.html) and
[modeling issues](https://tamarin-prover.com/manual/master/book/010_modeling-issues.html).

## Check the runner

```sh
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check
uv run --locked prek install
uv run --locked prek run --all-files
```

These tests exercise output validation and failure handling; they do not replace
running the prover on the models.
