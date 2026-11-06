"""Отдельная публикация возвратного хвоста и классификация точного контракта косвенной передачи."""
import json
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main as publish
from ClassifyActionRegionType import main as classify
import ActionBankedCallbackReturnFacts as tail
import ActionBankedCallbackFacts as dispatch


if __name__=='__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionBankedCallbackCombinedVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==786432
    for tag,entry in (('ActionBankedCallbackReturn',0x6D00),('ActionBankedCallback',0x6CEF)):
        path=ROOT/('Tools/Disasm/Reports/'+tag+'Verification.json')
        report=dict(proof,total_cases=proof['cases_by_entry'][hex(entry)],parent_total_cases=786432,entry=entry)
        # Проверка исходного полного отчёта до замены его уточнённым отчётом диспетчерского входа.
        if tag=='ActionBankedCallback':assert json.loads(path.read_text('utf-8'))==proof
        else:assert not path.exists()
        path.write_text(json.dumps(report,indent=2)+'\n','utf-8')
        if entry==0x6D00:publish(tail,tag,entry,entry+6,393216,allow_subrange=True)
        else:classify(dispatch,tag,'ActionBankedCallback',state_fields=dispatch.FIELDS,include_blocks=(
            ('Includes/Const/Include.inc','module ActionBankCallbackConst',dispatch.CONST_BLOCK),))
