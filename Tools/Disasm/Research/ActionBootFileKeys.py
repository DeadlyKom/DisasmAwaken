"""Шесть физических ключей загрузчика полёта после переноса в 4200."""
import re

PATH = 'Source/ActionBoot/Data/FileKeys.asm'
KEYS = (('Voxal', 'VOXAL   '), ('Voxal0', 'VOXAL0  '),
        ('Control', 'CONTROL '), ('Control0', 'CONTROL0'),
        ('Panel', 'PANEL   '), ('Object3D', 'OBJECT3D'))


def render(raw, *, keys=KEYS, module='ActionBootFileKeys', origin=0x42D0,
           document='ActionBootFileKeys', title='ключи загрузчика полёта'):
    assert len(raw) == len(keys) * 9
    lines = ['                module ' + module,
             '                ; Документация [' + title + '](../../../Docs/' + document + '.md)',
             f'                assert $ == #{origin:04X}']
    labels = {}
    for index, (label, name) in enumerate(keys):
        assert raw[index*9:index*9+9] == name.encode('ascii') + b'C'
        code = (label+':').ljust(16) + 'FTrDosFileKey { { "' + name + '" }, #43 }'
        lines.append(code.ljust(80) + '; восемь символов имени с исходными пробелами и тип C, терминатора нет')
        labels[module+'.'+label] = origin + 9*index
    lines += [f'                assert $ == #{origin+len(raw):04X}', '                endmodule', '']
    return '\n'.join(lines), labels


def parse(text):
    code = '\n'.join(line.partition(';')[0] for line in text.splitlines())
    rows = re.findall(r'FTrDosFileKey\s*\{\s*\{\s*"([^"]*)"\s*\}\s*,\s*#([0-9A-F]{2})\s*\}', code)
    assert len(rows) == 6 and all(len(name)==8 for name, _ in rows)
    return b''.join(name.encode('ascii')+bytes([int(kind,16)]) for name, kind in rows)


def name_operands(region, function_address, operation):
    if (region,function_address)!=('ActionBoot',0x4200):
        return operation
    for index, (name, _) in enumerate(KEYS):
        operation = operation.replace(f'LD HL, #{0x42D0+9*index:04X}', 'LD HL, @ActionBootFileKeys.'+name)
    return operation
