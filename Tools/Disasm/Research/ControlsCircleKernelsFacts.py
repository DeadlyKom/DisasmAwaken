"""Общие фазы трёх круговых ядер, контракты ограничены исходным протоколом инициализаторов."""
FUNCTIONS={0xD633:('CircleRasterCore','Двухфазное сужение кругового сечения с двумя криволинейными краями'),
    0xD727:('ResumeCirclePushSpan','Восстановление CPU-стека после обычной PUSH-заливки и продолжение горизонтальной фазы'),
    0xD73B:('LeftClippedCircleCore','Двухфазное сужение с неподвижным левым краем до совпадения порога Aprime'),
    0xD833:('RightClippedCircleCore','Двухфазное сужение с неподвижным правым краем до совпадения порога Aprime')}
LOCAL={
    0xD644:'CheckDown',0xD649:'EmptyReturn',0xD64B:'SaveStack',0xD64F:'SlowRow',0xD673:'FillPairs',
    0xD67E:'SlowDown',0xD681:'SlowY',0xD68F:'SlowRight',0xD693:'SlowX',0xD696:'FinishSlowX',0xD69A:'ChoosePhase',
    0xD69F:'SlowLeftByte',0xD6A8:'SlowRightByte',0xD6B1:'Finish',0xD6B7:'FastLeftByte',0xD6C0:'FastRightByte',
    0xD6C9:'FastX',0xD6CE:'FastRight',0xD6D2:'FastDifference',0xD6D7:'FinishFastX',0xD706:'PushSpan',
    0xD736:'NextDown',
    0xD74F:'CheckDown',0xD754:'EmptyReturn',0xD756:'SaveStack',0xD75A:'SlowRow',0xD773:'FillPairs',
    0xD77D:'SlowDown',0xD780:'SlowY',0xD78D:'SlowX',0xD799:'ChoosePhase',0xD79E:'SlowRightByte',
    0xD7A8:'ReleaseSlow',0xD7B2:'ReleaseFast',0xD7BC:'Finish',0xD7C2:'FastRightByte',0xD7CC:'FastX',
    0xD7D0:'FastDifference',0xD7FE:'PushSpan',0xD80D:'PushJump',0xD81F:'ResumeRows',0xD82E:'ResumeDown',
    0xD847:'CheckDown',0xD84C:'EmptyReturn',0xD84E:'SaveStack',0xD852:'SlowRow',0xD86D:'FillPairs',
    0xD872:'NextRow',0xD879:'SlowDown',0xD87C:'SlowY',0xD88A:'SlowX',0xD896:'ChoosePhase',
    0xD89B:'SlowLeftByte',0xD8A4:'ReleaseSlow',0xD8A8:'ReleaseFast',0xD8AC:'Finish',0xD8B2:'FastLeftByte',
    0xD8BB:'FastX',0xD8C0:'FastDifference',0xD8F0:'PushSpan',0xD8FF:'PushJump',0xD911:'ResumeRows',0xD920:'ResumeDown'}
LABELS={};RENAMES={};CONTINUATIONS={0xD633:0xD727}
for start,(name,_) in FUNCTIONS.items():
    RENAMES['Controls.Unknown'+format(start,'04X')+'.Entry']='Controls.'+name+'.Entry'
    end={0xD633:0xD727,0xD727:0xD73B,0xD73B:0xD833,0xD833:0xD925}[start]
    for address,label in LOCAL.items():
        if not start<address<end:continue
        old=('ResumeRows' if address in (0xD81F,0xD911) else 'ResumeDown' if address in (0xD82E,0xD920) else 'Point'+format(address,'04X'))
        RENAMES['Controls.Unknown'+format(start,'04X')+'.'+old]='Controls.'+name+'.'+label
    for first in (0xD717,0xD80F,0xD901):
        if start<=first<end:
            for count in range(1,17):
                label='Push'+str(count);address=first+16-count
                LOCAL[address]=label
                RENAMES['Controls.Unknown'+format(start,'04X')+'.'+label]='Controls.'+name+'.'+label

CONTRACTS={}
for start in (0xD633,0xD73B,0xD833):
    clipped=start!=0xD633
    CONTRACTS['Controls',start]=(
        ['HL задаёт правую границу строки растра 8000..8BFF, DE задаёт младший адрес левой границы E, D произвольный',
         ('BC содержит маски открытого интервала, обе границы канонического сечения находятся в 0..255' if not clipped else
          'BC и неподвижная граница соответствуют договору DrawLeftClippedHalf либо DrawRightClippedHalf, CurveX=8..247'),
         "HL'=0, D'=0, B'=FF, C'=(-X) AND FF, E'=Y0, допустимые начальные X/Y0 заданы в документации внешних входов",
         ("AF' сохраняется при обычном входе, при продолжении отсечённого ядра F' уже может содержать результат CP" if not clipped else
          "A' задаёт порог снятия отсечения, F' может быть произвольным"),
         'IX задаёт IXL как рисунок и IXH как чередование, IY сохраняется',
         'на CPU-стеке SavedAF и внешний возврат, Direction по D18B равен 0 для движения вверх либо 1 для движения вниз',
         'банк 1 выбран, растр и стек не пересекают код, IRQ не вмешиваются, отдельные внутренние входы требуют состояния соответствующей фазы'],
        ['HL, DE, BC содержат конечные края и маски либо арифметическое состояние при исходном выходе с активным EXX',
         'AF восстановлен из SavedAF, альтернативные HL, DE, BC содержат состояние ошибки, Y и X либо переставленные края',
         ("AF' сохраняется" if not clipped else "A' сохраняется, F' содержит результат последнего сравнения с Cprime либо входное значение, если сравнения не было"),
         'IXH и IY сохраняются, IXL переключается после каждой нарисованной строки, SP после внешнего RET равен входному SP+4',
         'I, IM, IFF и страница сохраняются, порты не записываются'],
        ["HL, DE, BC, AF, HL', DE', BC', "+("F', " if clipped else '')+'IXL, R, растр, SavedSP, условно изменяемые операнды и четыре временных байта CPU-стека'],
        ['это внутреннее ядро после PUSH AF и подготовки альтернативных пар, настоящий CALL к Entry без такой рамки не соответствует договору',
         'FinishSlowX и FinishFastX обычного ядра принимают активный EXX, первое прибавление по X и INC C уже выполнены',
         'сохранённый AF восстанавливается даже при выходе с активным EXX, переставленные HL/DE/BC принудительно не исправляются',
         'при пустом обычном сечении SavedSP не меняется, при начале рисования он равен входному SP, Direction читается, но не записывается',
         'быстрый PUSH-хвост временно заменяет SP правой границей, новая RAM не выделяется, рамка FSingleCircleHalfFrame учитывает внешний инициализатор',
         'модели подтверждают достижимые состояния из описанных внешних входов и цепочки PUSH, произвольные входные ошибки и отдельные внутренние адреса не объявляются исчерпывающе проверенными',
         'полное произведение геометрии и рисунков, R целого ядра, кратность пиксельных записей, IRQ, сборка и нативный запуск не доказаны'])
CONTRACTS['Controls',0xD727]=(
    ['HL задаёт правую границу после PUSH-заливки, DE задаёт правый младший адрес D и левый E, BC содержит маски',
     'AF содержит два байта рисунка, альтернативные пары содержат состояние горизонтальной фазы',
     'IX задаёт рисунок и чередование, SavedSP указывает SavedAF и внешний возврат, Direction определяет шаг строки',
     'SP пока направлен в растр, банк 1 выбран, IRQ не вмешиваются'],
    ['HL и E перенесены на следующую строку либо за её вертикальный край, D и BC сохраняются до продолжения ядра',
     'на обычном продолжении AF и IXL соответствуют AdvanceRasterUp либо AdvanceRasterDown, SP=SavedSP',
     'при достижении края AF восстановлен из SavedAF, SP=SavedSP+4 и исполнен внешний RET',
     "HL', DE', BC', AF', IXH, IY, I, IM, IFF и страница сохраняются до продолжения ядра"],
    ['HL, E, AF, IXL, SP, R, два байта CPU-стека непосредственного CALL помощника'],
    ['вход не является отдельной возвращающейся процедурой, жёсткий порядок после CircleRasterCore.asm сохраняется',
     'обычное продолжение переходит к CircleRasterCore.FastX, состояние альтернативной ошибки не сбрасывается',
     'отдельная модель PUSH-цепочек проверяет реальные помощники, R и все записи до FastX либо внешнего возврата',
     'полный последующий проход относится к моделям сечения, IRQ и нативный запуск не выполнены'])

COMMENTS={}
def before(pc,text):COMMENTS[pc]=([text],COMMENTS.get(pc,([],None))[1])
def condition(pc,text):COMMENTS[pc]=(COMMENTS.get(pc,([],None))[0],'переход, если '+text)
for pc in (0xD633,0xD73B,0xD833):before(pc,'Проверка исходной геометрии перед первым заполнением, SavedAF уже лежит на CPU-стеке.')
for pc in (0xD637,0xD742,0xD83A,0xD727,0xD81F,0xD911):before(pc,'Чтение Direction, нулевое значение выбирает движение вверх, единица движение вниз.')
for pc in (0xD63F,0xD74A,0xD842):before(pc,'Проверка допуска верхнего прохода, старшая страница правого адреса должна быть больше 7F.')
for pc in (0xD646,0xD751,0xD849):before(pc,'Проверка допуска нижнего прохода, старшая страница правого адреса должна быть не больше 8B.')
for pc in (0xD649,0xD754,0xD84C):before(pc,'Восстановление SavedAF и внешнего возврата без записи SavedSP и без рисования.')
for pc in (0xD64B,0xD756,0xD84E):before(pc,'Сохранение адреса SavedAF перед заполнением, этот стек нужен для обычного и нелокального выхода.')
for pc in (0xD64F,0xD6E2,0xD75A,0xD7E5):before(pc,'Обновление правого крайнего байта, включающая маска C сохраняет границу, остальные биты получают рисунок IXL.')
for pc in (0xD65A,0xD6ED,0xD854,0xD8D7):before(pc,'Обновление левого крайнего байта, включающая маска B сохраняет границу, остальные биты получают рисунок IXL.')
for pc in (0xD663,0xD6F6,0xD85D,0xD8E0):before(pc,'Расчёт числа полных байтов между исключёнными крайними байтами, остаток по модулю два заполняется отдельно.')
for pc in (0xD765,0xD7F0):before(pc,'Расчёт полных байтов от неподвижной левой границы, её байт включён в заполнение и не вычитается.')
for pc in (0xD681,0xD780,0xD87C):before(pc,'Расчёт новой вертикальной разности, два прибавления DEprime разделены увеличением только Eprime без переноса в Dprime.')
for pc in (0xD68A,0xD6C9,0xD885,0xD8BB):before(pc,'Сужение левого криволинейного края на один пиксель, перенос маски требует следующего байта E.')
for pc in (0xD68F,0xD6CE,0xD789,0xD7CC):before(pc,'Сужение правого криволинейного края на один пиксель, перенос маски требует предыдущего байта L.')
for pc in (0xD693,0xD6D2,0xD78D,0xD7D0,0xD88A,0xD8C0):before(pc,'Расчёт первого приращения по X в альтернативных парах, код отрицательного X увеличивается по модулю байта.')
for pc in (0xD696,0xD6D7):before(pc,'Продолжение с активным EXX, первое прибавление по X и INC C уже выполнены, осталось второе прибавление.')
for pc in (0xD791,0xD7D6,0xD88E,0xD8C6):before(pc,'Проверка порога Aprime по новому коду Cprime, совпадение снимает отсечение и передаёт второе приращение обычному ядру.')
for pc in (0xD7AA,0xD7B4):before(pc,'Проверка совпадения байтов перед снятием левого отсечения, последующий EXX возвращает арифметические пары в основной набор.')
for pc in (0xD6B1,0xD7BC,0xD8AC):before(pc,'Восстановление CPU-стека и SavedAF, активное состояние EXX намеренно не меняется.')
for pc in (0xD706,0xD7FE,0xD8F0):before(pc,'Расчёт смещения 16-A для выбора числа PUSH, сохранение краёв и создание пары одинаковых байтов рисунка в AF.')
for pc in (0xD714,0xD80C,0xD8FE):before(pc,'Замена CPU-стека адресом растра, изменённый JR направит исполнение в нужный хвост из шестнадцати PUSH.')
for pc in (0xD717,0xD80F,0xD901):before(pc,'Динамическая цепочка, каждый PUSH записывает пару байтов рисунка справа налево, настоящий стек восстановит продолжение.')
for pc in (0xD72B,0xD823,0xD915):before(pc,'Восстановление CPU-стека перед настоящим CALL шага строки, помощник может завершить весь рисователь.')
for pc in (0xD6DD,0xD7E0,0xD8D0):before(pc,'Подготовка вертикальной разности для следующей PUSH-строки, увеличение Eprime остаётся байтовым.')

for pc in (0xD635,):condition(pc,'младший левый адрес не меньше правого, завершить пустое сечение')
for pc in (0xD740,0xD838):condition(pc,'остаток адреса по модулю 32 не меньше 32, исходная недостижимая ветвь завершения сохранена')
for pc in (0xD63B,0xD746,0xD83E):condition(pc,'Direction ненулевой, проверить нижний предел страницы')
for pc in (0xD640,0xD74B,0xD843):condition(pc,'правый адрес выше страницы 7F, начать заполнение')
for pc in (0xD647,0xD752,0xD84A):condition(pc,'правый адрес не выше страницы 8B, начать заполнение')
for pc in (0xD668,0xD6FB,0xD769,0xD7F4,0xD862,0xD8E5):condition(pc,'число полных байтов чётное, перейти к заполнению парами без одиночного байта')
for pc in (0xD676,0xD776,0xD872,0xD72F,0xD827,0xD919):condition(pc,'Direction ненулевой, вызвать шаг вниз вместо шага вверх')
for pc in (0xD688,0xD787,0xD883):condition(pc,'вертикальная ошибка отрицательна, сохранить ширину и нарисовать следующую строку')
for pc in (0xD69A,0xD799,0xD896):condition(pc,'ошибка отрицательна, продолжить медленное заполнение текущей ширины')
for pc in (0xD68D,0xD6CC,0xD888,0xD8BE):condition(pc,'маска левого края перенесена за байт, увеличить адрес E')
for pc in (0xD691,0xD6D0,0xD78B,0xD7CE):condition(pc,'маска правого края перенесена за байт, уменьшить адрес L')
for pc in (0xD6A2,0xD6AB,0xD6BA,0xD6C3,0xD89E,0xD8B5):condition(pc,'байтовые адреса краёв совпали, восстановить стек и завершить сечение')
for pc in (0xD7A2,0xD7C6):condition(pc,'правый байт стал меньше неподвижного левого на один, завершить сечение')
for pc in (0xD6D5,0xD7D3,0xD8C3):condition(pc,'код Cprime обернулся в ноль, выйти до второго прибавления и обратного EXX')
for pc in (0xD6DB,0xD7DE,0xD8CE):condition(pc,'ошибка неотрицательна, продолжить горизонтальное сужение до следующей строки')
for pc in (0xD792,0xD7D7,0xD88F,0xD8C7):condition(pc,'Aprime совпал с новым Cprime, снять отсечение в соответствующей фазе')
for pc in (0xD7AD,0xD7B7):condition(pc,'байтовые адреса совпали при снятии отсечения, выйти с активным EXX')

STATE_FIELDS=(('NormalOdd',0xD672,'изменяемый байт LD A,n после одиночного байта обычного ядра'),
    ('NormalFastOdd',0xD705,'изменяемый байт LD A,n перед обычной PUSH-заливкой'),
    ('NormalPushJump',0xD716,'изменяемое смещение JR к обычному PUSH-хвосту'),
    ('LeftOdd',0xD772,'изменяемый байт LD A,n после левого неподвижного края'),
    ('LeftFastOdd',0xD7FD,'изменяемый байт LD A,n перед левой PUSH-заливкой'),
    ('LeftPushJump',0xD80E,'изменяемое смещение JR к левому PUSH-хвосту'),
    ('RightOdd',0xD86C,'изменяемый байт LD A,n после правого неподвижного края'),
    ('RightFastOdd',0xD8EF,'изменяемый байт LD A,n перед правой PUSH-заливкой'),
    ('RightPushJump',0xD900,'изменяемое смещение JR к правому PUSH-хвосту'))


def name_operands(region,address,operation):
    if region!='Controls' or address not in FUNCTIONS:return operation
    operation=operation.replace('(#D186)','(@ControlsRasterStepState.SavedSP)').replace('(#D18B)','(@ControlsCircleWork.Value.Direction)')
    for name,value,_ in STATE_FIELDS:
        operation=operation.replace('(#'+format(value,'04X')+')','(@ControlsCircleKernelsState.'+name+')')
    return operation
