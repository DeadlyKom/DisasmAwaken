"""Уточнение проверки R State0D без изменения инструкций и физических байтов."""
import json
from CheckIntro import ROOT


def main():
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionSelectedRecordProximityVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases']==1024 and proof['exact_registers_including_r']
    changes={
        'Tools/Disasm/Research/ActionSelectedRecordProximityFacts.py':(
            ('сверены регистры кроме R, восемь банков RAM','сверены все регистры с R, восемь банков RAM'),
            ('все возможные данные записей, точный R, аппаратные IRQ','все возможные данные записей, аппаратные IRQ')),
        'Source/Action/HandleSelectedRecordProximity.asm':(
            ('сверены регистры кроме R, восемь банков RAM','сверены все регистры с R, восемь банков RAM'),
            ('все возможные данные записей, точный R, аппаратные IRQ','все возможные данные записей, аппаратные IRQ')),
        'Docs/ActionSelectedRecordProximity.md':(
            ('Регистры кроме R, все восемь банков RAM','Все регистры с R, все восемь банков RAM'),
            ('точный R, T, IRQ, сборка','T, IRQ, сборка')),
    }
    pending={}
    for name,replacements in changes.items():
        path=ROOT/name;before=path.read_bytes();text=before.decode('utf-8')
        for old,new in replacements:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        pending[path]=(before,text.encode('utf-8'))
    for prefix,part in (('Candidates/ActionSelectedProximityRefresh',1),('History/BeforeActionSelectedProximityRefresh',0)):
        folder=ROOT/'Tools/Disasm/Research'/prefix;assert not folder.exists()
        for path,values in pending.items():
            target=folder/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(values[part])
    for path,(before,after) in pending.items():assert path.read_bytes()==before
    for path,(before,after) in pending.items():path.write_bytes(after)
    print(json.dumps(dict(passed=True,files=len(pending),assembly_executed=False)))


if __name__=='__main__':main()
