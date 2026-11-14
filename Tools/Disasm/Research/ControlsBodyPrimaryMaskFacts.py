"""Вариант малого контура с входом в операнд и продолжение большого растра."""

TAG = 'ControlsBodyPrimaryMask'
TITLE = 'основная затравка малого тела и режим 1 большого растра'
PROOF = 'ControlsBodyDrawVerification'
REGION = 'Controls'
SLOT = 22
LOCATION = 'банк 1'
CASES = 91711
KEYS = {}
FUNCTIONS = {0xD227: ('DrawBodyPrimaryMask', 'Выбор основной затравки малого тела и режима 1 большого растра')}
ENDS = {0xD227: 0xD232}
CONTINUATIONS = {0xD227: 0xD232}
LOCAL = {}
MUTATIONS = ()

CONTRACTS = {('Controls', 0xD227): (
    ['готовая FBodyProjection.Value, рисунок в D240 и режим малого рисователя по CEF9',
     'банк 1 выбран, стек и рабочие области доступны по договорам DrawSmallBody и CallLargeCircle, IRQ не вмешивается'],
    ['при A малого рисователя меньше 9 его выход сохранён, F заменён сравнением CP 09',
     'при A не меньше 9 записан Mode=1, исполнение продолжается в CallLargeCircle без отдельного JP',
     'при полном возврате SP увеличен на два, страница сохранена, портов нет'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, R, растр, маски, рабочая запись круга, изменяемые операнды и до шестнадцати временных байтов CPU-стека'],
    ['наложенный PrimaryEntry малого рисователя исполняет AF как XOR A, A\'=0 выбирает Primary',
     'Row00 после построения всё равно обновляется из Alternate, разные затравки не объединяются',
     'выбор большого пути проверяет возвращённый A, а не повторно читает Radius',
     'в 45365 сценариях сверены регистры кроме R, все банки и кратность непиксельных записей',
     'штатный вызов D227 пока не установлен'],
)}

COMMENTS = {
    0xD227: (['Вызов малого рисователя через наложенный вход с нулевым селектором затравки.'], None),
    0xD22A: (['Проверка возвращённого A относительно первого большого радиуса.'], None),
    0xD22C: ([], 'выход, если A меньше 9, результат малого пути окончателен'),
    0xD22D: (['Установка режима 1 для общего большого рисователя.'], None),
}


def file_offset(address):
    return address - 0xC000


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return (operation.replace('#D9DF', '@SmallBodyConst.PrimaryEntry')
            .replace('CP #09', 'CP @SmallBodyConst.RadiusLimit')
            .replace('LD A, #01', 'LD A, @SmallBodyConst.LargeModePri')
            .replace('(#D18C)', '(@ControlsCircleWork.Value.Mode)'))


def prepare(pending, symbols, root):
    alias = 'SmallBodyConst.PrimaryEntry'
    constant = 'SmallBodyConst.LargeModePri'
    assert alias not in symbols and constant not in symbols
    assert symbols['Controls.DrawSmallBody.Entry'] == 0xD9DE
    symbols.update({alias: 0xD9DF, constant: 1})

    path = root / 'Source/Controls/DrawSmallBody.asm'
    source = path.read_text('utf-8')
    instruction = 'Entry:          LD A, #AF\n'
    binding = '                ; SmallBodyConst.PrimaryEntry указывает на байт AF, на этом входе выполняется XOR A.\n'
    assert source.count(instruction) == 1
    pending[path] = source.replace(instruction, instruction + binding).encode('utf-8')

    path = root / 'Includes/Const/Include.inc'
    source = path.read_text('utf-8')
    section = '                module SmallBodyConst\n'
    binding = ('LargeModePri    equ #01'.ljust(80)
               + '; большой растр после малого профиля с основной затравкой\n'
               + 'PrimaryEntry    equ #D9DF'.ljust(80)
               + '; вход на AF, выполняется XOR A и выбирается основная затравка\n'
               + '                assert PrimaryEntry == @Controls.DrawSmallBody.Entry + 1\n')
    assert source.count(section) == 1
    pending[path] = source.replace(section, section + binding).encode('utf-8')

    path = root / 'Source/Files/22_CONTROL0.inc'
    source = pending[path].decode('utf-8')
    include = '                include "../Controls/CallLargeCircle.asm"'
    assert source.count(include) == 1
    pending[path] = source.replace(include, include + ' ; (1) жёсткий порядок, последовательное исполнение').encode('utf-8')
