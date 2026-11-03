"""Публикация родительского маршрута шести шкал с честной квалификацией композиции."""
import json
from ClassifyActionRegionType import main,ROOT
import ActionPanelGaugesFacts as facts


def record_method():
    path=ROOT/'Tools/Disasm/Reports/ActionPanelGaugesClassification.json'
    report=json.loads(path.read_text('utf-8'))
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionPanelGaugesVerification.json').read_text('utf-8'))
    assert report['passed'] and proof['passed']
    count=report.pop('independent_model_cases',None)
    assert count is None or count==proof['total_cases']
    report.update(compositional_model_cases=proof['total_cases'],independent_complete_child_oracle=False,
        child_reports=['ControlsSixRowGaugeVerification.json','ActionGaugeWrapperVerification.json','ActionPreferredByteVerification.json'])
    path.write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    path=ROOT/'Docs/FunctionDetails/Action.md';text=path.read_text('utf-8')
    start=text.index('## UpdatePanelGauges\n');end=text.find('\n## ',start+4);end=len(text) if end<0 else end
    block=text[start:end].replace('Алгоритм, контракты и независимая модель','Алгоритм, контракты и композиционная проверка')
    path.write_bytes((text[:start]+block+text[end:]).encode('utf-8'))


if __name__=='__main__':
    main(facts,'ActionPanelGauges','ActionPanelGauges',facts.STATE_FIELDS)
    record_method()
