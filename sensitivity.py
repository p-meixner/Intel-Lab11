"""Run from any directory: python Intel-Lab11/sensitivity.py.

Uses an unchanged copy of the Lab 10 engine. Standard library only.
Each run loads a fresh module and receives a deep copy of all base constants.
"""
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOLERANCE = 1e-7


def fresh_model():
    spec = importlib.util.spec_from_file_location('intel_run', HERE / 'intel_proforma.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def assumptions(model):
    return copy.deepcopy({k: v for k, v in vars(model).items() if k.isupper()})


def run(base, key=None, value=None):
    model = fresh_model()
    inputs = copy.deepcopy(base)
    if key:
        inputs[key] = copy.deepcopy(value)
    changed = [k for k in base if inputs[k] != base[k]]
    assert changed == ([key] if key and value != base[key] else [])
    for name, item in inputs.items():
        setattr(model, name, copy.deepcopy(item))
    checks = []
    rows = []
    original_check = model.assert_balanced

    def record_check(year, row):
        # Preserve even a failed row, allowing funding failures to be traced.
        if 'year' in row:
            rows.append(copy.deepcopy(row))
        try:
            original_check(year, row)
        except ValueError as error:
            checks.append(f'{year}: FAIL - {error}')
            raise
        checks.append(f'{year}: balance, cash floor, cash-flow link (forecast), funding limits PASS')

    model.assert_balanced = record_check
    error = None
    try:
        model.project()
    except ValueError as exc:
        error = str(exc)
    assert assumptions(model) == inputs, 'Model mutated inputs'
    return dict(inputs=inputs, changed_inputs=changed, rows=rows, checks=checks,
                valid=error is None, error=error)


def main():
    base = assumptions(fresh_model())
    (HERE / 'base_inputs.json').write_text(json.dumps(base, indent=2) + '\n', encoding='utf-8')
    before = run(base)
    assert before['valid'], before['error']
    drivers = {
        'GROWTH': [0.04, base['GROWTH'], 0.06],
        'GROSS_MARGINS': [[v - 0.01 for v in base['GROSS_MARGINS']],
                          base['GROSS_MARGINS'],
                          [v + 0.01 for v in base['GROSS_MARGINS']]],
    }
    records = {'base_before': before}
    lines = ['Intel Lab 11 sensitivity',
             'Outputs and signed changes: USD millions; final year: FY2030; cash flow: FCFE.',
             'Input percentages apply to FY2026-2030 in order.',
             'Value per share: N/A for every run. Full equity valuation remains unresolved.',
             'Negative FCFE retained; no positive-only valuation or invented terminal value.',
             f'Accounting and restored-base tolerance: {TOLERANCE} USD million.', '']
    table = ['| Driver | Case | Inputs (%) FY2026-2030 | Operating profit | Change | FCFE | Change | Status |',
             '|---|---|---|---:|---:|---:|---:|---|']
    spans = {}
    for key, values in drivers.items():
        valid = []
        for label, value in zip(['lower', 'base', 'higher'], values):
            result = run(base, key, value)
            records[f'{key}_{label}'] = result
            path = value if isinstance(value, list) else [value] * 5
            input_text = ', '.join(f'{v * 100:.2f}' for v in path)
            if result['valid']:
                final = result['rows'][-1]
                valid.append(final)
                result['deltas'] = {field: final[field] - before['rows'][-1][field]
                                    for field in ['operating_income', 'fcfe']}
                table.append(f"| {key} | {label} | {input_text} | {final['operating_income']:.2f} | "
                             f"{result['deltas']['operating_income']:+.2f} | {final['fcfe']:.2f} | "
                             f"{result['deltas']['fcfe']:+.2f} | PASS |")
            else:
                table.append(f"| {key} | {label} | {input_text} | N/A | N/A | N/A | N/A | INVALID: {result['error']} |")
        spans[key] = {field: max(r[field] for r in valid) - min(r[field] for r in valid)
                      for field in ['operating_income', 'fcfe']} if valid else None
        spans[key]['valid_runs'] = len(valid)
    after = run(base)
    records['base_after'] = after
    assert before['inputs'] == after['inputs'] == base
    assert after['valid']
    max_difference = max(abs(a[k] - b[k]) for a, b in zip(before['rows'], after['rows']) for k in a)
    assert len(before['rows']) == len(after['rows']) == 5 and max_difference <= TOLERANCE
    lines.extend(table)
    lines += ['', 'Output spans: maximum minus minimum across VALID runs only.']
    for key, span in spans.items():
        lines.append(f"{key}: operating profit {span['operating_income']:.2f}; FCFE {span['fcfe']:.2f}; valid runs {span['valid_runs']}/3.")
    lines += [f'\nRestored base: PASS; all inputs identical; maximum statement difference {max_difference:.10f}.']
    for name, result in records.items():
        lines += ['', name, 'Independent inputs changed: ' + (', '.join(result['changed_inputs']) or 'none')]
        lines.extend(result['checks'])
        lines.append('Full linked statement details (USD millions except year):')
        lines.extend(json.dumps(row, sort_keys=True) for row in result['rows'])
    output = '\n'.join(lines) + '\n'
    (HERE / 'sensitivity_output.txt').write_text(output, encoding='utf-8')
    (HERE / 'run_details.json').write_text(json.dumps(dict(runs=records, spans=spans), indent=2) + '\n', encoding='utf-8')
    (HERE / 'results.md').write_text('\n'.join(lines[:lines.index('base_before')]) + '\n', encoding='utf-8')
    print('\n'.join(lines[:lines.index('base_before')]))


if __name__ == '__main__':
    main()
