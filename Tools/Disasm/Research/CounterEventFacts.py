"""Счётчик имеет настоящий пустой EventHandler с внутренним RET, а не обновление таймера."""
import re
FUNCTIONS={0xA6EA:('IgnoreCounterEvent','Пустой обработчик события счётчика, исходный JP во внутренний RET без изменения данных')}
RENAMES={'HandleItem01':'IgnoreCounterEvent'}
LABELS={('Station',0xA6ED):'ReturnNoop'}
LABEL_RENAMES={'IgnoreCounterEvent.PointA6ED':'IgnoreCounterEvent.ReturnNoop'}
DOCUMENTS={('Station',0xA6EA):('CounterEvent','полное сохранение AF, отдельный внутренний вход и отсутствие тика счётчика')}
CONTRACTS={('Station',0xA6EA):(
 ['HL, DE, BC, AF, альтернативные и индексные пары произвольны и сохраняются',
  'CPU-стек содержит читаемый адрес возврата, станционный код по A6EA и A6ED доступен'],
 ['HL, DE, BC, AF, альтернативные пары, IX, IY, I, IFF и IM сохранены',
  'память и порты не меняются, SP увеличен на два, PC снят с прежней вершины CPU-стека',
  'R увеличен на два через Entry и на один при прямом внутреннем входе ReturnNoop, старший бит R сохранён'],
 ['только SP, PC и R по исходным JP и RET'],
 ['Entry не обновляет BCD-счётчик и не читает ввод, обработка накопленного Pulse находится в основном цикле',
  'диспетчер может войти прямо в ReturnNoop=Entry+3, оба входа сохраняют полный AF',
  'проверены все 65536 AF для каждого входа и полная неизменность памяти, сборка и нативный запуск не выполнялись'])}
COMMENTS={0xA6EA:(['передача события во внутренний пустой возврат, счётчик здесь не обновляется'],None),0xA6ED:(['возврат с исходными AF и остальными общими регистрами'],None)}
TARGETS={0xA6ED:'Station.IgnoreCounterEvent.ReturnNoop'}


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
