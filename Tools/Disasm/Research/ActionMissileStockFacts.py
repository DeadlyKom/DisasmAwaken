"""Выбор счётчика ракет и его адреса, разновидности двух запасов пока не установлены."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
FUNCTIONS={0x70ED:('SelectMissileStock','Выбор ненулевого приоритетного остатка ракет либо запасного счётчика с возвратом адреса')}
CONTRACTS={('Action',0x70ED):(
    ['HL, DE, BC и AF исходных числовых аргументов не задают',
     'ActionMissileStockState.Value содержит два доступных байтовых счётчика, Fallback перед Preferred',
     'исполняется перенесённое ядро ACTION, на CPU-стеке внешний возврат, IRQ не вмешиваются'],
    ['HL указывает на Preferred при его ненулевом значении, иначе на Fallback',
     'DE и BC сохраняются, A содержит значение выбранного счётчика',
     'F соответствует AND Preferred, на запасном пути F=54 независимо от возвращённого A',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2",
     'R увеличивается на 4 M1 при ненулевом Preferred и на 7 M1 при его нуле'],
    ['HL, AF, R'],
    ['Carry всегда сброшен, Z показывает нулевой Preferred, проверка наличия ракет вызывающим кодом отдельно выполняет AND A',
     'данный читатель не изменяет запас или CPU-стек, возвращённый HL используется для DEC (HL) после вызова по 706F',
     'роль остатка ракет подтверждается вызовом QueueNumberBank1 между фрагментами Осталось и ракет банка Controls',
     'виды двух запасов не установлены, их имена описывают только доказанный приоритет выбора',
     'все 65536 пар проверены на исходных байтах, обработчики пуска целиком этой моделью не исполнялись'])}
COMMENTS={
    0x70ED:(['Выбор адреса приоритетного остатка ракет, это второй байт физической пары.'],None),
    0x70F1:(['Проверка приоритетного значения, флаги этой проверки сохраняются при чтении запасного счётчика.'],None),
    0x70F2:([],'выход, если Preferred ненулевой, A и HL уже задают выбранный счётчик'),
    0x70F3:(['Выбор предыдущего физического байта Fallback вместе с адресом, повторной проверки флагов нет.'],None)}
FIELDS=(('Fallback',1,'выбирается при нулевом Preferred, вид этого запаса пока не установлен'),
        ('Preferred',1,'выбирается первым при ненулевом значении, вид этого запаса пока не установлен'))
TABLE=('ActionMissileStockState','Source/Action/Data/MissileStock.asm',0x3C12,0x3C14,
       'FMissileStock',FIELDS,('Value',))


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0x70ED:
        operation=operation.replace('LD HL, #9C13','LD HL, @ActionMissileStockState.Value.Preferred')
    return operation


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[выбор остатка ракет](../../../Docs/ActionMissileStock.md)'),labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionMissileStockState' and clean.pop(0)=='assert $ == #9C12'
    assert clean.pop(0)=='Value:          FMissileStock {'
    assert re.fullmatch(r'#[0-9A-F]{2},',clean.pop(0))
    assert re.fullmatch(r'#[0-9A-F]{2}',clean.pop(0))
    assert clean==['}','assert $ == #9C14','endmodule']
    return parse_records(text,TABLE,0x6000)
