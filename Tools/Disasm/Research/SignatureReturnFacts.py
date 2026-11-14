"""Обёртки характеристики, возвращающие банк 6 вместо станционного банка 0."""
from WorldSignatureFacts import CONTRACTS as KEY_CONTRACTS
FUNCTIONS={0xA480:('DescribeCurrentKeyForLang','Характеристика текущего ключа с возвратом банка языка 6'),
 0xA48B:('DescribeKeyForLang','Характеристика входного ключа с возвратом банка языка 6')}
DOCUMENTS={('Station',a):('SignatureReturn','договор результата и последовательность страниц 1, 0, 6') for a in FUNCTIONS}
CONTRACTS={}
for address,base in ((0xA480,0xA464),(0xA48B,0xA46E)):
 inputs,outputs,corrupt,notes=KEY_CONTRACTS['Station',base]
 inputs=[s.replace('HL - FirstWord, DE - SecondWord, AF - A Variant=0..255, BC сохраняемый контекст','HL - FirstWord, DE - SecondWord, BC сохраняемый контекст, AF - A Variant=0..255') for s in inputs]
 CONTRACTS['Station',address]=(
  [*[s for s in inputs if 'возврат исполняется' not in s],'возврат должен находиться в фиксированной памяти либо в банке LANG 6'],
  ['HL, DE, BC и основной AF имеют результат соответствующего DescribeCurrentKey либо DescribeKeyBanked',
   "HL', DE', BC' сохранены",
   "AF' содержит страницу (входная CurrentPage AND #F8) OR #16 и флаги её OR",
   'IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2',
   'порт #7FFD и тень последовательно получают страницы с младшими битами 1, 0, 6 и принудительным ROM 1'],
  ["HL, DE, AF, AF', R, SignatureState.WorkKey, CurrentPage, порт #7FFD и временный CPU-стек"],
  ['через банковое ядро четыре байта WorkKey инициализируются входными словами, затем обновляются Variant+1 раз',
   'CurrentPage и порт #7FFD изменяются трижды, собственные CALL обёртки и вложенные сохранения пишут временный CPU-стек',
   'исходное слово возврата сохраняется, POP не очищает временные записи RAM, R зависит от генерации характеристики',
   'входные старшие биты страницы сохраняются, исходный номер RAM-банка не восстанавливается',
   'итоговый основной AF сохраняется через два EX AF вокруг третьего выбора страницы',
   'точные признаки и формулы результата описаны в WorldSignature.md, алгоритм ядра не меняется'])
COMMENTS={}
for address,callee in ((0xA480,'DescribeCurrentKey'),(0xA48B,'DescribeKeyBanked')):
 COMMENTS[address]=(['получение исходной характеристики через '+callee+', временный возврат в банк 0'],None)
 COMMENTS[address+3]=(['сохранение основного AF результата перед выбором банка языка'],None)
 COMMENTS[address+4]=(['выбор банка LANG 6 с установленным ROM 1'],None)
 COMMENTS[address+9]=(['восстановление AF характеристики, результат выбора страницы остаётся в альтернативном AF'],None)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 return operation.replace('CALL #A464','CALL @Station.DescribeCurrentKey.Entry').replace('CALL #A46E','CALL @Station.DescribeKeyBanked.Entry').replace('CALL #6396','CALL @Station.SelectRamBank.Entry')
