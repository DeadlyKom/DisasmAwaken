"""Уточнение доказанного R State0C, инструкции и размещение не меняются."""
from CheckIntro import ROOT
import json


def main():
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ActionClass18ProximityVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['exact_registers_including_r'] and proof['total_cases']==958
    pending={}
    replacements=(('сверены регистры кроме R, все восемь банков','сверены все регистры с R, все восемь банков'),
                  ('R добавляет 2 M1 к стоимости ребёнка, точный R ребёнка пока не доказан',
                   'R добавляет 2 M1 к стоимости ребёнка, точный R композиции проверен моделью State0E'))
    for name in ('Tools/Disasm/Research/ActionClass18ProximityFacts.py','Source/Action/HandleClass18Proximity.asm'):
        path=ROOT/name;before=path.read_bytes();text=before.decode('utf-8')
        for old,new in replacements:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        pending[path]=(before,text.encode('utf-8'))
    path=ROOT/'Docs/ActionClass18Proximity.md';before=path.read_bytes();text=before.decode('utf-8')
    for old,new in (('регистры кроме R, все восемь банков RAM','все регистры, включая R, все восемь банков RAM'),
                    ('списка, точный R, T, IRQ','списка, T, IRQ'),
                    ('точный R дальнего ребёнка пока не доказан','точный R всей композиции проверен моделью State0E')):
        assert text.count(old)==1; text=text.replace(old,new)
    pending[path]=(before,text.encode('utf-8'))
    for prefix,part in (('Candidates/ActionClass18Refresh',1),('History/BeforeActionClass18Refresh',0)):
        folder=ROOT/'Tools/Disasm/Research'/prefix;assert not folder.exists()
        for path,values in pending.items():
            target=folder/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(values[part])
    for path,(before,after) in pending.items():assert path.read_bytes()==before
    for path,(before,after) in pending.items():path.write_bytes(after)
    print(json.dumps(dict(passed=True,files=len(pending),assembly_executed=False)))


if __name__=='__main__':main()
