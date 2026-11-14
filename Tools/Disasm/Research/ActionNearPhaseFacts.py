"""Общий хвост F087, два пространства широких векторов и исходный изменяемый порог."""
FUNCTIONS={0xF087:('UpdateNearVectorPhase','Проверка близких широких векторов, случайного состояния 6 и шага фазы записи')}
LOCAL={0xF0AC:'CheckGlobal'}
STATE_MODULE='ActionNearPhaseState'
STATE_FIELDS=(('RandomHighMin',0xF09D,'изменяемый байт CP n, порог половины старшего байта потока 0'),)
MODIFIED_WRITERS=((0xF093,0xF09D,0xF09C,1),)
CONTRACTS={('Action',0xF087):(
    [
     'HL, DE, BC и AF числовых аргументов не задают, IX указывает доступные StateCode и OffsetPhase1 записи',
     'действуют договоры FindFirstNearWideVector, MaxFoldedVectorHigh и NextRandomWord0',
     'список широких векторов, его счётчик, глобальные High0..High2 и состояние потока 0 доступны',
     'ACTION банка 0 выбран, шесть дополнительных байтов CPU-стека доступны, IRQ и повторный вход исключены',
     'читается Component0.High, для активной записи доступны остальные фазовые поля, класс, состояние и порог',
     'OffsetScaleLow и OffsetScaleHigh активной записи доступны для записи, ACTION банка 0 и общая RAM доступны',
     'действует договор ApplyObjectOffsetVector, шесть байтов под SP и внешний возврат не перекрывают его код, таблицы, операнды и результаты',
     'IRQ и повторный вход исключены',
    ],
    [
     'FindFirstNearWideVector выбирает первый близкий вектор либо возвращает L=7F, его числовой результат L сравнивается с 4',
     'при L<4 RandomHighMin получает 28+4*L и вызывается поток 0, если H>>1 не меньше порога и L=7F, StateCode=06',
     'после StateCode=06 глобальная проверка и увеличение OffsetPhase1 пропускаются, AF=7F6A только на границе перед F0F8',
     'во всех остальных случаях MaxFoldedVectorHigh вычисляет максимум глобальных свёрнутых High0..High2, при максимуме меньше 4 OffsetPhase1 увеличен по модулю 256',
     'перед F0F8 при увеличении A равен новой фазе, F соответствует INC прежней фазы с Carry=1, иначе A равен глобальному максимуму и F от CP с 4',
     'перед F0F8 HL соответствует выбранному широкому вектору либо потоку, L после глобальной проверки равен глобальному максимуму',
     'перед F0F8 DE и B определяются FindFirstNearWideVector, C сохраняется, альтернативные HL, DE и BC меняются только при потоке 0',
     'при маркере Component0.High=80 общий хвост даёт AF=8042, остальные регистры сохраняют результаты префикса, собственные записи не откатываются, R добавляет четыре M1',
     'на активной ветви нижеследующие результаты вычислителя относятся к V из прежнего OffsetScaleLow и выбранного старшего байта',
     'HL=(-Q) AND FFFF при бите 7 S=1, иначе HL=Q, DE=Q при бите 7 S=1, иначе DE=abs(V)',
     'BC - B=W[Offset0], C=0',
     'AF - A=S, F от 16-разрядного 0-Q при бите 7 S=1, иначе флаги логического XOR с результатом S',
     "HL', DE', BC' сохраняют результаты потока 0 либо исходные значения без потока",
     "AF' - A'=U, F'=(U AND 28) OR (40 при U=0) OR (10 при 2*((P SHR 16) AND 0F)+(U AND 1)>0F), остальные биты F' нулевые",
     'IX восстановлен, IYH сохраняется, IYL=W[(Offset1+64) AND FF]',
     'Coefficient0..2 содержат результат построителя, Base0..2 содержат три произведения с одним входным V',
     'SP=входной SP+2, I, IM, IFF и paging сохраняются, порты не используются',
     'Offset0..2 получают OffsetPhase0, wrap8(OffsetPhase1+80) и OffsetPhase2',
     'OffsetScaleLow получает wrap8(старое+1), если этот кандидат ниже Phase2OrTarget, иначе сохраняется прежний байт',
     'OffsetScaleHigh обнулён при ClassCode<10 и StateCode не равном 13, иначе сохранён',
     'на активной ветви R учитывает 30+Hold+4*Small+2*Small*Different M1 подготовки плюс полный вычислитель, старший бит R сохраняется',
     'все эффекты активного хвоста вычислены после обновления StateCode и OffsetPhase1, полное R включает стоимость собственного префикса и общего хвоста',
     'IX, IYH, I/IM/IFF и paging сохраняются, активный IYL заменяется вычислителем, OUT отсутствует',
     'на всех путях SP=входной SP+2, рамка собственного входа до шести байтов повторно используется общим вычислителем',
    ],
    [
     "HL, DE, BC, AF, HL', DE', BC' при потоке 0, AF' на активном пути, IYL, R, RandomHighMin, StateCode, OffsetPhase1, условно масштабы, три фазовых операнда, Coefficient0..2, Base0..2 и до шести временных байтов CPU-стека",
    ],
    [
     'результат поиска и глобальные High0..High2 относятся к разным источникам, их близость не отождествляется',
     'операнд RandomHighMin исходно равен 28, каждый достигнутый случайный путь пересчитывает его, новое значение не выделяет RAM',
     'прежние 75008 сценариев останавливаются перед F0F8, новая композиция 150016 сценариев проверяет каждый прежний профиль с активной и маркерной текущей записью',
     'из новых случаев 143360 относятся к F087, по 3328 к родителям F07C и F081, их дополнительная рамка до десяти байтов не является глубиной самого F087',
     'сверены регистры кроме T, точный R, восемь банков, кратность присваиваний и отсутствие OUT, пределы и дополнительные фазы связаны с профилем',
     'полный кадр, полное произведение входов, IRQ, точные T, сборка и нативный запуск не проверялись',
     'эффективное слово V перед 6D06 содержит прежний OffsetScaleLow в E и итоговый OffsetScaleHigh в D, это не входное DE всей процедуры',
     'Hold=1 при сохранении прежнего младшего масштаба, иначе 0, Small=1 при ClassCode<10, Different=1 при StateCode не равном 13, иначе соответствующий признак нулевой',
     '10, 13 и 80 в условиях полей обозначают шестнадцатеричные коды, числа M1 десятичные',
    ])}

# Полные определения символов числовых постусловий общего вычислителя.
from ActionObjectOffsetTransferFacts import CONTRACTS as _FORMULA_OFFSET_CONTRACTS
CONTRACTS['Action', 0xf087][3].extend(_FORMULA_OFFSET_CONTRACTS['Action', 0xF0F8][3][3:9])

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
