"""Физический четырёхбайтовый маркер TR-DOS после логического BASIC, без изменения каталога."""
from collections import Counter
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    reports = ROOT / 'Tools/Disasm/Reports'
    read = lambda name: json.loads((reports / (name + '.json')).read_text(encoding='utf-8'))
    sm, symbols, inventory = (read(name) for name in ('SourceMap', 'Symbols', 'Inventory'))
    old = next(item for item in sm if item['slot'] == 3 and item['offset'] == 119)
    old_path = ROOT / old['path']
    raw = old_path.read_bytes()
    assert old['kind'] == 'unclassified' and len(raw) == 137 and raw[:4] == b'\x80\xAA\x14\x00'
    path = 'Source/Basic/Data/Autostart.asm'
    tail = 'Source/Resources/03_AWAKEN/UnknownAfterBasicAutostart.bin'
    text = '''                module BasicProgramAutostart
                ; Документация [автозапуск BASIC](../../../Docs/BasicProgram.md)
                ; Здесь используются файловые смещения, маркер не является продолжением BASIC в RAM.
                assert $ == #0077
Entry:          FTrDosBasicAutostart {
                    #80,                                                        ; Marker80, первая часть сигнатуры
                    #AA,                                                        ; MarkerAA, вторая часть сигнатуры
                    #0014                                                       ; LineNumber, строка 20 содержит RANDOMIZE USR 23873
                }
                assert $ == #007B
                endmodule
'''
    pending = {ROOT / path: text.encode('utf-8'), ROOT / tail: raw[4:]}
    sm[sm.index(old):sm.index(old) + 1] = [dict(old, length=4, kind='typed_data', path=path,
        sha256=hashlib.sha256(raw[:4]).hexdigest()), dict(old, offset=123, length=133, path=tail,
        sha256=hashlib.sha256(raw[4:]).hexdigest())]
    symbols['BasicProgramAutostart.Entry'] = 119
    inventory['ranges_by_kind'] = dict(Counter(item['kind'] for item in sm))
    sizes = Counter()
    for item in sm:
        sizes[item['kind']] += item['length']
    inventory['physical_bytes_by_kind'] = dict(sizes)
    for name, value in (('SourceMap', sm), ('Symbols', symbols), ('Inventory', inventory)):
        pending[reports / (name + '.json')] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    path = ROOT / 'Source/Files/03_AWAKEN.inc'
    text = path.read_text(encoding='utf-8')
    needle = '                incbin "../Resources/03_AWAKEN/UnclassifiedBasicSectorTail.bin"'
    assert text.count(needle) == 1
    text = text.replace(needle, '                include "../Basic/Data/Autostart.asm"\n'
        '                assert $ == #007B\n'
        '                ; Следующие 133 байта имеют неизвестное назначение и сохраняются без изменений.\n'
        '                incbin "../Resources/03_AWAKEN/UnknownAfterBasicAutostart.bin"')
    pending[path] = text.encode('utf-8')
    path = ROOT / 'Includes/Structs/Include.inc'
    text = path.read_text(encoding='utf-8')
    assert 'struct FTrDosBasicAutostart' not in text
    block = '''                struct FTrDosBasicAutostart
Marker80        db #80                                                          ; первый байт сигнатуры автозапуска, не самостоятельный флаг
MarkerAA        db #AA                                                          ; второй байт сигнатуры автозапуска
LineNumber      dw #0000                                                        ; номер первой выполняемой строки BASIC, little-endian
                ends
                assert FTrDosBasicAutostart == #04

'''
    pending[path] = text.replace('                endif', block + '                endif').encode('utf-8')
    path = ROOT / 'Tools/Disasm/VerifySources.py'
    text = path.read_text(encoding='utf-8')
    marker = '    # Проверка трёх физических фаз и вложенных полей создаваемого узла очереди.'
    assert text.count(marker) == 1
    hook = '''    # Проверка реального служебного маркера автозапуска сразу после логического BASIC.
    autostart=(ROOT/'Source/Basic/Data/Autostart.asm').read_text('utf-8')
    values=re.search(r'Entry:\\s+FTrDosBasicAutostart\\s*\\{([^}]+)\\}', '\\n'.join(line.partition(';')[0] for line in autostart.splitlines()))[1]
    fields=[int(value.strip()[1:],16) for value in values.split(',')]
    assert fields==[0x80,0xAA,20] and sources[3][119:123]==bytes((fields[0],fields[1],fields[2]&255,fields[2]>>8))
    assert symbols['FTRDOSBASICAUTOSTART']==4 and symbols['FTRDOSBASICAUTOSTART.LINENUMBER']==2
    assert symbols['BASICPROGRAMAUTOSTART.ENTRY']==119

'''
    pending[path] = text.replace(marker, hook + marker).encode('utf-8')
    path = ROOT / 'Docs/BasicProgram.md'
    text = path.read_text(encoding='utf-8')
    text += '''
## Служебный автозапуск

Сразу после 119 логических байтов лежит `80 AA 14 00`. Это сигнатура
автозапуска TR-DOS и слово строки 20, а не ещё одна BASIC-строка.
Формат подтверждает [реализация SAVETRD](https://github.com/z00m128/sjasmplus/blob/master/sjasm/io_trd.cpp)
и [официальное описание директивы](https://z00m128.github.io/sjasmplus/documentation.html#po_savetrd).
Справочник подтверждает формат, наличие и значение маркера установлены
по фактическим байтам данного образа.

[Autostart.asm](../Source/Basic/Data/Autostart.asm) хранит реальный
FTrDosBasicAutostart со строкой #0014. Адрес метки является файловым
смещением #0077, исполняемый адрес RAM для этих четырёх байтов не
назначается. Строка 20 выбирает исходный USR #5D41. Следующие 133 байта
первого сектора остаются явно неизвестными. Каталог и его исходное
число 45 секторов не менялись.
'''
    pending[path] = text.encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/BasicAutostart'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeBasicAutostart'
    assert not candidate.exists() and not history.exists()
    before = {path: path.read_bytes() if path.exists() else None for path in (*pending, old_path)}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, original in before.items():
        assert path.read_bytes() == original if original is not None else not path.exists()
        if original is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(original)
    for path, raw in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == '.json':
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix='basic-autostart-', suffix='.tmp', delete=False) as output:
                temporary = Path(output.name)
                output.write(raw)
            try:
                os.replace(temporary, path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        else:
            path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert old_path.resolve().is_relative_to((ROOT / 'Source/Resources').resolve())
    assert old_path.read_bytes() == (history / old_path.relative_to(ROOT)).read_bytes()
    old_path.unlink()
    print('80 AA 14 00 оформлены служебной записью автозапуска строки 20, следующий хвост сохранён')


if __name__ == '__main__':
    main()
