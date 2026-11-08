"""Девять физических слов базиса в порядке старших байтов коэффициентов RenderSceneFrame."""
from PreviewSceneTables import render as render_records,parse as parse_records

TABLE=('ActionRenderBasis','Source/Action/Data/RenderBasis.asm',0x3B00,0x3B12,'FBasisWord',
       (('Low',1,'младший байт исходного слова базиса'),
        ('High',1,'старший байт слова, перед передачей в коэффициент 80 заменяется на 81')),
       tuple('C'+str(row)+str(column) for column in range(3) for row in range(3)))


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[физические слова базиса](../../../Docs/ActionRenderBasis.md)'),labels


def parse(text):return parse_records(text,TABLE,0x6000)


def structure():
    return '''
                ; Двухбайтовое слово базиса, не код доступности FActionRecord
                struct FBasisWord
Low             db #00                                                          ; младший байт слова базиса
High            db #00                                                          ; старший байт, RenderSceneFrame передаёт его с заменой 80 на 81
                ends
                assert FBasisWord == 2
                assert FBasisWord.Low == 0
                assert FBasisWord.High == 1
'''


def name_operands(region,address,operation):
    if (region,address) not in (('Action',0xE020),('Voxel',0xE500)):return operation
    for index,name in enumerate(TABLE[-1]):
        for offset,suffix in ((0,''),(1,'.High')):
            old='(#'+format(0x9B00+2*index+offset,'04X')+')'
            operation=operation.replace(old,'(@ActionRenderBasis.'+name+suffix+')')
    for index in range(3):
        operation=operation.replace('(#'+format(0x9B12+index,'04X')+')',
                                    '(@ActionRenderPhases.Value.Phase'+str(index)+')')
    return operation
