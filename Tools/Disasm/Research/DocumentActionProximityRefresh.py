"""Точные границы проверки R двух композиций без изменения инструкций игры."""
import json
from CheckIntro import ROOT


def main():
    pairs=(
        ('собственный перенос аргументов не пишет RAM и добавляет 27 M1, точный R всей геометрической композиции не доказан',
         'собственный перенос аргументов не пишет RAM и добавляет 27 M1, CALL геометрии добавляет ещё один M1'),
        ('в композиции сверены регистры кроме R, все восемь банков, значения и кратность записей и оба OUT',
         'в 512 композиционных сценариях сверены все регистры с R, восемь банков, значения и кратность записей и оба OUT'),
        ('точные регистры кроме R дальнего вычислителя, восемь банков, кратность записей и реальные порты проверены, R доказан в 103584 сценариях',
         'точные регистры с R, восемь банков, кратность записей и реальные порты проверены во всех 106496 сценариях, включая дальний вычислитель'),
        ('полное произведение входов, R дальнего вычислителя, аппаратные IRQ',
         'полное произведение входов, аппаратные IRQ'),
    )
    files=('Tools/Disasm/Research/ActionSelectedRecordStepFacts.py',
           'Tools/Disasm/Research/ActionLinkedProximityFacts.py',
           'Source/Action/StepCodesTowardRecord.asm',
           'Source/Action/HandleLinkedRecordProximity.asm')
    pending={}
    # Проверка доказательств до изменения описаний, границы моделей остаются прежними.
    for tag,count,key in (('ActionSelectedRecordStep',393728,'full_composed_r_proved'),
                          ('ActionLinkedProximity',106496,'far_geometry_R_proved')):
        proof=json.loads((ROOT/f'Tools/Disasm/Reports/{tag}Verification.json').read_text('utf-8'))
        assert proof['passed'] and proof['total_cases']==count and proof[key]
    for name in files:
        path=ROOT/name;before=path.read_bytes();text=before.decode('utf-8')
        for old,new in pairs:
            if old in text:text=text.replace(old,new)
        assert text!=before.decode('utf-8'),name
        pending[path]=(before,text.encode('utf-8'))
    for name,replacements in (
        ('Docs/ActionSelectedRecordStep.md',(
            ('из-за временных стеков дочерних процедур. Точный R всей геометрии\nотдельно не доказан, собственные 27 M1 обёртки проверены точно.',
             'из-за временных стеков дочерних процедур. Проверены собственные 27 M1\nобёртки, один M1 вызова геометрии и точный R всей композиции на 512 профилях.'),
            ('геометрии и шага, сверены регистры кроме R, восемь банков RAM,',
             'геометрии и шага, сверены все регистры, включая R, восемь банков RAM,'))),
        ('Docs/ActionLinkedProximity.md',(
            ('кратность записей и настоящие порты. R доказан в 103584 сценариях,\nR дальнего вычислителя не объявляется установленным. Максимальная',
             'кратность записей и настоящие порты. Точный R проверен во всех 106496\nсценариях, включая дальний вычислитель. Максимальная'),)),
    ):
        path=ROOT/name;before=path.read_bytes();text=before.decode('utf-8')
        for old,new in replacements:
            assert text.count(old)==1,(name,old);text=text.replace(old,new)
        pending[path]=(before,text.encode('utf-8'))
    # Создание кандидата отдельно от текущих ручных исходников перед публикацией.
    for prefix,part in (('Candidates/ActionProximityRefresh',1),('History/BeforeActionProximityRefresh',0)):
        folder=ROOT/'Tools/Disasm/Research'/prefix;assert not folder.exists()
        for path,values in pending.items():
            target=folder/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(values[part])
    # Проверка отсутствия параллельных изменений перед точечной записью комментариев.
    for path,(before,after) in pending.items():assert path.read_bytes()==before
    for path,(before,after) in pending.items():path.write_bytes(after)
    print(json.dumps(dict(passed=True,files=len(pending),assembly_executed=False)))


if __name__=='__main__':main()
