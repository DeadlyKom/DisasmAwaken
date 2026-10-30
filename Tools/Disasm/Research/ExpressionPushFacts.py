"""Байтовое и словное добавление в стек выражений, композиция доказанных читателей."""
FUNCTIONS={0xC1B5:('ReadCredits','Чтение исходного слова #984E и добавление его в стек выражений'),
 0xC241:('ReadFieldLowerj','Добавление байта #9850 в стек выражений через общий байтовый вход'),
 0xC24C:('ReadFieldUpperJ','Добавление байта #9851 в стек выражений'),
 0xC252:('PushTrue','Добавление логической единицы в стек выражений без изменения F'),
 0xC257:('PushFalse','Добавление нуля в стек выражений с F=#44'),
 0xC25B:('ReadEventCode','Добавление байтового кода события #983A в стек выражений'),
 0xC261:('ReadFieldLoweru','Добавление байта #984B в стек выражений')}
LABELS={('Text',0xC244):'AppendByte'}
DOCUMENTS={('Text',a):('ExpressionPushes','байтовая и словная запись, альтернативные пары и композиция') for a in FUNCTIONS}
DEST="HL' - адрес следующих двух доступных для записи байтов стека выражений, без перекрытия текущего кода и CPU-стека"
CONTRACTS={('Text',0xC1B5):(
 [DEST,'исходное слово по #984E доступно для чтения'],
 ['HL, BC и AF сохранены, DE прочитанное слово, записанное младшим байтом первым',
  "HL' увеличен на два, DE' копия DE, BC', AF', IX, IY, I и IFF сохранены",
  'SP обычного возврата равен входному SP+2'],
 ["DE, HL', DE'"],
 ['после LD DE,(#984E) исполнение последовательно входит в PushExpressionWord, жёсткий порядок include обязателен',
  'игровые единицы исходного слова отдельно не доказываются одним чтением'])}
for address in (0xC241,0xC24C,0xC252,0xC257,0xC25B,0xC261):
 value={0xC241:'байт #9850',0xC24C:'байт #9851',0xC252:'1',0xC257:'0',0xC25B:'байт #983A',0xC261:'байт #984B'}[address]
 inputs=[DEST,'источник '+value+' доступен']
 if address==0xC241:inputs+=['общий AppendByte принимает A как добавляемое байтовое значение']
 CONTRACTS['Text',address]=(
  inputs,
  ['HL, DE и BC сохранены, AF - A='+value+', F '+('=#44 от XOR A' if address==0xC257 else 'сохранён'),
   "HL' увеличен на два, в прежнюю позицию записано A, затем 0, DE', BC', AF', IX, IY, I и IFF сохранены",
   'SP обычного возврата равен входному SP+2'],
  ["AF"+(' только A' if address!=0xC257 else '')+", HL'"],
  ['байтовый вход не переносит результат в DE альтернативного набора, в отличие от PushExpressionWord',
   'запись имеет ширину слова, хотя источник байтовый, старший байт всегда нулевой'])
COMMENTS={
 0xC1B5:(['чтение исходного слова перед последовательным входом в PushExpressionWord'],None),
 0xC241:(['чтение сохранённого байта взвешенной суммы, единицы ещё не установлены'],None),
 0xC244:(['переход к альтернативному указателю стека выражений без переноса DE'],None),
 0xC245:(['запись младшего байта нового слова выражения'],None),
 0xC247:(['запись нулевого старшего байта для байтового результата'],None),
 0xC24A:(['возврат к основным регистрам, альтернативный указатель уже продвинут на два'],None),
 0xC24C:(['чтение исходного байта #9851 для добавления как слова'],None),
 0xC252:(['выбор логического значения 1 без пересчёта флагов'],None),
 0xC257:(['выбор нуля с Z=1, PV=1 и остальными сброшенными флагами'],None),
 0xC25B:(['чтение байтового кода события без изменения флагов'],None),
 0xC261:(['чтение исходного байта #984B без предположения о его игровых единицах'],None)}

WRAPPERS={49602: ('ReadFieldLowero', 'ReadEquipmentWeight'), 49638: ('ReadFieldLoweri', 'ReadSecondWeight'), 49665: ('ReadFieldLowerk', 'ReadSelectedPrimaryFields'), 49697: ('ReadFieldLowerr', 'ReadSelectedSecondaryFields'), 49767: ('ReadFieldUpperG', 'ReadMarketField'), 49801: ('ReadFieldUpperO', 'CheckEquipmentThreshold'), 49845: ('ReadFieldUpperI', 'CheckSecondEntryThreshold'), 49872: ('ReadFieldUpperK', 'ReadBank4PrimaryFields'), 49898: ('ReadFieldUpperR', 'ReadBank4SecondaryFields'), 49924: ('ReadFieldLowerg', 'ReadCargoField'), 50045: ('ReadFieldUpperL', 'ReadCurrentKeyParams'), 50067: ('ReadFieldLowerl', 'ReadOtherKeyParams'), 50089: ('ReadFieldUpperY', 'ReadCurrentKeyCodes'), 50111: ('ReadFieldLowery', 'ReadOtherKeyCodes')}

ALT_AF_WRITERS={'ReadEquipmentWeight','ReadSecondWeight','ReadMarketField','CheckEquipmentThreshold','CheckSecondEntryThreshold',
 'ReadCurrentKeyParams','ReadOtherKeyParams','ReadCurrentKeyCodes','ReadOtherKeyCodes'}
for address,(name,callee) in WRAPPERS.items():
 FUNCTIONS[address]=(name,'Получение результата через '+callee+' и запись слова в стек выражений')
 DOCUMENTS['Text',address]=('ExpressionPushes','композиция '+callee+' и PushExpressionWord')
 CONTRACTS['Text',address]=(
  [DEST,'выполняется входной договор '+callee+', для обычного результата допустим корректный суффикс',
   'читатель сохраняет альтернативный HL до записи результата, итоговый адрес остаётся доступным для двух байтов'],
  ['HL, DE, BC и AF по выходному договору '+callee+', DE дополнительно записан в стек выражений',
   "HL' увеличен на два относительно исходной позиции, DE' содержит записанный результат",
   "BC' и AF' по договору читателя, IX и IY также по его договору, I и IFF сохраняются",
   'SP обычного возврата равен входному SP+2, слово записано младшим байтом первым'],
  ["HL, DE, BC, AF, HL', DE', BC' только B"+(", AF' по пути читателя" if callee in ALT_AF_WRITERS else '')+', IX'],
  ['CALL читателя получает собственный возврат, затем JP PushExpressionWord использует исходный возврат обёртки',
   'дополнительных арифметических преобразований и пересчёта F обёртка не выполняет',
   'если читатель передаёт управление SkipLine вместо возврата, запись результата не достигается'])
 COMMENTS[address]=(['получение результата DE через '+callee+' с его исходными побочными эффектами'],None)
 COMMENTS[address+3]=(['добавление слова DE через общий PushExpressionWord, новый CALL не создаётся'],None)

CONTRACTS["Text",0xC3BF][3].append("запись y по #C9EC затенена ранней y по #C998, обычный DispatchReadField выбирает PushTrue")
