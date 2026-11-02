"""Публикация шестибайтовой обёртки с проверенными физическими банками."""
import ControlsParameterActivationFacts as facts
from ClassifyControlsTextDisplay import main
from ClassifyControlsTextDisplay import ROOT
import json


def record_method():
    path = ROOT/'Tools/Disasm/Reports/ControlsParameterActivationClassification.json'
    report = json.loads(path.read_text('utf-8'))
    assert report['passed']
    cases = report.pop('independent_model_cases',report.get('compositional_model_cases'))
    assert cases==1036
    report.update(compositional_model_cases=cases,independent_complete_child_oracle=False,
        independently_checked_children=['ControlsParameterTablesVerification.json',
            'ActionApplyParametersVerification.json','ActionParameterActivationVerification.json'])
    path.write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))


if __name__=='__main__':
    main(facts,'ControlsParameterActivation','ControlsParameterActivation',())
    record_method()
