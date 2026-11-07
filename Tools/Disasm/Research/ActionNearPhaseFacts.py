"""Общий хвост F087, два пространства широких векторов и исходный изменяемый порог."""
FUNCTIONS={0xF087:('UpdateNearVectorPhase','Проверка близких широких векторов, случайного состояния 6 и шага фазы записи')}
LOCAL={0xF0AC:'CheckGlobal'}
STATE_MODULE='ActionNearPhaseState'
STATE_FIELDS=(('RandomHighMin',0xF09D,'изменяемый байт CP n, порог половины старшего байта потока 0'),)
MODIFIED_WRITERS=((0xF093,0xF09D,0xF09C,1),)
CONTRACTS={('Action',0xF087):(
    ['HL, DE, BC и AF числовых аргументов не задают, IX указывает доступные StateCode и OffsetPhase1 записи',
     'действуют договоры FindFirstNearWideVector, MaxFoldedVectorHigh и NextRandomWord0',
     'список широких векторов, его счётчик, глобальные High0..High2 и состояние потока 0 доступны',
     'ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены'],
    ['FindFirstNearWideVector выбирает первый близкий вектор либо возвращает L=7F, его числовой результат L сравнивается с 4',
     'при L<4 RandomHighMin получает 28+4*L и вызывается поток 0, если H>>1 не меньше порога и L=7F, StateCode=06',
     'после StateCode=06 глобальная проверка и увеличение OffsetPhase1 пропускаются, AF=7F6A',
     'во всех остальных случаях MaxFoldedVectorHigh вычисляет максимум глобальных свёрнутых High0..High2, при максимуме меньше 4 OffsetPhase1 увеличен по модулю 256',
     'при увеличении A равен новой фазе, F соответствует INC прежней фазы с Carry=1, иначе A равен глобальному максимуму и F от CP с 4',
     'HL соответствует выбранному широкому вектору либо потоку, L после глобальной проверки равен глобальному максимуму',
     'DE и B определяются FindFirstNearWideVector, C сохраняется, альтернативные HL, DE и BC меняются только при потоке 0',
     "AF', IX, IY, I/IM/IFF и paging сохраняются, PC=F0F8 и SP сохраняется, внешний возврат не исполнен",
     'R точно проверен композицией поиска, потока и глобального максимума, формула накладных M1 приведена в документации'],
    ["HL, DE, B, AF, HL', DE', BC' при потоке 0, R, RandomHighMin, StateCode либо OffsetPhase1 по ветвям, до шести байтов CPU-стека"],
    ['результат поиска и глобальные High0..High2 относятся к разным источникам, их близость не отождествляется',
     'операнд RandomHighMin исходно равен 28, каждый достигнутый случайный путь пересчитывает его, новое значение не выделяет RAM',
     '71680 сценариев этого входа и 3328 двух родительских состояний проверены совместно, общий отчёт содержит 75008 сценариев',
     'реальные дети исполняются, сравниваются регистры, флаги, R, SP, восемь банков и все записи',
     'проверка останавливается перед F0F8, полный кадр, IRQ, точные T, сборка и нативный запуск не выполнялись'])}
COMMENTS={
    0xF087:(['Поиск первого близкого широкого вектора, его результат L не подменяется глобальным максимумом.'],None),
    0xF08A:(['Проверка результата поиска перед случайным переводом текущей записи в состояние 6.'],None),
    0xF08D:([],'переход, если результат L не меньше 4, пропустить поток 0 и проверить глобальные байты'),
    0xF08F:(['Расчёт порога 40+4*L для половины старшего байта нового слова потока 0.'],None),
    0xF093:(['Обновление исходного операнда CP n рассчитанным порогом без выделения новой памяти.'],None),
    0xF096:(['Получение одного нового слова потока 0 для обеих случайных проверок.'],None),
    0xF099:(['Расчёт беззнаковой половины старшего байта нового слова.'],None),
    0xF09C:(['Проверка половины старшего байта по только что рассчитанному RandomHighMin.'],None),
    0xF09E:([],'переход, если половина H меньше RandomHighMin, проверить глобальные байты'),
    0xF0A0:(['Проверка точного младшего байта 7F того же нового слова.'],None),
    0xF0A3:([],'переход, если младший байт нового слова отличается от 7F, проверить глобальные байты'),
    0xF0A5:(['Обновление состояния 6, эта ветвь пропускает увеличение фазового индекса.'],None),
    0xF0AC:(['Проверка отдельного глобального максимума, High0..High2 не являются результатом предыдущего поиска.'],None),
    0xF0B2:([],'переход, если глобальный максимум не меньше 4, сохранить фазу и продолжить общий хвост'),
    0xF0B4:(['Обновление циклического индекса OffsetPhase1 на единицу, FF переходит в 00.'],None),
}
INCLUDE_BLOCKS=(('Includes/Const/Include.inc','module ActionNearPhaseConst','''
                ; Исходные пороги широких векторов и выбора состояния 6
                module ActionNearPhaseConst
SmallLimit      equ #04                                                         ; исключающий верхний порог близости, результаты 0..3 допускаются
RandomBase      equ #28                                                         ; базовая часть изменяемого порога половины H
RandomLowCode   equ #7F                                                         ; точный младший байт нового слова для состояния 6
SelectedState   equ #06                                                         ; исходный индекс состояния, выбранного случайной ветвью
                endmodule
'''),)


def name_operands(region,function_address,operation):
    if (region,function_address)!=('Action',0xF087):return operation
    for address,name in ((0x69BE,'FindFirstNearWideVector'),(0xEB72,'NextRandomWord0'),(0x699C,'MaxFoldedVectorHigh')):
        operation=operation.replace('CALL #'+format(address,'04X'),'CALL @Action.'+name+'.Entry')
    return (operation.replace('#F0F8','@Action.PrepareObjectOffsetTransform.Entry')
            .replace('(#F09D)','(@ActionNearPhaseState.RandomHighMin)')
            .replace('(IX+#0A)','(IX + @FActionRecord.StateCode)')
            .replace('(IX+#08)','(IX + @FActionRecord.OffsetPhase1)')
            .replace('CP #04','CP @ActionNearPhaseConst.SmallLimit')
            .replace('ADD A, #28','ADD A, @ActionNearPhaseConst.RandomBase')
            .replace('CP #7F','CP @ActionNearPhaseConst.RandomLowCode')
            .replace(', #06',', @ActionNearPhaseConst.SelectedState'))


def qualify_mutations(records,flow,functions,pieces):
    for item in records:
        if item['region']=='Action' and item['writer']==0xF093:
            item.update(writer_slot=17,writer_offset=0x9093,writer_bank=0,
                target_slot=17,target_offset=0x909D,target_bank=0,target_region='Action',
                target_path='Source/Action/UpdateNearVectorPhase.asm',target_source_classified=True,writer_source_classified=True)
