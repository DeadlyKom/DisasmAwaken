"""Передний и задний вид, общий разворот базиса и три пары NOP либо NEG."""
import json
TAG='ActionViewDirectionCommand'
TITLE='переключение переднего и заднего вида'
CASES=2568
FUNCTIONS={0x762A:('ToggleViewDirection','Разворот базиса, обновление точек и согласованная смена трёх опкодных пар направления вида')}
ENDS={0x762A:0x7680}
KEYS={0x762A:0x19}
LOCAL={0x7663:'SelectRear'}
PAIRS=((0x6E75,'NegateFirst'),(0x6E88,'NegateSecond'),(0x6E9B,'NegateThird'))
MUTATIONS=((0x7632,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
    (0x7637,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
    *((writer,address,2,address,'Source/Action/UpdateMotionFromControls.asm') for writer,address in
      ((0x7649,0x6E75),(0x764C,0x6E88),(0x764F,0x6E9B),(0x7666,0x6E75),(0x7669,0x6E88),(0x766C,0x6E9B))))
CONTRACTS={('Action',0x762A):(
    ['HL, DE, BC и AF входных числовых аргументов не задают, BC сохраняемый контекст',
     'CommandDelay допускает обработку только при нуле, выбран банк 0, paging разблокирован',
     'действуют договоры NegateOuterBasisRows, InitializeBankedBufferPoints и QueueTextItemBank1, Controls банка 1 загружен',
     'первый байт NegateFirst выбирает направление, произвольные прежние байты остальных пар перезаписываются',
     'CPU-стек допускает восемнадцать дополнительных байтов, IRQ и повторный вход исключены'],
    ['при ненулевой задержке HL, DE и BC сохраняются, A содержит задержку, F соответствует AND A, запись памяти и OUT отсутствуют',
     'при допуске CursorA получает EE1B, CommandDelay получает 20, шесть слов базиса меняют знак по договору NegateOuterBasisRows',
     '35 точек банка 1 подготовлены заново, Seed обновлён 70 раз, BC сохраняется, DE содержит исходный C02 базиса',
     'при нулевом исходном первом байте три пары получают ED44, HL=44ED, переданы F1E1 и F239, выбран задний вид',
     'при любом ненулевом первом байте три пары получают 0000, HL=0000, переданы F1E1 и F228, выбран передний вид',
     'A содержит исходный первый байт, F соответствует AND этого байта, IX и IY сохраняются',
     "HL', DE', BC', AF' получают результаты InitializeBankedBufferPoints, I, IM и IFF сохраняются",
     'OUT 7FFD получает 11,10 три раза, итоговая полная конфигурация 10, каждая из двух строк очереди независимо принимается либо отклоняется',
     'SP после внешнего RET равен исходному SP+2, максимальная дополнительная глубина восемнадцать байтов'],
    ['HL, DE, AF, HL\', DE\', BC\', AF\', R, CommandDelay, CursorA, шесть слов базиса, точки и Seed банка 1, шесть байтов изменяемого кода, очередь, paging и восемнадцать временных байтов стека'],
    ['ED44 исполняется как NEG, 0000 как две NOP, длина и число M1 каждой пары равны двум, здесь пары только создаются',
     'каждое переключение сначала меняет знак базиса и перестраивает точки, даже при произвольном прежнем ненулевом первом байте',
     '2568 композиционных сценариев проверяют настоящие три дочерних тела, RAM и регистры кроме R и тактов',
     'исполнение созданных NEG отдельно проверено на 65536 знаковых словах, нативный вид и полный игровой кадр не проверялись'])}
COMMENTS={
 0x762A:(['Проверка задержки перед переключением переднего и заднего вида.'],None),
 0x762E:([],'выход, если CommandDelay ненулевой, базис, точки и опкоды сохранить'),
 0x762F:(['Выбор исходного звукового потока принятой команды.'],None),
 0x7635:(['Обновление задержки до разворота базиса и повторной подготовки точек.'],None),
 0x763A:(['Изменение знака двух внешних строк физического базиса, средняя строка сохраняется.'],None),
 0x763D:(['Повторная подготовка 35 банковых точек с 70 настоящими шагами генератора.'],None),
 0x7640:(['Проверка первого опкода режима, остальные две пары как входное условие не читаются.'],None),
 0x7644:([],'переход, если первый опкод равен нулю, записать NEG во все три пары и выбрать задний вид'),
 0x7646:(['Создание трёх пар NOP для переднего вида, все шесть прежних байтов перезаписываются.'],None),
 0x7652:(['Передача сообщения о включении выбранного режима, флаги проверки первого опкода сохраняются.'],None),
 0x765A:(['Передача названия переднего вида отдельным запросом очереди.'],None),
 0x7663:(['Создание трёх инструкций NEG из исходного слова 44ED, в памяти оно хранится ED,44.'],None),
 0x766F:(['Передача сообщения о включении выбранного режима, флаги проверки первого опкода сохраняются.'],None),
 0x7677:(['Передача названия заднего вида отдельным запросом очереди.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x762A:return operation
    replacements={'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
        '(#ECA9)':'(@ActionAyEffectState.CursorA)',
        'LD HL, #EE1B':'LD HL, @ActionViewDirectionConst.Sound',
        'LD A, #14':'LD A, @ActionViewDirectionConst.Delay',
        'LD HL, #0000':'LD HL, @ActionViewDirectionConst.ForwardPair',
        'LD HL, #44ED':'LD HL, @ActionViewDirectionConst.RearPair',
        'CALL #AFF5':'CALL @Action.NegateOuterBasisRows.Entry',
        'CALL #6CD6':'CALL @Action.InitializeBankedBufferPoints.Entry',
        'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry',
        '#7663':'@Action.ToggleViewDirection.SelectRear'}
    for address,name in PAIRS:replacements['(#'+format(address,'04X')+')']='(@Action.UpdateMotionFromControls.'+name+')'
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    path=root/'Source/Action/UpdateMotionFromControls.asm';text=path.read_text('utf-8')
    needle='                NOP\n                NOP';assert text.count(needle)==3
    for address,name in PAIRS:
        replacement='                ; Пара изменяемого кода, 0000 даёт две NOP, ED44 даёт NEG загруженного коэффициента.\n'+(name+':').ljust(16)+'NOP\n                NOP'
        text=text.replace(needle,replacement,1)
        key='Action.UpdateMotionFromControls.'+name;assert key not in symbols;symbols[key]=address
    pending[path]=text.encode('utf-8')
    path=root/'Tools/Disasm/Research/SemanticNames.py';text=pending[path].decode('utf-8')
    for address,name in PAIRS:text+=f"LABELS['Action',{address}]='{name}'\n"
    pending[path]=text.encode('utf-8')
    path=root/'Tools/Disasm/Research/ActionMotionWithoutKeysFacts.py';text=path.read_text('utf-8')
    text+='\nLOCAL.update('+repr(dict(PAIRS))+')\nLABELS.update({("Action",address):name for address,name in '+repr(dict(PAIRS))+'.items()})\n'
    pending[path]=text.encode('utf-8')
    path=root/'Includes/Variables/Include.inc';text=path.read_text('utf-8')
    needle='DepthSignMode   equ #6E75';lines=[];found=0
    for line in text.splitlines():
        if line.startswith(needle):
            line=needle.ljust(80)+'; 00 передний вид и +30000, ED задний вид и -30000, читается первый опкод пары\n                assert DepthSignMode == @Action.UpdateMotionFromControls.NegateFirst';found+=1
        lines.append(line)
    assert found==1;pending[path]=('\n'.join(lines)+'\n').encode('utf-8')
    path=root/'Includes/Const/Include.inc';text=path.read_text('utf-8');assert text.count('                endif')==1
    addition='                ; Исходные параметры переключателя направления вида\n                module ActionViewDirectionConst\n'
    for name,value,description in (('Sound','#EE1B','исходный поток AY-канала A'),('Delay','#14','задержка повторной команды, двадцать шагов обработчика'),
        ('ForwardPair','#0000','две NOP, загруженный коэффициент не меняется'),('RearPair','#44ED','NEG, в памяти ED,44, восьмибитное отрицание коэффициента')):
        addition+=(name.ljust(16)+'equ '+value).ljust(80)+'; '+description+'\n'
    addition+='                endmodule\n\n';pending[path]=text.replace('                endif',addition+'                endif').encode('utf-8')
    path=root/'Tools/Disasm/Reports/ModifiedCode.json';records=json.loads(pending[path])
    for record in records:
        if record['region']=='Action' and record['writer'] in (0x7649,0x764C,0x764F,0x7666,0x7669,0x766C):
            record.update(target_original_instruction_count=2,target_original_bytes='0000',target_runtime_byte_sequences=['0000','ed44'],generated_instruction='NEG')
    pending[path]=(json.dumps(records,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
