"""Физические указатели состояний EF50..EF7B перед кодом EF7C."""
from PreviewSceneTables import render as render_records, parse as parse_records

FIELDS = (('Handler', 2, 'исходный адрес обработчика состояния, проверка цели выполняется отдельно'),)
TABLE = ('ActionObjectStateHandlers', 'Source/Action/Data/ObjectStateHandlers.asm', 0x8F50, 0x8F7C,
         'FObjectStateHandler', FIELDS, tuple(f'State{index:02X}' for index in range(22)))
KNOWN_HANDLERS = {0xF51E: 'Action.UpdatePreferredClass18.Entry',
                  0xEFB5: 'Action.AdvanceObjectPhaseWait.Entry',
                  0xEF7D: 'Action.AdvanceObjectOffsetRise.Entry',
                  0xEF9A: 'Action.AdvanceObjectOffsetFall.Entry'}
STRUCT = ('\n                ; Физический указатель обработчика состояния объекта\n'
          '                struct FObjectStateHandler\n'
          + 'Handler'.ljust(16) + 'dw #0000'.ljust(64) + '; адрес в банке ACTION\n'
          + '                ends\n                assert FObjectStateHandler == 2\n\n')


def render(source):
    text, labels = render_records(source, TABLE, 0x6000)
    text = text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[выбор обработчика состояния](../../../Docs/ActionObjectStateDispatch.md)')
    lines = []
    for line in text.splitlines():
        code, separator, note = line.partition(';')
        for address, name in KNOWN_HANDLERS.items():
            literal = '#'+format(address, '04X')
            if code.strip() == literal:
                assert separator
                line = code.rstrip().replace(literal, '@'+name).ljust(80)+';'+note
                break
        lines.append(line)
    return '\n'.join(lines)+'\n', labels


def parse(text):
    for address, name in KNOWN_HANDLERS.items():
        text = text.replace('@'+name, '#'+format(address, '04X'))
    return parse_records(text, TABLE, 0x6000)
