"""Четыре полных 32-битных вычитания, возвращающие только старшую половину и её флаги."""
PAIRS=((0xE7E0,'Top','Left'),(0xE7F4,'Top','Right'),(0xE808,'Bottom','Left'),(0xE81C,'Bottom','Right'))
FUNCTIONS={p:('SubtractPreviewClip'+first+second,'Разность кэшей '+first+' и '+second+' с заёмом младшего слова и возвратом старшего') for p,first,second in PAIRS}
ENDS={p:p+20 for p,_,_ in PAIRS}
LABELS={}
DOCUMENTS={('D3D',p):('PreviewClipProducts','физический разрыв левого кэша, перенос низкой половины, точные регистры и ограниченный смысл Z') for p,_,_ in PAIRS}
CONTRACTS={}
COMMENTS={}
for p,first,second in PAIRS:
 CONTRACTS['D3D',p]=(
  ['HL не является входом, DE сохраняется, BC не является входом, AF - A сохраняется, входной Carry сбрасывается',
   'кэши '+first+' и '+second+' содержат готовые 32-битные значения, низкая и высокая половины имеют исходные физические адреса',
   'для Left младшее слово C2EE и старшее C2FA разнесены, промежуточные байты не входят в кэш'],
  ['HL содержит старшее слово ('+first+'-'+second+') по модулю 2^32, младшая разность не возвращается',
   'DE сохранён, BC содержит старшее слово второго кэша '+second,
   'AF - A сохранён, F от старшего SBC HL, BC с заёмом младшей половины',
   'Z=1 означает нулевую старшую половину разности, младшая при этом может быть ненулевой',
   "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2, память не записывается"],
  ['HL, BC, AF - только F'],
  ['сброс Carry выполняется только перед младшей половиной, загрузки двух старших слов его не меняют',
   'это не проверка равенства полных кэшей через Z, знак S принадлежит обёрнутой 32-битной разности',
   'условия предварительной подготовки кэшей задают обработчики, полный разбор их путей ещё не завершён'])
 COMMENTS[p]=(['чтение младших слов кэшей '+first+' и '+second+' из фактических полей'],None)
 COMMENTS[p+7]=(['сброс входного Carry перед младшей разностью с сохранением A'],None)
 COMMENTS[p+8]=(['расчёт младшей половины и её заёма, сам младший результат дальше теряется'],None)
 COMMENTS[p+10]=(['чтение старших слов без изменения Carry младшей разности'],None)
 COMMENTS[p+17]=(['расчёт старшей половины с унаследованным заёмом, Z относится только к этой половине'],None)


def name_operands(region,address,operation):
 if region!='D3D' or address not in FUNCTIONS:return operation
 fields={0xC2DC:'PreviewClipTopProduct.Value.LowWord',0xC2DE:'PreviewClipTopProduct.Value.HighWord',0xC2EA:'PreviewClipBottomProduct.Value.LowWord',0xC2EC:'PreviewClipBottomProduct.Value.HighWord',0xC2EE:'PreviewClipLeftLow.Value.Word',0xC2FA:'PreviewClipLeftHigh.Value.Word',0xC2FC:'PreviewClipRightProduct.Value.LowWord',0xC2FE:'PreviewClipRightProduct.Value.HighWord'}
 for pointer,label in fields.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@'+label+')')
 return operation
