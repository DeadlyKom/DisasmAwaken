"""State0A, общая вращаемая фаза, три эффекта класса 17 и переход к созданию класса 3."""
FUNCTIONS={0xF49C:('SweepClass17AndPrepareSpawn','Обработка до трёх записей класса 17 и подготовка периодического создания при недостатке связей класса 3')}
LOCAL={0xF4B2:'CheckMarker',0xF4B9:'NextRecord',0xF4FF:'CheckClass3'}
STATE_MODULE='ActionClass17SweepState'
STATE_FIELDS=(('SweepPhase',0xF49D,'существующий операнд LD A,n, общая вращаемая фаза допуска обхода'),)
MODIFIED_WRITERS=((0xF49F,0xF49D,0xF49C,1),)
CONTRACTS={('Action',0xF49C):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступную текущую FActionRecord',
     'от A100 достижим маркер 8080, активные строки доступны по ClassCode, Unknown0D и TargetIndex',
     'вложенный индекс TargetIndex кандидата адресует читаемый ClassCode, действуют договоры RecordIndexToAddress и CountClass3LinksUpToTwo',
     'для кандидатов класса 11 с целью класса 12 действуют договоры PrepareLargeEffect и AllocateLargeEffect, проверяемая ветвь класса 17 не создаёт игровых дочерних записей',
     'OBJECT3D и VOXAL доступны в банках 4 и 3, 7FFD разблокирован, восемнадцать дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены'],
    ['SweepPhase вращается RRCA и сохраняется, только прежний бит 0 допускает обход, при его нуле сразу обнуляются Base0..2 и возвращается исходный контекст кроме HL, AF и R',
     'при обходе для каждой активной строки Unknown0D владельца IX получает Unknown0D этой строки до проверки её класса',
     'только полные ClassCode=11 и полный класс связанной по TargetIndex записи=12 допускают большой эффект, максимум три вызова эффекта за проход',
     'кандидат становится временным IX, исходные IX, указатель сканирования, шаг и счётчик восстанавливаются после настоящего большого эффекта',
     'после обхода CountClass3LinksUpToTwo считает класс 3 с StateCode=2 и LinkedIndex=текущему Unknown0D владельца',
     'при двух совпадениях состояние владельца сохраняется, при нуле либо одном StateCode=0B, SavedStateCode получает 2 либо 3 по младшему биту прочитанного R',
     'только при текущем Unknown0D=1A вызывается AdjustMode с непосредственным C=20, это вход готовой поправки, таблица индексов не читается',
     'все пути обнуляют Base0..2 через ResetRecordUpdateBases, HL=0, SP после полного внешнего RET увеличен на два',
     'после исполненного обхода DE=0040, BC и AF определяются насыщенным счётчиком, проверкой связи либо AdjustMode, IY последним большим эффектом либо исходным IY',
     'IX и I/IM/IFF сохраняются, при эффектах альтернативные пары и AF\' определяются реальным большим эффектом и восстановлением счётчика, paging возвращён в 10',
     'R точно сверяется композиционной моделью всех достигнутых ветвей, накладные стоимости и границы приведены в документации'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IY, R, SweepPhase, Unknown0D и условно StateCode/SavedStateCode владельца, выбранные записи и эффекты, Base0..2, режимная поправка, операнды и банки по договорам детей, до восемнадцати байтов CPU-стека, SP внешним RET"],
    ['это исходная цель State0A, коды 11 и 12 шестнадцатеричные, соответственно 17 и 18 десятично',
     'SweepPhase общий для всех объектов, исходный 92 задаёт три допуска на восемь вызовов, это не восемь независимых флагов и не обязательные кадры',
     'текущая запись может сама пройти фильтр, её освобождение не отменяет последующие присваивания через восстановленный IX',
     '38144 сценария покрыли все фазы, стили списков и все исходные байты поправки и режима, реальные большие эффекты исполняются до внешнего RET',
     'сверены точные регистры, флаги, R, восемь банков, кратность записей и настоящие порты, полный игровой кадр не заявляется',
     'полное произведение входов, аппаратные IRQ, точные T, сборка и нативный запуск не выполнялись'])}
COMMENTS={
    0xF49C:(['Обновление общей циклической фазы RRCA, допуск определяется прежним битом 0.'],None),
    0xF4A2:([],'переход, если прежний бит 0 SweepPhase сброшен, пропустить обход и обнулить базы'),
    0xF4A5:(['Подготовка альтернативного E=3, это предел числа эффектов данного прохода, старший D сохраняется.'],None),
    0xF4A9:(['Подготовка указателя перед первой записью и исходного шага 64 к её старшему байту компоненты.'],None),
    0xF4B2:(['Проверка младшего байта маркера только у строки со старшим байтом 80.'],None),
    0xF4B6:([],'переход, если оба байта первой компоненты равны 80, завершить просмотр и проверить связи класса 3'),
    0xF4B9:(['Поиск следующей активной строки, значение 80 старшего байта требует отдельной проверки маркера.'],None),
    0xF4BD:([],'переход, если старший байт первой компоненты равен 80, проверить младший байт маркера'),
    0xF4BF:(['Чтение класса и двух контекстных байтов активной записи через её выровненный младший адрес.'],None),
    0xF4CA:(['Обновление Unknown0D владельца до фильтра класса, это присваивание происходит для каждой активной строки.'],None),
    0xF4D3:(['Проверка полного класса кандидата 11, это десятичный 17, маскирования бита 7 нет.'],None),
    0xF4D6:([],'переход, если полный ClassCode кандидата отличается от 11, проверить следующую строку'),
    0xF4D8:(['Проверка полного класса цели по TargetIndex кандидата, курсор сканирования сохраняется в альтернативных парах.'],None),
    0xF4E5:([],'переход, если полный ClassCode связанной цели отличается от 12, проверить следующую строку'),
    0xF4E7:(['Сохранение счётчика, указателя, шага и исходного IX перед временным выбором кандидата как текущей записи эффекта.'],None),
    0xF4F2:(['Создание настоящего большого эффекта кандидата класса 17, эта ветвь не создаёт игровые дочерние записи.'],None),
    0xF4F5:(['Восстановление владельца, шага, курсора и альтернативного счётчика после полного банкового возврата.'],None),
    0xF4FB:(['Обновление оставшегося числа эффектов только после завершённого вызова.'],None),
    0xF4FD:([],'переход, если осталось разрешённое число эффектов, продолжить просмотр записей'),
    0xF4FF:(['Подсчёт до двух активных связей класса 3, состояние 2 и ссылка сравниваются целиком.'],None),
    0xF502:([],'переход, если найдено два совпадения и Carry сброшен, сохранить состояние владельца и обнулить базы'),
    0xF504:(['Обновление владельца до State0B и подготовка числа последующих созданий 2 либо 3 по реальному R.'],None),
    0xF511:(['Проверка специальной текущей связи перед непосредственной поправкой C=32 без табличного индекса.'],None),
    0xF518:([],'вызов, если текущий Unknown0D равен 1A, применить готовую поправку C=32 через AdjustMode'),
    0xF51B:(['Обязательное обнуление общих Base0..2 и полный внешний возврат.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionClass17SweepConst','''
                ; Полные фильтры и исходные параметры State0A
                module ActionClass17SweepConst
EffectLimit     equ #03                                                         ; максимум вызовов большого эффекта за один допущенный проход
CandidateClass  equ #11                                                         ; полный класс кандидата, 17 десятично
TargetClass     equ #12                                                         ; полный класс связанной цели, 18 десятично
SpawnState      equ #0B                                                         ; состояние периодического создания класса 3
SpawnBaseCount  equ #02                                                         ; младший бит R прибавляется к этому исходному числу созданий
SpecialLink     equ #1A                                                         ; связь, допускающая непосредственную поправку C
DirectDelta     equ #20                                                         ; положительная исходная поправка, 32, при режиме увеличивается на 10
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF49C):return operation
    operation=(operation.replace('(#F49D)','(@ActionClass17SweepState.SweepPhase)')
        .replace('LD E, #03','LD E, @ActionClass17SweepConst.EffectLimit')
        .replace('LD DE, #0040','LD DE, @FActionRecord')
        .replace('LD A, #0B','LD A, @ActionClass17SweepConst.SpawnState')
        .replace('LD (IX+#0A), #0B','LD (IX+#0A), @ActionClass17SweepConst.SpawnState')
        .replace('ADD A, #02','ADD A, @ActionClass17SweepConst.SpawnBaseCount')
        .replace('CP #1A','CP @ActionClass17SweepConst.SpecialLink')
        .replace('LD C, #20','LD C, @ActionClass17SweepConst.DirectDelta')
        .replace('CP #11','CP @ActionClass17SweepConst.CandidateClass')
        .replace('CP #12','CP @ActionClass17SweepConst.TargetClass')
        .replace('CP #80','CP @ActionReuseConst.ReusableHigh'))
    for literal,name in (('0D','Unknown0D'),('0A','StateCode'),('16','SavedStateCode')):
        operation=operation.replace('(IX+#'+literal+')','(IX + @FActionRecord.'+name+')')
    for address,name in ((0xE6A7,'RecordIndexToAddress.Entry'),(0xEA29,'PrepareLargeEffect.Entry'),(0x62CF,'CountClass3LinksUpToTwo.Entry')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name)
    return operation.replace('CALL Z, #638C','CALL Z, @Action.ApplyIndexedDelta.AdjustMode').replace('#F572','@Action.ResetRecordUpdateBases.Entry')


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0xF49F:
            item.update(writer_slot=17,writer_offset=0x949F,writer_bank=0,target_slot=17,target_offset=0x949D,
                target_bank=0,target_region='Action',target_path='Source/Action/SweepClass17AndPrepareSpawn.asm',
                target_source_classified=True,writer_source_classified=True)
