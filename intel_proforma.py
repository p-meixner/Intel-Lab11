"""Intel Lab 10: statements and positive-FCFE classroom valuation.

FY2025 filing baseline; forecast judgments and limitations in README.md.
USD millions except per-share values. Run: python intel_proforma.py
Break test: python intel_proforma.py --break-cash
"""

import math
import sys

# Historical source and forecast rationale: README.md.
# All forecasts are analyst classroom judgments, not Intel guidance.
GROWTH = 0.05
GROSS_MARGINS = [0.36, 0.38, 0.40, 0.42, 0.44]
SGA_RATIOS = [4624 / 52853] * 5  # Applied to revenue, not gross profit.
RD_RATIOS = [0.25, 0.24, 0.23, 0.22, 0.21]
DEPRECIATION_RATE = 10757 / 105414
INVENTORY_DAYS = 11618 / 34478 * 365
FLOOR_PLAN_RATIO = 0.0
IMPAIRMENT = 0.0
CAPEX = 17672.0
TAX_RATE = 0.21
OTHER_WC_RATE = 3839 / 52853  # Receivables / sales; other balances flat.
MIN_CASH = 5000.0
REVOLVER_LIMIT = 0.0  # No unverified borrowing capacity assumed.
REVOLVER_RATE = 0.06
REPAYMENT = 2499.0  # Annual scenario, not a verified maturity schedule.
BUYBACK = 0.0
FLOOR_PLAN_RATE = 0.0
DEBT_RATE = 0.04
COST_OF_EQUITY = 0.12
TERMINAL_GROWTH = 0.025
SHARES = 4994.0  # Year-end actual shares, not annual EPS weighted average.
COMPARISON_SHARES = 5250.0  # Rounded provider shares; presentation only.
MARKET_PRICE = 127.39  # Sept. 24, 2026, 4:00 p.m. EDT regular close.
NCI = 12079.0

OPENING = dict(revenue=52853.0, inventory=11618.0, ppe=105414.0,
               other_assets=211429.0 - 14265.0 - 11618.0 - 105414.0,
               cash=14265.0, floor_plan=0.0, debt=46585.0,
               other_liabilities=38484.0, equity=114281.0, nci=NCI,
               revolver=0.0, investments=23151.0)


def balance_gap(row):
    return (row['cash'] + row['inventory'] + row['ppe'] + row['other_assets']
            - row['floor_plan'] - row['debt'] - row['revolver']
            - row['other_liabilities'] - row['equity'] - row['nci'])


def assert_balanced(year, row):
    """Check independently computed balances; never plug cash to equity."""
    if any(not math.isfinite(value) for value in row.values()):
        raise ValueError(f'{year}: non-finite model value')
    gap = balance_gap(row)
    if abs(gap) > 1e-7:
        raise ValueError(f'{year}: balance-sheet gap {gap:.1f}')
    if row['cash'] < MIN_CASH - 1e-7:
        raise ValueError(f"{year}: cash below minimum; gap {row['cash'] - MIN_CASH:.1f}")
    if not -1e-7 <= row['revolver'] <= REVOLVER_LIMIT + 1e-7:
        raise ValueError(f'{year}: revolver outside 0 to {REVOLVER_LIMIT:.1f}')
    if row['investments'] < -1e-7:
        raise ValueError(f'{year}: short-term investments exhausted')
    if 'opening_cash' in row:
        expected_cash = (row['opening_cash'] + row['operating_cash_flow']
                         + row['capex_outflow'] + row['investment_sales']
                         + row['financing_cash_flow'])
        cash_gap = row['cash'] - expected_cash
        if abs(cash_gap) > 1e-7:
            raise ValueError(f'{year}: cash-flow reconciliation gap {cash_gap:.1f}')


def project(break_cash=False):
    rows = []
    opening = OPENING.copy()
    assert_balanced('FY2025', opening)
    for index, year in enumerate(range(2026, 2031)):
        sga_ratio = SGA_RATIOS[index]
        row = {'year': year}
        row['revenue'] = opening['revenue'] * (1 + GROWTH)
        row['gross_profit'] = row['revenue'] * GROSS_MARGINS[index]
        row['cost_of_sales'] = row['revenue'] - row['gross_profit']
        row['sga'] = row['revenue'] * sga_ratio
        row['rd'] = row['revenue'] * RD_RATIOS[index]
        row['depreciation'] = opening['ppe'] * DEPRECIATION_RATE
        row['impairment'] = IMPAIRMENT
        row['operating_income'] = (row['gross_profit'] - row['sga']
                                   - row['rd'] - IMPAIRMENT)
        row['interest'] = (opening['floor_plan'] * FLOOR_PLAN_RATE
                           + opening['debt'] * DEBT_RATE
                           + opening['revolver'] * REVOLVER_RATE)
        row['pretax'] = row['operating_income'] - row['interest']
        row['tax'] = max(0, row['pretax']) * TAX_RATE
        row['net_income'] = row['pretax'] - row['tax']
        row['inventory'] = row['cost_of_sales'] * INVENTORY_DAYS / 365
        row['floor_plan'] = row['inventory'] * FLOOR_PLAN_RATIO
        row['ppe'] = opening['ppe'] + CAPEX - row['depreciation']
        row['change_other_wc'] = OTHER_WC_RATE * (row['revenue'] - opening['revenue'])
        row['other_assets'] = opening['other_assets'] + row['change_other_wc'] - IMPAIRMENT
        row['repayment'] = REPAYMENT
        row['debt'] = opening['debt'] - row['repayment']
        row['other_liabilities'] = opening['other_liabilities']
        row['nci'] = opening['nci']
        row['equity'] = opening['equity'] + row['net_income'] - BUYBACK
        row['change_inventory'] = row['inventory'] - opening['inventory']
        row['change_floor_plan'] = row['floor_plan'] - opening['floor_plan']
        row['operating_cash_flow'] = (row['net_income'] + row['depreciation'] + IMPAIRMENT
                                      - row['change_inventory'] - row['change_other_wc']
                                      + row['change_floor_plan'])
        row['capex_outflow'] = -CAPEX
        row['fcfe'] = row['operating_cash_flow'] - CAPEX - row['repayment']
        cash_before_revolver = opening['cash'] + row['fcfe'] - BUYBACK
        # Fund cash shortfalls by selling existing short-term investments at par.
        # They are already included in other_assets; never count proceeds twice.
        row['investment_sales'] = min(max(0.0, MIN_CASH - cash_before_revolver),
                                      opening['investments'])
        row['investments'] = opening['investments'] - row['investment_sales']
        row['other_assets'] -= row['investment_sales']
        cash_before_revolver += row['investment_sales']
        if cash_before_revolver < MIN_CASH:
            change_revolver = min(MIN_CASH - cash_before_revolver,
                                  REVOLVER_LIMIT - opening['revolver'])
        else:
            change_revolver = -min(cash_before_revolver - MIN_CASH, opening['revolver'])
        row['change_revolver'] = change_revolver
        row['revolver'] = opening['revolver'] + change_revolver
        row['cash'] = cash_before_revolver + change_revolver
        row['repayment_outflow'] = -row['repayment']
        row['buyback_outflow'] = -BUYBACK
        row['financing_cash_flow'] = -row['repayment'] - BUYBACK + change_revolver
        row['opening_cash'] = opening['cash']
        row['change_cash'] = row['cash'] - opening['cash']
        row['assets'] = row['cash'] + row['inventory'] + row['ppe'] + row['other_assets']
        row['liabilities_equity'] = (row['floor_plan'] + row['debt'] + row['revolver']
                                      + row['other_liabilities'] + row['equity'] + row['nci'])
        if break_cash and year == 2026:
            row['cash'] = OPENING['cash']
        assert_balanced(f'FY{year}E', row)
        rows.append(row)
        opening = row
    return rows


def print_table(title, fields, rows):
    print(f'\n{title} (USD millions)')
    print(f"{'':32}" + ''.join(f"{'FY' + str(r['year']) + 'E':>13}" for r in rows))
    for label, key in fields:
        print(f'{label:32}' + ''.join(f'{r[key]:13.1f}' for r in rows))


def value_positive_fcfe(rows):
    """Lab convention, NOT a complete common-equity appraisal.

Negative funding requirements remain in statements. No value is assigned to
them here. Do not extrapolate negative terminal-year FCFE, or add back repayment
to manufacture a positive terminal base. No liquid-asset/NCI bridge is included.
"""
    for row in rows:
        assert_balanced(f"FY{row['year']}E", row)
    if COST_OF_EQUITY <= TERMINAL_GROWTH or SHARES <= 0:
        raise ValueError('Require cost of equity > terminal growth and positive shares')
    explicit = sum(max(0.0, r['fcfe']) / (1 + COST_OF_EQUITY) ** t
                   for t, r in enumerate(rows, 1))
    terminal = None
    if rows[-1]['fcfe'] > 0:
        terminal = (rows[-1]['fcfe'] * (1 + TERMINAL_GROWTH)
                    / (COST_OF_EQUITY - TERMINAL_GROWTH)
                    / (1 + COST_OF_EQUITY) ** len(rows))
    return explicit, terminal


def main():
    if any(arg != '--break-cash' for arg in sys.argv[1:]):
        raise SystemExit('Usage: python intel_proforma.py [--break-cash]')
    rows = project(break_cash='--break-cash' in sys.argv)
    print_table('Income statement', [
        ('Revenue', 'revenue'), ('Cost of sales', 'cost_of_sales'),
        ('Gross profit', 'gross_profit'), ('SG&A', 'sga'),
        ('R&D', 'rd'), ('Depreciation (embedded; memo)', 'depreciation'), ('Impairment', 'impairment'),
        ('Operating income', 'operating_income'), ('Interest', 'interest'),
        ('Pretax income', 'pretax'), ('Tax', 'tax'), ('Net income', 'net_income')], rows)
    print_table('Balance sheet', [
        ('Cash', 'cash'), ('Inventory', 'inventory'), ('PP&E', 'ppe'),
        ('Other assets', 'other_assets'),
        ('  Includes ST investments', 'investments'), ('Total assets', 'assets'),
        ('Floor plan', 'floor_plan'), ('Term debt', 'debt'), ('Revolver', 'revolver'),
        ('Other liabilities', 'other_liabilities'), ('Intel equity', 'equity'),
        ('Noncontrolling interests', 'nci'),
        ('Liabilities + equity', 'liabilities_equity')], rows)
    print_table('Cash flow statement', [
        ('Net income', 'net_income'), ('Add depreciation', 'depreciation'),
        ('Add impairment', 'impairment'), ('Increase inventory (subtract)', 'change_inventory'),
        ('Increase other WC (subtract)', 'change_other_wc'),
        ('Increase floor plan (add)', 'change_floor_plan'),
        ('Operating cash flow', 'operating_cash_flow'), ('Capital spending', 'capex_outflow'),
        ('Debt repayment', 'repayment_outflow'), ('Share buyback', 'buyback_outflow'),
        ('Revolver draw / (repayment)', 'change_revolver'),
        ('Financing cash flow', 'financing_cash_flow'),
        ('Short-term investment sales', 'investment_sales'), ('Change in cash', 'change_cash'),
        ('Opening cash', 'opening_cash'), ('Closing cash', 'cash'), ('FCFE', 'fcfe')], rows)
    print('\nChecks')
    for row in rows:
        assert_balanced(f"FY{row['year']}E", row)
        gap = balance_gap(row)
        print(f"FY{row['year']}E: balance gap = {0.0 if abs(gap) < 1e-7 else gap:.1f}; "
              f"cash >= {MIN_CASH:.1f}: PASS; cash-flow link: PASS; funding limits: PASS")
    print('\nFCFE status (negative amounts remain in the statements)')
    for row in rows:
        status = 'negative FCFE' if row['fcfe'] < 0 else 'nonnegative FCFE'
        print(f"FY{row['year']}E: {row['fcfe']:.1f} -- {status}")
    explicit, terminal = value_positive_fcfe(rows)
    value = explicit + (terminal if terminal is not None else 0.0)
    print('\nLAB 10 POSITIVE-CASH-FLOW COMPONENT ONLY; not a stock price target')
    print(f'PV of positive explicit FCFE (USD millions): {explicit:.2f}')
    if terminal is None:
        print('Terminal value: N/A -- 2030 FCFE is not positive; excluded, not estimated as zero.')
    else:
        print(f'PV of terminal value (USD millions): {terminal:.2f}')
    print(f'Positive-cash-flow component (USD millions): {value:.2f}')
    print(f'Lab value per share at FY2025 shares ({SHARES:.0f} million): ${value / SHARES:.2f}')
    print(f'Lab value per comparison share ({COMPARISON_SHARES:.0f} million, approximate): '
          f'${value / COMPARISON_SHARES:.2f}')
    print(f'Market: ${MARKET_PRICE:.2f}, Sept. 24, 2026, 4:00 p.m. EDT regular close.')
    print('Zero positive forecast cash flow does not mean Intel stock is worthless.')
    print('Full equity valuation remains unresolved; see README.md for scope and comparison limits.')


if __name__ == '__main__':
    main()
