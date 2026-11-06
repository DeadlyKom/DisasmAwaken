"""Публикация двух проверенных частей вычислителя смещения."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main
import ActionObjectOffsetVectorFacts as vector
import ActionObjectOffsetCoefficientsFacts as coefficients


if __name__ == '__main__':
    reports = ROOT/'Tools/Disasm/Reports'
    proof = json.loads((reports/'ActionObjectOffsetVectorVerification.json').read_text(encoding='utf-8'))
    assert proof['passed'] and proof['original_IX_restored']
    main(vector, 'ActionObjectOffsetVector', 0x6D06, 0x6D38, proof['total_cases'])
    summary = dict(passed=True, total_cases=proof['cases_by_entry']['B044'], shared_report='Tools/Disasm/Reports/ActionObjectOffsetVectorVerification.json')
    (reports/'ActionObjectOffsetCoefficientsVerification.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    main(coefficients, 'ActionObjectOffsetCoefficients', 0xB044, 0xB0E9, summary['total_cases'], allow_subrange=True)
