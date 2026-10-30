"""Статические исполняемые писатели трёх скалярных полей и их два вида CPU-рамки."""
ENTRIES={0xC642:('PushWordFieldWriter',0xC648,0xC652,0x984E,True),
 0xC657:('PushByteUWriter',0xC65D,0xC669,0x984B,False),
 0xC66E:('PushByteJWriter',0xC674,0xC680,0x9851,False)}
FUNCTIONS={a:(name,'Создание указателя писателя '+('слова' if word else 'байта')+' по #'+format(field,'04X')) for a,(name,invoke,store,field,word) in ENTRIES.items()}
DOCUMENTS={('Text',a):('ScalarWriters','создание указателя, рамка оператора и отдельный вход Store') for a in ENTRIES}
LABELS={};COMMENTS={};CONTRACTS={}
for address,(name,invoke,store,field,word) in ENTRIES.items():
 LABELS['Text',invoke]='Invoke';LABELS['Text',store]='Store'
 CONTRACTS['Text',address]=(
  ["Entry принимает HL' следующую позицию стека выражений, доступны два байта записи",
   'для Invoke на CPU-стеке FFieldInvokeFrame, Operator адрес операции, AfterStore адрес продолжения',
   'Invoke принимает BC правый операнд, поле #'+format(field,'04X')+' доступно для чтения и записи',
   'оператор получает DE текущее значение, BC правый операнд, возвращает DE через RET с банком LANG 6',
   'Store можно вызвать отдельно с DE результатом и обычным адресом возврата'],
  ['Entry сохраняет HL, BC и AF, DE адрес Invoke, добавленный в стек выражений',
   "Entry увеличивает HL' на два, DE' становится адресом Invoke, BC', AF', IX, IY, I и IFF сохранены",
   'Invoke заменяет Operator в FFieldInvokeFrame адресом Store, образуя FFieldOperatorFrame, и входит в оператор через JP (HL)',
   'после Invoke и Store поле получает '+('полное DE' if word else 'младший E без насыщения, старший D результата не записывается'),
   'регистры после Invoke определяются оператором и Store, '+('Store регистры не меняет' if word else 'Store устанавливает A=E, F сохраняет'),
   'SP после Entry либо отдельного Store равен входному SP+2, после полного Invoke равен входному SP+4'],
  ["Entry - DE, HL', DE'",'Invoke - HL, DE и регистры по договору выбранного оператора',('Store - нет' if word else 'Store - AF только A')],
  ['Entry не записывает целевое поле и не исполняет операцию, только добавляет статический указатель',
   'Invoke загружает текущее поле, а не значение на момент создания указателя, код писателя не генерируется заново',
   'байтовые Invoke читают слово, но обнуляют H, соседний байт поля не является частью операнда',
   'игровые единицы поля не выводятся из этой операции записи'])
 COMMENTS[address]=(['выбор статического входа Invoke как значения писателя поля'],None)
 COMMENTS[address+3]=(['добавление адреса Invoke в стек выражений без выполнения записи поля'],None)
 COMMENTS[invoke]=(['снятие адреса оператора из FFieldInvokeFrame в DE'],None)
 COMMENTS[invoke+1]=(['выбор Store как возврата оператора'],None)
 COMMENTS[invoke+4]=(['замена слова Operator адресом Store, остальная рамка сохраняется'],None)
 COMMENTS[invoke+5]=(['чтение текущего значения целевого поля в HL перед обменом с адресом оператора'],None)
 COMMENTS[store]=(['сохранение '+('полного слова DE' if word else 'младшего E через A без изменения F')+' в исходное поле'],None)


def name_operands(region,address,operation):
 if region!='Text' or address not in ENTRIES:return operation
 name,invoke,store,_,_=ENTRIES[address]
 return operation.replace('#'+format(invoke,'04X'),'@Text.'+name+'.Invoke').replace('#'+format(store,'04X'),'@Text.'+name+'.Store')
