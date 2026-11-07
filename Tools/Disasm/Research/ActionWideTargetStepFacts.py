"""Писатель шести операндов и точная подготовка шести аргументов геометрии."""
FUNCTIONS={0x7EB7:('StepRecordTowardWideVector','Обновление двух кодов записи по трём широким компонентам выбранной цели')}
LOCAL={};LABELS={};CONTINUATIONS={}
RENAMES={'Action.Unknown7EB7.Entry':'Action.StepRecordTowardWideVector.Entry'}
CONTRACTS={('Action',0x7EB7):(
    ['HL, DE, BC, AF входных аргументов не задают',
     'IX указывает FActionRecord с тремя словами Components, текущими OffsetPhase1/OffsetPhase2 и стабильным TargetCodeStep',
     'IY указывает три читаемые четырёхбайтовые компоненты в порядке little-endian',
     'таблицы LOG, EXP и SignedRatioCodes подготовлены как для EncodeHalfCoordinateDeltas, корень банка 1 доступен',
     '7FFD имеет одно из значений 00, 08, 10, 18, код и операнды доступны, CPU-стек допускает 16 дополнительных байтов',
     'IRQ не вмешиваются, исходные компоненты, таблицы и код не перекрывают рабочие записи и рамку стека'],
    ['HL, DE, BC, AF и два поля OffsetPhase1/OffsetPhase2 определены цепочкой ClampPatchedVectorWords и StepRecordTargetCodes',
     'Left0, Left1, Left2 равны насыщенным словам выбранного IY в исходном знаковом правиле бита 23',
     'Right0, Right1, Right2 равны исходным трём словам Components записи IX',
     'OffsetPhase1/OffsetPhase2 изменяются по разным исходным правилам шага TargetCodeStep, точные формулы в документации',
     "HL', DE', BC', AF' определены дочерней геометрией, IX, IY сохранены, SP=входной SP+2",
     'шесть операндов ClampPatchedVectorWords содержат копию исходных 12 байтов IY, финальный 7FFD=10',
     'I, IM, IFF сохраняются, две реальные записи порта 7FFD равны 11 и 10'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', R, 16 временных байтов CPU-стека, шесть операндов координат и операнды дочерней геометрии, OffsetPhase1/OffsetPhase2, 7FFD"],
    ['между чтением цели и геометрией исходные LD/PUSH/POP/EXX только размещают шесть аргументов без изменения координат',
     'конечный JP не создаёт нового возврата, StepRecordTargetCodes возвращает непосредственно внешнему вызывающему',
     'предел входа банкового корня 7FFE и недостижимость его плохой верхней области наследуются от EncodeHalfCoordinateDeltas',
     '338616 сценариев проверили реальные дочерние процедуры, все слова Components каждой позиции и граничные dword',
     'сопоставлены регистры кроме R, кратность записей, остаток CPU-стека, все банки RAM и реальные переключения страниц',
     'R, полное произведение входов, игровые единицы, IRQ, точные T, сборка и нативный запуск не доказаны'])}
COMMENTS={
0x7EB7:(['Чтение первой широкой компоненты выбранной цели, порядок байтов little-endian.'],None),
0x7EC3:(['Обновление пары исходных операндов первой компоненты ClampPatchedVectorWords.'],None),
0x7ECA:(['Чтение второй широкой компоненты выбранной цели.'],None),
0x7ED6:(['Обновление пары исходных операндов второй компоненты.'],None),
0x7EDD:(['Чтение третьей широкой компоненты выбранной цели.'],None),
0x7EE9:(['Обновление пары исходных операндов третьей компоненты.'],None),
0x7EF0:(['Преобразование трёх signed32 к словам с насыщением 7F00 и исходным знаком по биту 23.'],None),
0x7EF3:(['Сохранение второй и третьей левых координат для переноса в альтернативные регистры.'],None),
0x7EF5:(['Чтение первых двух правых координат из текущей записи IX.'],None),
0x7F01:(['Преобразование раскладки аргументов, основные HL/DE/BC временно уходят в альтернативный набор.'],None),
0x7F04:(['Чтение третьей правой координаты в будущий альтернативный BC.'],None),
0x7F0A:(['Восстановление основных Left0/Right0/Right1, альтернативные HL/DE/BC содержат Left1/Left2/Right2.'],None),
0x7F0B:(['Обновление двух кодов направления, хвостовой JP сохраняет внешний адрес возврата.'],None)}
STRUCT_BLOCK='\n                ; Три исходных signed32, формат доказан чтениями 7EB7 и вычитаниями 68CD\n'
STRUCT_BLOCK+='                struct FActionWideComponent\n'
for name,note in (('Byte0','разряды 7..0 исходной компоненты'),('Byte1','разряды 15..8 исходной компоненты'),
    ('Byte2','разряды 23..16, бит 7 используется 7F0E как знак выходного слова'),('Byte3','разряды 31..24, бит 7 задаёт знак полного signed32')):
    STRUCT_BLOCK+=name.ljust(16)+'db #00'.ljust(64)+'; '+note+'\n'
STRUCT_BLOCK+='                ends\n                assert FActionWideComponent == #04\n\n                struct FActionWideVector\n'
for i in range(3):STRUCT_BLOCK+=('Component'+str(i)).ljust(16)+'FActionWideComponent'.ljust(64)+'; исходная широкая компонента '+str(i)+'\n'
STRUCT_BLOCK+='                ends\n                assert FActionWideVector == #0C\n\n'


def name_operands(region,address,operation):
    if (region,address)!=('Action',0x7EB7):return operation
    for value,name in ((0x7F0F,'FirstHigh'),(0x7F12,'FirstLow'),(0x7F23,'SecondHigh'),(0x7F26,'SecondLow'),(0x7F37,'ThirdHigh'),(0x7F3A,'ThirdLow')):
        operation=operation.replace('#'+format(value,'04X'),'@ActionClampVectorWordsState.'+name)
    for offset in range(12):operation=operation.replace('(IY+#'+format(offset,'02X')+')','(IY + @FActionWideVector.Component'+str(offset//4)+'.Byte'+str(offset%4)+')')
    for offset in range(6):operation=operation.replace('(IX+#'+format(offset,'02X')+')','(IX + @FActionRecord.Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')+')')
    return operation


def qualify_mutations(records,regions,functions):
    for item in records:
        if item['region']=='Action' and 0x7EB7<=item['writer']<0x7F0E:
            assert item['target'] in (0x7F0F,0x7F12,0x7F23,0x7F26,0x7F37,0x7F3A)
            item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True,
                target_region='Action',target_bank=5,target_slot=17,target_offset=item['target']-0x6000+0x23D,
                target_source_classified=True,target_path='Source/Action/ClampPatchedVectorWords.asm')
