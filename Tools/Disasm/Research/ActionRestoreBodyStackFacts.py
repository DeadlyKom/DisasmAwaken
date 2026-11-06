"""Восстановление CPU-стека перед обработкой результата проекции."""
FUNCTIONS = {0x6AAD: ('RestoreBodyStack', 'Восстановление настоящего SP после арифметического накопителя')}
LOCAL = {}
FALLTHROUGH = True
STATE_FIELDS = (('SavedSP', 0x6AAE, 'операнд LD SP,nn, записанный входом подготовки тела'),)
CONTRACTS = {('Action', 0x6AAD): (
    ['CPU-стек временно заменён арифметическим значением, SavedSP содержит настоящий SP от 6A6E'],
    ['SP восстановлен из SavedSP, флаги вычислителя и остальные пары сохраняются, исполнение продолжается по 6AB0'],
    ['SP и R, RAM и порты сохраняются'],
    ['один M1, обычного CALL и RET в этом фрагменте нет, 6AB0 должен следовать непосредственно'],
)}
COMMENTS = {0x6AAD: (['Восстановление настоящего CPU-стека перед проверкой переполнения в следующем фрагменте.'], None)}


def name_operands(region, address, operation):
    return operation


def qualify_mutations(modified, flow, functions, pieces):
    assert not any(item['region'] == 'Action' and item['writer'] == 0x6A98 for item in modified)
    modified.append(dict(region='Action', writer=0x6A98, target=0x6AAE, target_instruction=0x6AAD,
                         size=2, target_operation='LD SP,#0000', path='Source/Action/Unknown6A6E.asm'))
    modified.sort(key=lambda item: (item['region'], item['writer'], item['target']))
