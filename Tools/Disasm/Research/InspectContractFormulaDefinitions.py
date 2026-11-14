"""Проверка определений символов P/Q/U/S в постусловиях вычислителя смещений."""
import json
from CheckIntro import ROOT
from Contracts import CONTRACTS


def main():
    rows = json.loads((ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes())
    checked, missing = [], []
    for row in rows:
        contract = CONTRACTS.get((row['region'], row['address']))
        if not contract or not any('HL=(-Q)' in line for line in contract[1]):
            continue
        checked.append(row['path'])
        # Проверка только данного семейства формул, прочие обозначения и договоры не объявляются исчерпанными.
        if not any(all(token in line for token in ('P=', 'Q=floor', 'U=', 'S=')) for line in contract[3]):
            missing.append(row['path'])
    result = dict(method='offset_vector_formula_symbol_definition_presence',
        checked_paths=checked, checked_count=len(checked), missing=missing,
        passed=not missing, algebraic_correctness_proved=False,
        all_contract_symbols_checked=False, source_modified=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ContractFormulaDefinitionsInspection.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(checked=len(checked), missing=len(missing))))


if __name__ == '__main__':
    main()
