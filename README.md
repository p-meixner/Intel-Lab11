# Lab 11 — Intel pro-forma sensitivity

Question: Which assumptions drive my company's forecast and value, and what explains their effects?

Status: Code and numerical evidence complete. Student interpretation and post-run partner exchanges remain to be completed below. The pre-run revenue-growth prediction and reported partner discussion are preserved in [locked_prediction.md](locked_prediction.md).

## Inputs and comparison

All financial statement amounts are USD millions. Outputs are FY2030 operating profit and signed FCFE. Value per share is unavailable: the Lab 10 positive-only cash-flow component is not a defensible complete equity valuation. No negative cash flows are discarded and no terminal value is invented.

| Independent driver | Lower | Base | Higher | Years | Range rationale |
|---|---|---|---|---|---|
| Revenue growth | 4% annually | 5% annually | 6% annually | 2026–2030 | Student's labelled judgment: recovery one percentage point slower or faster; not guidance. |
| Gross margin | 35%, 37%, 39%, 41%, 43% | 36%, 38%, 40%, 42%, 44% | 37%, 39%, 41%, 43%, 45% | 2026–2030, respectively | AI-selected at the student's request: labelled judgment testing modestly weaker/stronger manufacturing recovery, one percentage point below/above each base-year margin. Not guidance or a statistical interval. |

Confirmation of the partner's pre-run review of the second range was not supplied; do not represent that step as completed.

## Numerical evidence

See [results.md](results.md) for the visible sensitivity table, signed differences, spans, valuation limitation and passing restored-base check. [sensitivity_output.txt](sensitivity_output.txt) contains every run's checks and full statement fields. [run_details.json](run_details.json) retains all actual inputs and statement details, including the base before and after. [base_inputs.json](base_inputs.json) preserves the separate original assumptions.

Each run uses a freshly loaded model and deep copies of the base inputs. Only the selected driver changes; all other independent assumptions reset to base. Linked statement quantities recalculate. Invalid runs are flagged and excluded from output spans. Accounting and restored-base tolerance is 0.0000001 USD million; display rounding is two decimals, so recomputing differences from displayed figures can differ by 0.01.

## Run and files

Keep all files in this folder together. From the course folder:

```text
python Intel-Lab11/sensitivity.py
```

Or from inside this folder:

```text
python sensitivity.py
```

The script uses only Python's standard library and regenerates the four result files. `intel_proforma.py` is an unchanged copy of the working Lab 10 model; the original Lab 10 folder is preserved. Its standalone valuation printout retains the Lab 10 convention; use the sensitivity results' N/A valuation treatment for Lab 11.

## Student completion — fill in from your analysis and actual exchanges

Additional reported partner feedback: “My partner was initially very curious and ultimately agreed with my analysis.” This reaction is also saved in the locked record. The specific post-run question and numerical check remain unreported.

Partner-range correction: the partner also used Intel, with FY2030 gross margins of 43% lower, 44% base and 45% higher. The earlier range was a typo; the corrected notes appear in the locked record.

1. Explain the actual versus predicted result in the appended section of the locked record. Explain whether it changes your valuation conclusion or research priority, including a reason if it does not.
2. Identify the larger operating-profit and FCFE driver **over these ranges**, using the spans in results.md. Trace a causal link through actual statement numbers. Explain how the chosen ranges limit the ranking.
3. Record partner exchange 2: the changed result and base checked, the recomputed difference, confirmation that other inputs stayed at base, and the question or correction. Record the check you performed on the partner's actual results.
4. Record partner exchange 3: question received about the ranges, your response, partner's summary, and why your companies might differ. Avoid comparing companies by raw dollar changes.
5. In your own words: What is one-at-a-time sensitivity? How can range selection affect the ranking? Why is this table not a forecast probability? Which result surprised you?

## GitHub checkout

Upload this entire `Intel-Lab11` folder to your own GitHub repository, excluding `__pycache__`. Submit the GitHub link to this README and to `sensitivity.py`; the README links to the supporting files, including the required model dependency. Local file links are not GitHub submission URLs. No upload has been performed.

## AI use

AI saved the student's reported pre-run prediction and partner discussion, selected the second driver/range at the student's request, built and ran the sensitivity wrapper, and prepared the numerical evidence. Student explanations and unreported partner exchanges have been left pending.
