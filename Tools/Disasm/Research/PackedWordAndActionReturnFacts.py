"""Пополнение 16-битного резервуара и фактические кадры возврата непрямого действия."""
FUNCTIONS={0xA014:('RefillPackedBits','Чтение очередного слова битового потока из IX с восстановлением счётчика B из C без изменения флагов'),
 0x7F30:('ResumeActionPointer','Возобновление указателя после RET непрямого рисователя с продолжением восстановления AF'),
 0x7F33:('RestoreActionAF','Снятие сохранённого AF из динамического кадра и возврат внешнему обработчику')}
RENAMES={'UnknownA014':'RefillPackedBits','Unknown7F33':'RestoreActionAF'}
IN_PLACE={0x7F30}
LABELS={}
CONTINUATIONS={0x7F30:0x7F33}
CONTINUATION_SCOPES={0x7F30:'call_then_next_physical_fragment'}
DOCUMENTS={('Station',a):('PackedWordAndActionReturn','битовый резервуар, неизменность F, созданный на стеке возврат и SP+4') for a in FUNCTIONS}
CONTRACTS={('Station',0xA014):(
 ['BC содержит C исходное значение счётчика битов, B заменяется им буквально',
  'AF сохраняемый контекст, все биты F, включая Carry предыдущего сдвига, должны остаться исходными',
  'IX указывает на два читаемых байта следующего слова, стек содержит обычный возврат'],
 ['HL содержит little-endian слово от исходного IX, DE сохранён, B равен исходному C, C сохранён, AF сохранён',
  "HL', DE', BC', AF', IY, I, IFF и IM сохранены, IX увеличен на два по модулю 65536",
  'SP после RET равен входному+2, память и страница не меняются'],
 ['HL, B, IX'],
 ['IX является продвигаемым курсором потока, отдельная запись или буфер этим кодом не создаются',
  'UnpackResource читает биты ADD HL,HL, уменьшает B через DJNZ и использует оставшийся Carry после пополнения',
  'первичная подготовка битового контекста задаёт C=10, сама процедура не проверяет этот счётчик']),
 ('Station',0x7F33):(
 ['HL, DE, BC, AF и оба набора регистров сохраняемый контекст, кроме AF, загружаемого из стека',
  'SP указывает на FActionReturnFrame, SavedAF по +0, внешний ReturnAddress по +2',
  'обычный CALL без заранее сохранённого AF не соответствует этому входу'],
  ["HL, DE, BC, HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, AF равен SavedAF",
   'PC равен извлечённому внешнему ReturnAddress, SP увеличен на четыре по модулю 65536',
   'память, bitmap, указатель и страница не меняются'],
  ['AF, SP согласно динамическому кадру'],
  ['в SavedAF младший байт является F, старший A, сохраняются все восемь флаговых разрядов',
   'HandleStatusPanelAction создаёт этот кадр PUSH AF, ранний JP Z и продолжение 7F30 сходятся в одном хвосте']),
 ('Station',0x7F30):(
 ['HL, DE, BC и индексные регистры удовлетворяют ResumePointer, фоны, таблицы и параметры указателя подготовлены',
  'SP указывает на FActionReturnFrame после RET рисователя, SavedAF по +0 и внешний ReturnAddress по +2',
  'перед JP (HL) HandleStatusPanelAction создал FActionDrawFrame с DrawReturn=7F30, рисователь уже снял это первое слово'],
  ["HL, DE, BC, HL', DE', BC', IX и IY сохранены по ResumePointer, AF восстановлен из SavedAF",
   "AF' рабочий указателя, I, IFF и IM сохранены, страница не меняется",
   'UpdateBlocked=0, указатель возобновлён согласно его договору, PC равен внешнему ReturnAddress, SP увеличен на четыре'],
  ["AF, AF' по указателю, SP по кадру, bitmap и состояние указателя согласно ResumePointer"],
  ['единственная инструкция CALL ResumePointer занимает три ранее невыделенных байта CD D8 63 по 7F30',
   'после неё исполнение физически продолжается в RestoreActionAF, порядок include (0), (1) жёсткий',
   'полный HandleStatusPanelAction проверен отдельно в StatusPanelAction, произвольные рисователи ограничены своими договорами'])}
COMMENTS={0xA014:(['пополнение числа оставшихся битов, флаги последнего сдвига должны сохраниться'],None),
 0xA015:(['чтение младшего байта очередного слова и продвижение потокового курсора'],None),
 0xA01A:(['чтение старшего байта со следующей позиции и завершение продвижения на два'],None),
 0x7F30:(['возобновление указателя после снятия созданного DrawReturn рисователем'],None),
 0x7F33:(['восстановление SavedAF из FActionReturnFrame перед внешним CPU-возвратом'],None)}
TARGETS={0x63D8:'Station.ResumePointer.Entry',0x7F30:'Station.ResumeActionPointer.Entry'}


def name_operands(region,address,operation):
 if region!='Station':return operation
 if address==0x7F17:return operation.replace('#7F30','@Station.ResumeActionPointer.Entry')
 if address==0x7F30:return operation.replace('#63D8','@Station.ResumePointer.Entry')
 return operation
