"""Подготовка постоянного адреса приёмника перед условным входом #7497."""
import json


TAG = 'IntroAttributeScanPrefix'
DOCUMENT = 'IntroAttributeCountTail'
TITLE = 'фиксированный приёмник условного обхода атрибутов'
REGION = 'IntroUnpack'
SLOT = 3
LOCATION = 'перенесённый хвост AWAKEN.B банка 5'
PROOF = 'IntroAttributeCountTailVerification'
CASES = 256
KEYS = {}
FUNCTIONS = {
    0x7494: ('SetAttributeScanDest', 'Выбор #FF01 и последовательный вход в условный обход атрибутов'),
}
ENDS = {0x7494: 0x7497}
CONTINUATIONS = {0x7494: 0x7497}
LOCAL = {}
MUTATIONS = ()

CONTRACTS = {('IntroUnpack', 0x7494): (
    ['HL указывает на исходные счётчики, действуют требования ScanAttributeCountTail',
     'приёмник семи байтов #FF01..#FF07 доступен, входное DE не используется'],
    ['Перед продолжением по #7497 DE=#FF01, прочие пары, флаги и SP сохранены',
     'при HL=#FF00 следующий LDIR распространяет исходный L по восьми соседним байтам'],
    ['DE и R до входа в ScanAttributeCountTail, затем по договору продолжения'],
    ['Исходные три байта переносятся вместе с телом из #8F94, отдельного вызова или RET между файлами нет',
     'условный вход проверен в 256 сценариях, штатная передача управления сюда не установлена'],
)}

COMMENTS = {0x7494: (['Выбор постоянного приёмника для последующего копирования счётчиков.'], None)}


def file_offset(address):
    return address - 0x4800


def proof_cases(report):
    return report['prefix']['cases']


def name_operands(region, address, operation):
    if (region, address) not in CONTRACTS:
        return operation
    return operation.replace('#FF01', '@IntroTailState.ScanDest')


def prepare(pending, symbols, root):
    proof = json.loads((root / 'Tools/Disasm/Reports/IntroAttributeCountTailVerification.json').read_bytes())
    assert proof['prefix']['cases'] == 256 and proof['prefix']['destination'] == 0xFF01
    assert proof['inferred_prefix_and_displacement_alias']['counter_address'] == 0xFF00
    path = root / 'Includes/Variables/Include.inc'
    text = path.read_text('utf-8')
    anchor = '                module IntroTailState\n'
    assert text.count(anchor) == 1 and 'IntroTailState.ScanDest' not in symbols
    symbols['IntroTailState.ScanDest'] = 0xFF01
    line = 'ScanDest        equ #FF01'.ljust(80) + '; адрес приёмника семи байтов из хвоста вступления\n'
    pending[path] = text.replace(anchor, anchor + line).encode('utf-8')
    include = root / 'Source/Files/03_AWAKEN.inc'
    text = pending[include].decode('utf-8')
    entry = '                include "../IntroUnpack/ScanAttributeCountTail.asm"'
    assert text.count(entry) == 1
    pending[include] = text.replace(entry, entry.ljust(80) +
                                    '; (1) жёсткий порядок, последовательное исполнение').encode('utf-8')
