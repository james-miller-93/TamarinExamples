# Validation record

Prepared 2026-10-31 against original commit
`57695c888ddd487c944f6ae6b804204545e6671a`.

- Original protocol rules and security formulas were compared after removing
  comments and whitespace and excluding the two new `HonestRun` lemmas: identical.
- Python regression tests exercise result validation, incomplete or duplicate
  results, warnings, failed processes, timeouts, missing tools, and version errors.
- Python formatting, lint, and type checks pass under Python 3.13.14.
- `python3 check_models.py` exits 2 with an actionable missing-Tamarin message.

## Prover execution is pending

No Tamarin parse, well-formedness check, or proof result is claimed for this revision.
Neither Tamarin nor Maude was installed before preparation. An installation from
the officially documented Homebrew tap stopped because Homebrew refused to load
the Maude formula from a tap it did not yet trust. No extra trust permission was
granted. Tamarin's formula was registered as trusted by the installer, and the
official tap was added; the prover installation did not complete.

The intended versions are Tamarin 1.12.0 and Maude 3.5.1. Once these are available,
run `python3 check_models.py`, inspect the retained logs, and update this record
with actual outcomes. Do not interpret the expected-results table as verified proofs.
