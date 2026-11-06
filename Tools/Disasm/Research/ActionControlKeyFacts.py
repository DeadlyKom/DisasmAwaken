"""Общие доказанные договоры шести клавиатурных обработчиков, без изменения размещения."""
from ActionControlKeyLayout import ENTRIES

CONST_BLOCK='\n                ; Исходные шаги накопителей клавиатурного повтора и границы signed8\n                module ActionControlKeyConst\n'
for name,value,note in (('One',1,'единичный запрос либо шаг знакового значения'),('OppositeReset',200,'сброс накопителя противоположного направления'),
    ('TurnAdd',94,'приращение накопителя поворота'),('XAdd',70,'приращение накопителя X'),('YAdd',72,'приращение накопителя Y'),
    ('TurnPositive',8,'исключённая верхняя граница положительного поворота'),('TurnNegative',249,'включённая нижняя граница отрицательного поворота'),
    ('XYPositive',4,'исключённая верхняя граница положительного X либо Y'),('XYNegative',253,'включённая нижняя граница отрицательного X либо Y'),
    ('NegativeFirst',255,'исходная подстановка минус единицы после неотрицательного кандидата')):
    CONST_BLOCK+=name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note+'\n'
CONST_BLOCK+='                endmodule\n\n'


def create(start):
    layout=next(row for row in ENTRIES if row[0]==start)
    _,name,tag,channel,direction,step,limit,own,opposite,latch,value=layout
    word='уменьшения' if direction<0 else 'увеличения'
    local={start+0x1C:'CheckLimit'}
    contracts={('Action',start):(
        ['HL, DE, BC, AF входных аргументов не задают',
         'исходный изменяемый операнд накопителя и '+channel+'Control доступны, код исполняется в фиксированном банке 5',
         'CPU-стек содержит внешний возврат, IRQ не вмешиваются, прежние операнды не изменяются параллельно'],
        ['HL, DE, BC сохраняются, '+channel+'Prev=1, текущий накопитель увеличен на '+str(step)+' по модулю 256',
         'накопитель противоположного направления равен C8 независимо от переноса текущего',
         'без переполнения накопителя управление не записывается, A=C8 и F соответствует ADD накопителя и шага',
         'при переполнении проверяется исходный знаковый кандидат '+word+' на единицу, точные граничные подстановки описаны в документации',
         'после проверки A содержит кандидата, F соответствует CP с границей '+format(limit,'02X')+', запись зависит от Carry',
         "HL', DE', BC', AF', IX, IY сохраняются, SP=входной SP+2, I, IM, IFF и 7FFD сохраняются",
         'R увеличен на 8 M1 без переноса, 13 M1 при отказе по границе, 15 либо 16 M1 при записи'],
        ['AF, R, три исходных изменяемых операнда и при разрешённом шаге соответствующий байт управления'],
        ['полный домен пары накопитель и управление проверен во всех 65536 сочетаниях этого входа',
         'начальные неподходящие signed8 не нормализуются общим насыщением, исходные переполнения и подстановки сохранены',
         'сопоставлены регистры включая R, все записи и восемь банков RAM, записей CPU-стека и порта нет',
         'повтор клавиши зависит от числа вызовов и накопленного остатка, период в игровых кадрах здесь не устанавливается',
         'совместное пространство остальных входных регистров, IRQ, точные T, сборка и нативный запуск не проверялись'])}
    comments={
        start:(['Создание запрета затухания '+channel+' на текущий проход, даже без готовности накопителя.'],None),
        start+5:(['Расчёт накопленного повтора клавиши с сохранением остатка по модулю 256.'],None),
        start+12:(['Обновление накопителя противоположного направления, флаги текущего ADD сохраняются.'],None),
        start+17:([], 'выход, если накопитель не переполнился, управление пока не изменяется'),
        start+18:(['Расчёт кандидата '+word+' signed8 на единицу.'],None),
        start+23:([], 'переход, если кандидат '+('отрицательный' if direction<0 else 'неотрицательный')+', проверить его границу без подстановки'),
        start+26:(['Создание исходного первого значения направления после смены знака либо его переполнения.'],None),
        start+28:(['Проверка кандидата на исходную границу направления, прежнее значение при отказе сохраняется.'],None),
        start+30:([], 'выход, если кандидат '+('меньше разрешённой отрицательной границы' if direction<0 else 'не меньше исключённой положительной границы')+', сохранить управление'),
        start+31:(['Обновление управления разрешённым кандидатом без изменения флагов CP.'],None)}
    state_names={address:field for field,address,_ in __import__('ActionControlDecayFacts').FIELDS}
    def name_operands(region,address,operation):
        if (region,address)!=('Action',start):return operation
        for target in (own,opposite,latch):operation=operation.replace('#'+format(target,'04X'),'@ActionControlDecayState.'+state_names[target])
        operation=operation.replace('#'+format(value,'04X'),'@ControlsPointMotionState.'+channel+'Control')
        operation=operation.replace('#01','@ActionControlKeyConst.One').replace('#C8','@ActionControlKeyConst.OppositeReset')
        operation=operation.replace('#'+format(step,'02X'),'@ActionControlKeyConst.'+channel+'Add')
        operation=operation.replace('#'+format(limit,'02X'),'@ActionControlKeyConst.'+('Turn' if channel=='Turn' else 'XY')+('Negative' if direction<0 else 'Positive'))
        return operation.replace('#FF','@ActionControlKeyConst.NegativeFirst')
    def qualify_mutations(records,regions,functions,pieces):
        for item in records:
            if item['region']!='Action':continue
            if start<=item['writer']<start+35:
                item.update(writer_bank=5,writer_offset=item['writer']-0x6000+0x23D,writer_source_classified=True,
                    target_region='Action',target_bank=5,target_slot=17,target_offset=item['target']-0x6000+0x23D)
            if any(entry[0]<=item['target']<entry[0]+35 for entry in ENTRIES):
                owner=next((f for f in functions if f['region']=='Action' and f['address']<=item['target']<f['address']+f['end_offset']-f['offset']),None)
                if owner:
                    item.update(target_source_classified=True,target_path=owner['path'],target_bank=5,target_region='Action')
            if item['target']==latch and start<=item['writer']<start+35:
                item.update(target_source_classified=True,target_path='Source/Action/LatchControlsAndDecay.asm')
    return dict(FUNCTIONS={start:(name,'Запрос '+word+' управления '+channel+' с накопителем повтора и исходной знаковой границей')},
        LOCAL=local,CONTRACTS=contracts,COMMENTS=comments,name_operands=name_operands,qualify_mutations=qualify_mutations,
        MODIFIED_WRITERS=((start+2,latch,latch-1,1),(start+9,own,own-1,1),(start+14,opposite,opposite-1,1)),
        INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionControlKeyConst',CONST_BLOCK),) if start==ENTRIES[0][0] else (),
        UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/Unclassified018_BeforeControlKeys.bin',
        UNCLASSIFIED_SUFFIX_PATH='Source/Resources/17_ACTION/Unclassified018_After'+name+'.bin')
