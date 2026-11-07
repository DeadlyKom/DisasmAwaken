"""Исходный повтор нулевого хвоста State00, новые области не выделяются."""
from ActionRecordBaseResetFacts import CONTRACTS as ORIGINAL_CONTRACTS,name_operands as original_names
FUNCTIONS={0xF691:('ResetIdleRecordBases','Обнуление трёх общих базовых слов при нулевом управляющем байте State00')}
LOCAL={}
CONTRACTS={('Action',0xF691):tuple([line.replace('F573','F692').replace('65536 сценариев','65536 сценариев отдельного входа') for line in section]
    for section in ORIGINAL_CONTRACTS['Action',0xF572])}
COMMENTS={0xF691:(['Подготовка нулевого базового слова из исходного непосредственного операнда.'],None),
          0xF694:(['Обнуление Base0 в общей процедуре обновления компонент.'],None),
          0xF697:(['Обнуление Base1 без изменения Active1 и Original1.'],None),
          0xF69A:(['Обнуление Base2 без изменения активных смещений и признака предупреждения.'],None)}
MODIFIED_WRITERS=((0xF694,0xE5B0,0xE5AF,2),(0xF697,0xE5CF,0xE5CE,2),(0xF69A,0xE5EA,0xE5E9,2))


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF691):return operation
    return original_names('Action',0xF572,operation)


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer'] in (0xF694,0xF697,0xF69A):
            item.update(writer_slot=17,writer_offset=item['writer']-0x6000,writer_bank=0,
                target_slot=17,target_offset=item['target']-0x6000,target_bank=0,target_region='Action',
                target_path='Source/Action/UpdateRecordComponents.asm',target_source_classified=True,writer_source_classified=True)
