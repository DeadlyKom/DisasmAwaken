"""Проверка кода цели и запаса, сообщение об отсутствии цели, сам пуск ещё не разобран."""
import re
from PreviewSceneTables import render as render_records,parse as parse_records
FUNCTIONS={
    0x709B:('ReportMissingMissileTarget','Передача в очередь сообщения об отсутствии захваченной цели с сохранением регистров'),
    0x70A4:('CheckMissileLaunch','Проверка кода захваченной цели и остатка ракет, очистка трёх захватов при пустом запасе')}
STATE_FIELDS=(('CommandDelay',0xA85F,'операнд LD A,n в UpdateFrame, проверка с имеющимся кодом цели записывает 5'),)
CONTRACTS={('Action',0x709B):(
    ['HL, DE, BC и AF сохраняются и числовых аргументов не задают',
     'действует договор QueueTextItemBank1, банк 1 содержит Controls, 7FFD не заблокирован',
     'код и внешний возврат находятся в общей RAM, доступны восемнадцать дополнительных байтов CPU-стека, IRQ не вмешиваются'],
    ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются",
     'SP=входной SP+2, сообщение F2C5 передано производителю очереди, очередь может молча отказать',
     'OUT 7FFD получает 11 и 10, на выходе выбран банк 0 с полной конфигурацией 10',
     'R получает стоимость QueueTextItem плюс 29 M1 обёртки и данного хвоста'],
    ['R, очередь и её курсор при успешной записи, восемнадцать байтов CPU-стека, регистр 7FFD'],
    ['это отдельный вход и общий хвост отказа CheckMissileLaunch, переход на него не создаёт дополнительной рамки CALL',
     'Z не формируется этой процедурой, входные флаги сохраняются даже при отказе очереди']) ,
 ('Action',0x70A4):(
    ['HL числового аргумента не задаёт, DE и BC сохраняются',
     'A код цели, FF означает отсутствие захвата, остальные значения здесь не проверяются на существование объекта',
     'входной Carry сохраняется только в результате отказа по коду FF, прочие входные флаги числового смысла не имеют',
     'ActionMissileStockState.Value задаёт запас, ActionMissileTargets.Value содержит три кода захвата',
     'действуют договоры SelectMissileStock и QueueTextItemBank1, очередь и общий стек доступны, 7FFD не заблокирован, IRQ не вмешиваются'],
    ['при входном A=FF HL, DE и BC сохраняются, A=00, F=50 OR входной Carry, сообщение об отсутствии цели передано очереди',
     'при A не равном FF HL задаёт выбранный счётчик запаса, DE и BC сохраняются, CommandDelay получает 5',
     'при ненулевом запасе A содержит выбранный остаток, F соответствует AND этого остатка, Z сброшен, цели не меняются',
     'при пустом запасе HL=9C12, AF=0044, три Target0..Target2 получают FF, сообщение F280 передано очереди',
     "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2",
     'счётчики ракет не уменьшаются, при обоих отказах 7FFD получает 11 и 10, при допуске OUT отсутствуют и страница сохраняется',
     'допуск исполняет 11 или 14 M1 в зависимости от выбранного поля, отказ без цели исполняет стоимость QueueTextItem плюс 31 M1, отказ по запасу плюс 48 M1'],
    ["HL, AF, R, CommandDelay при имеющемся коде цели, три кода захвата при пустом запасе, очередь и курсор при приёме сообщения, до восемнадцати байтов CPU-стека, 7FFD на путях отказа"],
    ['успешный допуск означает только код цели не FF и ненулевой остаток, выделение объекта и сам пуск происходят после возврата',
     'все отказы возвращают Z установленным независимо от того, приняла ли очередь сообщение',
     'CommandDelay не меняется при коде FF, но получает 5 даже при последующем отказе из-за пустого запаса',
     'проверка композиционная, реальные дочерние процедуры и переключения банков исполнялись без подмен'])}
COMMENTS={
 0x709B:(['Сохранение DE перед передачей фиксированного сообщения об отсутствии цели.'],None),
 0x709F:(['Добавление записи текста банка 1, регистрового признака приёма очередь не возвращает.'],None),
 0x70A4:(['-----------------------------------------','Проверка наличия кода захваченной цели','Инкремент распознаёт FF, Carry сохраняется для точного результата этого отказа.'],None),
 0x70A5:([],'переход, если входной код цели равен FF, передать сообщение и завершить проверку'),
 0x70A7:(['Установка задержки команд при любом имеющемся коде цели, до проверки запаса.'],None),
 0x70AC:(['-----------------------------------------','Проверка выбранного остатка ракет'],None),
 0x70AF:(['Проверка фактически возвращённого A, флаги читателя могли относиться к нулевому Preferred.'],None),
 0x70B0:([],'выход, если выбранный остаток ненулевой, два условия допуска выполнены'),
 0x70B1:(['-----------------------------------------','Снятие всех трёх захватов при пустом запасе'],None),
 0x70BC:(['Сохранение DE и постановка сообщения об исчерпанных ракетах.'],None),
 0x70C4:(['Формирование нулевого результата отказа независимо от приёма сообщения очередью.'],None)}
FIELDS=tuple(('Target'+str(i),1,'код захвата '+str(i)+', FF означает отсутствие цели, соответствие объектам ещё не установлено') for i in range(3))
TABLE=('ActionMissileTargets','Source/Action/Data/MissileTargets.asm',0x3B1B,0x3B1E,'FMissileTargets',FIELDS,('Value',))


def render(source):
    text,labels=render_records(source,TABLE,0x6000)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
        '[проверка перед пуском ракет](../../../Docs/ActionMissileLaunch.md)'),labels


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()]
    clean=[line for line in clean if line]
    assert clean.pop(0)=='module ActionMissileTargets' and clean.pop(0)=='assert $ == #9B1B'
    assert clean.pop(0)=='Value:          FMissileTargets {'
    for i in range(3):assert re.fullmatch(r'#[0-9A-F]{2}'+(',' if i<2 else ''),clean.pop(0))
    assert clean==['}','assert $ == #9B1E','endmodule']
    return parse_records(text,TABLE,0x6000)


def name_operands(region,function_address,operation):
    if region=='Action' and function_address in FUNCTIONS:
        operation=operation.replace('CALL #6040','CALL @Action.QueueTextItemBank1.Entry')
        operation=operation.replace('CALL #70ED','CALL @Action.SelectMissileStock.Entry')
        operation=operation.replace('JR Z, #709B','JR Z, @Action.ReportMissingMissileTarget.Entry')
        operation=operation.replace('LD DE, #F2C5','LD DE, @ActionMissileLaunchConst.NoTargetText')
        operation=operation.replace('LD DE, #F280','LD DE, @ActionMissileLaunchConst.EmptyStockText')
        operation=operation.replace('LD A, #05','LD A, @ActionMissileLaunchConst.DelayTicks')
        operation=operation.replace('LD A, #FF','LD A, @ActionMissileLaunchConst.NoTarget')
        operation=operation.replace('(#A85F)','(@ActionMissileLaunchState.CommandDelay)')
        for i,address in enumerate((0x9B1B,0x9B1C,0x9B1D)):
            operation=operation.replace('(#'+format(address,'04X')+')','(@ActionMissileTargets.Value.Target'+str(i)+')')
    return operation
