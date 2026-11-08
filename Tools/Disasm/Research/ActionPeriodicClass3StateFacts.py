"""State0B, общий период из 16 вызовов и ограничитель числа созданных записей в родителе."""
FUNCTIONS={0xF3F0:('SpawnPeriodicClass3Record','Периодическое создание одной записи класса 3 с уменьшением родительского счётчика и обязательным сбросом баз')}
LOCAL={0xF414:'CreateChild',0xF499:'ResetBases'}
STATE_MODULE='ActionPeriodicClass3State'
STATE_FIELDS=(('SpawnPhase',0xF3F1,'существующий операнд LD A,n, общая четырёхбитная фаза допуска создания'),)
MODIFIED_WRITERS=((0xF3F5,0xF3F1,0xF3F0,1),)
CONTRACTS={('Action',0xF3F0):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает активную FActionRecord родителя',
     'Unknown0D задаёт обычный байтовый индекс связанной записи, SavedStateCode используется здесь как счётчик оставшихся созданий',
     'SpawnPhase доступен для изменения, от A100 достижим маркер либо свободная запись, слово координат по 9BC1 читается классификатором',
     'действуют договоры FindReusableRecord, RecordIndexToAddress, ClassifyCoordinateRegion и ResetRecordUpdateBases',
     'ACTION банка 0 выбран, два дополнительных байта CPU-стека доступны, IRQ и повторный вход исключены'],
    ['SpawnPhase получает wrap8(SpawnPhase+1) AND 0F, только нулевой результат допускает попытку создания',
     'при ненулевой фазе либо отсутствии свободной записи новая запись не создаётся, Base0..2 всё равно обнуляются',
     'при найденной свободной записи проверяется Component0.High записи по индексу Unknown0D, значение 80 переводит родителя в StateCode=09 без заполнения ребёнка',
     'иначе ребёнок получает компоненты 0 и 2 родителя, компоненту 1 плюс BC, B=1 либо 2 по R и C=80',
     'ClassCode ребёнка=3, ModelOffset=10+4*код ClassifyCoordinateRegion слова по 9BC1, остальные записываемые поля перечислены в документации',
     'после заполнения SavedStateCode родителя уменьшен на один по модулю 256, только переход 1 в 0 устанавливает родительский StateCode=09',
     'на всех путях HL=0, Base0..2=0, прочие выходы зависят от последнего исполненного ребёнка',
     'при создании DE=0040, BC содержит смещение второй компоненты, A равен декрементированному родительскому счётчику и F от DEC с Carry=0',
     "HL', DE', BC', AF', IX, I/IM/IFF и paging сохраняются, IY равен найденной записи либо маркеру после поиска и исходному IY без поиска",
     'SP после внешнего RET увеличен на два, дополнительная рамка равна двум байтам, точная стоимость R приведена по ветвям в документации'],
    ['HL, DE, BC, AF, IY, R, SpawnPhase, ReuseByte просмотренных свободных записей, условные поля родителя и ребёнка, Base0..2 и два временных байта CPU-стека, SP внешним RET'],
    ['SpawnPhase общий для всех вызывающих записей, период измеряется вызовами этой процедуры, не гарантированным числом кадров',
     'SavedStateCode в этом состоянии является счётчиком, его прежнее нулевое значение оборачивается в FF, универсальное значение поля не выдумывается',
     '135168 сценариев охватили все фазы и родительские счётчики, все слова координат классификатора и граничные индексы со всеми R',
     'реальные поиск, индекс, классификатор и сброс исполняются, сверены регистры, флаги, R, восемь банков и все записи до полного RET',
     'полное произведение входов, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись'])}
COMMENTS={
    0xF3F0:(['Обновление общей фазы допуска, после INC остаются только четыре младших бита.'],None),
    0xF3F8:([],'переход, если новая SpawnPhase ненулевая, пропустить создание и обнулить общие базы'),
    0xF3FB:(['Поиск свободной записи, его очистка ReuseByte сохраняется даже при последующем отказе связанной записи.'],None),
    0xF3FE:([],'переход, если поиск достиг маркера, обнулить базы без создания ребёнка'),
    0xF401:(['Преобразование обычного индекса из Unknown0D, отдельной обработки FF здесь нет.'],None),
    0xF407:(['Проверка старшего байта Component0 связанной записи перед заполнением найденного свободного слота.'],None),
    0xF40B:([],'переход, если связанная запись имеет Component0.High не равный 80, заполнить ребёнка'),
    0xF40D:(['Обновление родителя до состояния 09 при недоступной связи, найденный свободный слот не заполняется.'],None),
    0xF414:(['Копирование первой компоненты родителя в ребёнка без числового изменения.'],None),
    0xF420:(['Расчёт положительного смещения второй компоненты, B равен младшему биту прочитанного R плюс один, C=80.'],None),
    0xF428:(['Создание второй компоненты ребёнка прибавлением общего BC по модулю 65536.'],None),
    0xF435:(['Копирование третьей компоненты родителя без смещения.'],None),
    0xF441:(['Классификация исходного слова координат по 9BC1 для выбора одного из четырёх байтовых смещений модели.'],None),
    0xF447:(['Расчёт ModelOffset=10+4*код области, повороты безопасны для доказанного диапазона кода 0..3.'],None),
    0xF44E:(['Заполнение исходных управляющих полей ребёнка класса 3, не записываемые поля свободного слота сохраняются.'],None),
    0xF476:(['Копирование индекса связи Unknown0D родителя в LinkedIndex ребёнка и завершение его управляющих полей.'],None),
    0xF48C:(['Обновление счётчика числа созданий, физическое поле SavedStateCode имеет в этом состоянии числовую роль.'],None),
    0xF493:([],'переход, если декрементированный счётчик ненулевой, сохранить текущее состояние родителя'),
    0xF495:(['Обновление родителя до состояния 09 после последнего разрешённого создания.'],None),
    0xF499:(['Обязательное обнуление общих Base0..2 через исходный хвост с внешним RET.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionPeriodicClass3Const','''
                ; Исходные параметры периодического создания класса 3
                module ActionPeriodicClass3Const
PhaseMask       equ #0F                                                         ; общая фаза по модулю 16 вызовов
ParentState     equ #09                                                         ; состояние родителя при недоступной связи либо окончании счётчика
ModelBase       equ #10                                                         ; байтовая база четырёх моделей, код области умножается на четыре
TargetLife      equ #96                                                         ; исходный управляющий байт 0F ребёнка, 150
InitialPhase0   equ #40                                                         ; начальный циклический индекс первой фазы
TimerByte11     equ #46                                                         ; управляющий счётчик байта 11, 70
InitialState    equ #02                                                         ; начальное состояние ребёнка
SavedState      equ #0C                                                         ; сохранённое состояние ребёнка
ChildClass      equ #03                                                         ; полный класс создаваемой записи
ControlByte13   equ #64                                                         ; исходный байт 13, 100
InitialByte10   equ #1E                                                         ; исходный байт 10, 30
                endmodule
'''),('Includes/Variables/Include.inc','module ActionPeriodicRegionState','''
                ; Исходное слово для выбора модели, память не выделяется
                module ActionPeriodicRegionState
Coordinate      equ #9BC1                                                       ; слово H,L для ClassifyCoordinateRegion в этом контексте
                endmodule
'''))


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF3F0):return operation
    for register,fields in (('IX',{13:'Unknown0D',22:'SavedStateCode',10:'StateCode'}),('IY',{6:'ModelOffset',15:'TargetIndex',7:'OffsetPhase0',8:'OffsetPhase1',9:'OffsetPhase2',17:'Unknown11',10:'StateCode',22:'SavedStateCode',12:'LinkFlags',18:'ClassCode',20:'Unknown14',21:'LinkOverride',11:'LinkedIndex',19:'Unknown13',16:'Unknown10',37:'TargetCodeStep'})):
        for offset,name in fields.items():operation=operation.replace('('+register+'+#'+format(offset,'02X')+')','('+register+' + @FActionRecord.'+name+')')
    for offset in range(6):
        name='Components.Component'+str(offset//2)+('.High' if offset&1 else '.Low')
        for register in ('IX','IY'):operation=operation.replace('('+register+'+#'+format(offset,'02X')+')','('+register+' + @FActionRecord.'+name+')')
    for address,name in ((0xE9A1,'FindReusableRecord'),(0xE6A7,'RecordIndexToAddress'),(0x6E2B,'ClassifyCoordinateRegion')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    operation=(operation.replace('(#F3F1)','(@ActionPeriodicClass3State.SpawnPhase)')
        .replace('(#9BC1)','(@ActionPeriodicRegionState.Coordinate)').replace('#F572','@Action.ResetRecordUpdateBases.Entry')
        .replace('AND #0F','AND @ActionPeriodicClass3Const.PhaseMask').replace('CP #80','CP @ActionReuseConst.ReusableHigh')
        .replace('ADD A, #10','ADD A, @ActionPeriodicClass3Const.ModelBase'))
    for register,field,literal,name in (('IX','StateCode','09','ParentState'),('IY','TargetIndex','96','TargetLife'),
        ('IY','OffsetPhase0','40','InitialPhase0'),('IY','Unknown11','46','TimerByte11'),('IY','StateCode','02','InitialState'),
        ('IY','SavedStateCode','0C','SavedState'),('IY','ClassCode','03','ChildClass'),('IY','Unknown13','64','ControlByte13'),('IY','Unknown10','1E','InitialByte10')):
        operation=operation.replace('LD ('+register+' + @FActionRecord.'+field+'), #'+literal,'LD ('+register+' + @FActionRecord.'+field+'), @ActionPeriodicClass3Const.'+name)
    return operation.replace('LD (IY + @FActionRecord.TargetCodeStep), #02','LD (IY + @FActionRecord.TargetCodeStep), @ActionChildSpawnConst.TargetStep')


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0xF3F5:
            item.update(writer_slot=17,writer_offset=0x93F5,writer_bank=0,target_slot=17,target_offset=0x93F1,
                target_bank=0,target_region='Action',target_path='Source/Action/SpawnPeriodicClass3Record.asm',
                target_source_classified=True,writer_source_classified=True)
