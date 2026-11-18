# Validation record

Checked 2026-10-31 on ARM64 macOS 27.0.1 with Python 3.13.14, Tamarin 1.12.0,
Maude 3.5.1, libbuddy 2.4, and Graphviz 16.1.0.

## Model results

```sh
GHCRTS='-N2 -M2G' python3 check_models.py
```

The command exited 0. Both models parsed and reported that all well-formedness
checks were successful. No warning or incomplete result was reported.

| Model | Lemma | Result | Proof-search steps |
| --- | --- | --- | --- |
| Basic | `HonestRun` (exists-trace) | verified | 8 |
| Basic | `MITM` (all-traces) | falsified; attack trace found | 8 |
| EasyFixMITM | `HonestRun` (exists-trace) | verified | 7 |
| EasyFixMITM | `OriginalMITM` (all-traces) | falsified; attack trace found | 8 |
| EasyFixMITM | `FixedMITM` (all-traces) | verified | 9 |
| EasyFixMITM | `MITMAlternate` (all-traces) | verified | 11 |

Tamarin reported processing times of 0.54 s and 0.63 s respectively. Each model
had a 600-second wall-clock timeout; the Haskell runtime used two cores and a
2 GiB heap limit. This heap limit is not a limit on total process-tree memory.

SHA-256 of the checked model files:

```text
Basic.spthy
73794476e034308fecb47af997005f587731fc435c516a6c45e7c0e5e3a7c9a4

EasyFixMITM.spthy
7afdfac8c636cc5a872ceb1d1dc5a815836db0bf49bb45eb61839132d05712de
```

The original protocol rules and security formulas are unchanged from commit
`57695c888ddd487c944f6ae6b804204545e6671a`: a comparison excluding comments,
whitespace, and the two new `HonestRun` lemmas confirmed they are identical.
The verified claims retain the assumptions and limits explained in the README.

## Tool and runner checks

- Tamarin's installation self-test passed all 55 cases, including checks of
  Maude, Graphviz, and the unification infrastructure.
- Homebrew's linkage checks passed for Tamarin, Maude, and libbuddy.
- The installed tools came from the project-maintained Homebrew tap at commit
  `7f44528a0059bf86c4c2744c30a122ccc4deb86b`. Homebrew recorded all three as
  installed from bottles. SHA-256 hashes of the downloaded bottle archives were
  also independently compared with the inspected formula checksums and matched.
- All 12 Python runner tests pass, along with Ruff lint/format, ty, and hooks.
  Tests cover incomplete/duplicate results, warnings, process failures, timeouts,
  missing tools, and version errors. They supplement the actual prover run above.

## Environment caveats

Homebrew labels this macOS prerelease a Tier 2 configuration. Two separate
formula tests did not pass in their original wrappers:

- **libbuddy:** its C++ compile test could not find `iostream`. The same test
  compiled using the existing macOS SDK's explicit C++ include directory, then
  ran successfully and printed the expected `T`. No compiler or SDK was installed.
- **Maude:** its formula expected interactive `Maude>` prompts in piped output.
  Version 3.5.1 returned the expected `hello world` result without those prompts.
  A direct string-reduction check passed, as did Tamarin's Maude checks.

These are reported separately from the successful model and runtime checks;
the original formula tests are not represented as passing. No tap recipe was edited.
Temporary formula-specific trust was removed after installation and tests, with
the preexisting trust entries preserved. Homebrew developer mode was restored to
its prior disabled state. The installed tools remain available.
