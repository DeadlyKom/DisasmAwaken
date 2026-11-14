"""Условный вход распаковщика и проверка байта за его выходным HL."""
import json


TAG = 'IntroDetachedUnpackGate'
TITLE = 'условный вход и переходы за экранным потоком'
REGION = 'IntroUnpack'
SLOT = 3
LOCATION = 'перенесённый хвост AWAKEN.B банка 5'
PROOF = 'IntroScreenResourcesVerification'
CASES = 3
KEYS = {}
FUNCTIONS = {
    0x74EC: ('UnpackTailGate', 'Внутренний вызов распаковщика и проверка двух байтов после его возврата'),
}
ENDS = {0x74EC: 0x74FF}
LOCAL = {0x74F7: 'ProbeByte'}
MUTATIONS = ()

CONTRACTS = {('IntroUnpack', 0x74EC): (
    ['Действует контекст внутреннего ADD HL,DE распаковщика, при штатной подготовке HL=#6E3C и DE=#008F',
     'Экран и стек доступны по договору UnpackScreen, после возврата читаются (HL) и условно (HL+8)'],
    ['После обычного возврата распаковщика A=#FF, Z=0, первый JP Z пропускается',
     'При нуле по выходному HL второй JP Z передаёт управление по #68EE, SP остаётся входным',
     'Иначе IX получает выходной HL, AF задаётся байтом (HL+8) и сравнением с #43',
     'По #74FF продолжается JR Z, смещение по #7500 находится за физическим концом записи'],
    ['Рабочие регистры и экран по UnpackScreen, затем AF и IX, два байта ниже входного SP',
     'При переходе #68EE дальнейшие записи и стек зависят от состояния генерируемого писателя'],
    ['Штатная передача управления на этот вход не установлена',
     'В исходном потоке HL=#5AFF и (HL)=7, поэтому оба абсолютных перехода пропускаются'],
)}

COMMENTS = {
    0x74EC: (['Вход после подготовки контекста распаковщика.'], None),
    0x74EF: ([], 'переход, если распаковщик вернул Z=1, нормальный терминатор оставляет Z=0'),
    0x74F2: (['Проверка байта по HL, после нормального возврата INC A получает ноль.'], None),
    0x74F4: ([], 'переход, если по выходному HL лежит ноль, передать управление хвосту писателя'),
    0x74F7: (['Перенос выходного HL в IX для чтения соседнего байта.'], None),
    0x74FD: (['Проверка значения перед относительным переходом, код JR Z следует по #74FF.'], None),
}


def file_offset(address):
    return address - 0x4800


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return (operation.replace('#6E3C', '@IntroTailState.UnpackBody')
            .replace('#68EE', '@IntroTailState.WriterTail')
            .replace('#08', '@IntroTailState.ProbeOffset')
            .replace('#43', '@IntroTailState.ProbeValue'))


def prepare(pending, symbols, root):
    proof = json.loads((root / 'Tools/Disasm/Reports/IntroScreenResourcesVerification.json').read_bytes())
    attribute_jump = proof['detached_attribute_jump']
    assert attribute_jump['terminator_af_cases'] == 512 and not attribute_jump['first_jump_taken_on_return']
    assert [profile['written_words'] for profile in attribute_jump['generated_and_ungenerated_paths']] == [0, 15]
    assert proof['detached_relative_target_cases'] == 768
    path = root / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    anchor = '                module IntroTailState\n'
    assert text.count(anchor) == 1
    fields = (
        ('UnpackBody', 0x6E3C, 'вход после получения PC и подготовки смещения потока'),
        ('WriterTail', 0x68EE, 'исходный NOP, при построении становится записью слова из HL'),
        ('ProbeOffset', 8, 'смещение читаемого байта относительно выходного HL'),
        ('ProbeValue', 0x43, 'значение для условия относительного перехода'),
    )
    lines = []
    for name, value, comment in fields:
        symbol = f'IntroTailState.{name}'
        assert symbol not in symbols
        symbols[symbol] = value
        lines.append((name.ljust(16) + f'equ #{value:04X}').ljust(80) + f'; {comment}\n')
    pending[path] = text.replace(anchor, anchor + ''.join(lines)).encode('utf-8')
