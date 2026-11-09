"""28 самостоятельных байтов правил и два последующих байта, одновременно являющиеся кодом."""
from PreviewSceneTables import render as render_records,parse as parse_records
FIELDS=(('Control',1,'биты 7..6, 00 прибавляет Current, ненулевой код сохраняет Current, смысл битов 5..0 не установлен'),)
TABLES=((17,0x5DC3,('ActionTractorCargoRules','Source/Action/Data/TractorCargoRules.asm',0x165A,0x1676,
    'FTractorCargoRule',FIELDS,tuple('Kind'+format(i,'02d') for i in range(28)))),)
BINDINGS=()
REQUIRED_REPORTS=('ActionTractorCollectVerification','ActionEjectCommandsVerification')
DOCUMENT='ActionTractorCollect'
TAG='ActionTractorCargoRules'


def validate_sources(sources):
    source=sources[17];expected=bytes([0]*17+[128]*3+[0]*3+[64]*3+[128,0])
    assert len(expected)==28 and source[0x165A:0x1676]==expected
    # Проверка двух правил с нормальными кодами 28 и 29, их байты остаются инструкцией следующего обработчика.
    assert source[0x1676:0x1679]==bytes.fromhex('3a 5f a8')
    assert 0x741D+28==0x7439 and 0x741D+29==0x743A
    return dict(physical_rule_records=28,code_data_alias_rules=2,
        code_data_alias_original_bytes='3a5f',aliases_emitted_twice=False,
        rule_index_bounds_check_present=False,full_gameplay_kind_domain_proved=False)


def render(source,origin,table):
    text,labels=render_records(source,table,origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[сбор объекта и перекрытие правил с кодом](../../../Docs/'+DOCUMENT+'.md)'),labels


def parse(text,origin,table):return parse_records(text,table,origin)


def structures():
    return ('                ; Исходный байт правила счётчика при сборе, младшие шесть битов не переименовываются в придуманные флаги\n'
        '                struct FTractorCargoRule\n'+
        'Control         db #00'.ljust(80)+'; поле 7..6, нуль учитывает количество в Current, ненулевое значение исключает\n'+
        '                ends\n                assert FTractorCargoRule == 1\n                assert FTractorCargoRule.Control == 0\n\n')
