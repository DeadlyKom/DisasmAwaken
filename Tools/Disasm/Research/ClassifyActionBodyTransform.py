"""Оформление двух участков вокруг проверенного восстановления стека."""
import json
from ClassifyActionRegionType import ROOT, main
import ActionBodyTransformFacts as facts


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    names = ('ActionPrepareBodyTransformVerification', 'ActionPublishBodyTransformVerification')
    proofs = [json.loads((reports / (name+'.json')).read_text(encoding='utf-8')) for name in names]
    assert all(proof['passed'] for proof in proofs)
    summary = dict(passed=True, total_cases=sum(proof['total_cases'] for proof in proofs),
                   component_reports=list(names), aggregate_boundary_and_continuation_checks=True, assembly_executed=False)
    (reports / 'ActionBodyTransformVerification.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    main(facts, 'ActionBodyTransform', 'ActionPrepareBodyTransform', ())
