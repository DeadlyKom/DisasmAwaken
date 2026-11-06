"""Публикация физических продолжений и четырёх разобранных входов, общий результат 383744 сценария."""
from importlib import import_module
import json
import sys
from ClassifyControlsTextDisplay import ROOT
from PublishActionRawFunction import main as raw
from ClassifyActionRegionType import main as classify

if __name__=='__main__':
    assert sys.argv[1:] in ([],['--resume-after-chance'])
    resume=bool(sys.argv[1:])
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionPreferredRecordVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==383744 and proof['exact_registers_including_R']
    for tag,start,end in (('ActionPreferredApply',0xF557,0xF572),('ActionPreferredChance',0xF527,0xF535),
                          ('ActionPreferredZeroBridge',0xF53F,0xF541),('ActionPreferredSevenBridge',0xF54B,0xF54D)):
        if resume and start in (0xF557,0xF527):
            completed=json.loads((ROOT/f'Tools/Disasm/Reports/{tag}Classification.json').read_text('utf-8'))
            assert completed['passed'] and completed['model_cases']==67584
            continue
        result=dict(proof,total_cases=proof['cases_by_entry'][hex(start)],parent_total_cases=proof['total_cases'],entry=start)
        (ROOT/f'Tools/Disasm/Reports/{tag}Verification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
        facts=import_module(tag+'Facts');original=facts.name_operands
        def published_operands(region,address,operation,original=original):
            operation=original(region,address,operation)
            # Сохранение существующих имён до единой финальной классификации четырёх входов.
            from ActionPreferredDispatchFacts import FUNCTIONS
            for target,(name,_) in FUNCTIONS.items():
                operation=operation.replace('@Action.'+name+'.Entry','@Action.Unknown'+format(target,'04X')+'.Entry')
            return operation
        facts.name_operands=published_operands
        raw(facts,tag,start,end,result['total_cases'])
    result=dict(proof,total_cases=sum(proof['cases_by_entry'][hex(a)] for a in (0xF51E,0xF535,0xF541,0xF54D)),parent_total_cases=proof['total_cases'])
    (ROOT/'Tools/Disasm/Reports/ActionPreferredDispatchVerification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8')
    classify(import_module('ActionPreferredDispatchFacts'),'ActionPreferredDispatch','ActionPreferredRecord',state_fields=())
