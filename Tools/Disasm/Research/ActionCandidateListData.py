"""Исходные десять пропусков и маркер FE списка кандидатов, не общий лимит всех runtime-списков."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLE=('ActionCandidateListData','Source/Action/Data/CandidateList.asm',0x401C,0x4027,'FCandidateCode',
       (('Code',1,'полный индекс 00..FD, FF означает пропуск, FE завершает список'),),
       tuple('Slot'+format(i,'02X') for i in range(10))+('EndMarker',))


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[исходный список кандидатов](../../../Docs/ActionCandidateList.md)'),labels


def parse(text):return parse_records(text,TABLE,0x6000)


def structure():
    return '''
                ; Полный числовой код элемента списка, отдельные битовые флаги не задаются
                struct FCandidateCode
Code            db #00                                                          ; 00..FD индекс записи, FF пропуск, FE конец списка
                ends
                assert FCandidateCode == 1
                assert FCandidateCode.Code == 0
'''
