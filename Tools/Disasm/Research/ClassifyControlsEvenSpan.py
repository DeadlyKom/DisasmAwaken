"""Публикация трёх физических частей доказанного динамического заполнителя."""
import ControlsEvenSpanFacts as facts
from ClassifyControlsTextDisplay import main, ROOT
import json
import re


def refine_comments():
    # Замена повторного пересказа одинаковых пар единым пояснением каждого динамического входа.
    for name,total,length in (('FillEvenSpanHead',24,30),('FillEvenSpanTail',36,18)):
        path = ROOT/('Source/Controls/'+name+'.asm')
        before = path.read_bytes()
        lines = before.decode('utf-8').splitlines()
        redundant = ('; выбор предыдущего байта той же страницы, заём не изменяет H',
                     '; сохранение байта заполнения в выбранной позиции')
        assert sum(line.strip() in redundant for line in lines) == total
        after = []
        for line in lines:
            if line.strip() in redundant:
                continue
            match = re.match(r'^(Entry|Fill\d+):',line)
            if match:
                count = length if match[1] == 'Entry' else int(match[1][4:])
                after.append('                ; динамический вход на '+str(count)+' байтов справа налево, заём младшего адреса не изменяет страницу')
            after.append(line)
        history = ROOT/('Tools/Disasm/Research/History/BeforeControlsEvenSpanComments/Source/Controls/'+name+'.asm')
        assert not history.exists()
        history.parent.mkdir(parents=True,exist_ok=True)
        history.write_bytes(before)
        assert path.read_bytes() == before
        path.write_text('\n'.join(after)+'\n',encoding='utf-8')


if __name__ == '__main__':
    proof = json.loads((ROOT/'Tools/Disasm/Reports/ControlsEvenSpanCodeClassification.json').read_text('utf-8'))
    assert proof['passed']
    # Регистрация дополнительных динамических входов, не меняющая существующие метки.
    path = ROOT/'Tools/Disasm/Reports/Symbols.json'
    before = path.read_bytes()
    symbols = json.loads(before)
    for address,name in facts.LOCAL.items():
        if name in ('ReadMode','SelectTail'):
            continue
        owner = 'FillEvenSpanHead' if address < 0xCECF else 'FillEvenSpanTail'
        key = 'Controls.'+owner+'.'+name
        assert key not in symbols and address not in (0xCEB7,0xCECF)
        symbols[key] = address
    history = ROOT/'Tools/Disasm/Research/History/BeforeControlsEvenSpanLabels/Tools/Disasm/Reports/Symbols.json'
    assert not history.exists()
    history.parent.mkdir(parents=True,exist_ok=True)
    history.write_bytes(before)
    assert path.read_bytes() == before
    path.write_text(json.dumps(symbols,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    main(facts,'ControlsEvenSpan','ControlsEvenSpan',(
        ('TailOffset',0xCEB4,'изменяемое знаковое смещение JR'),
        ('Mode',0xD18B,'общий байт режима, Z возвращает его нулевое состояние')))
