"""Четыре угла, разности двух слов и запись точки, все регистры и байтовые оборачивания проверены."""
FUNCTIONS={0xE84E:('AppendPreviewClipPoint','Запись упакованной точки в страницу C8 с байтовым оборачиванием размера'),0xE846:('AppendPreviewClipSecond','Упаковка младших байтов второго конца и последовательный вход в запись точки'),0xE830:('SubtractPreviewClipColumns','Разность знаковых слов колонок второго и первого конца с точными флагами SBC'),0xE83B:('SubtractPreviewClipRows','Разность знаковых слов строк второго и первого конца с точными флагами SBC')}
CORNERS=((0xE7B4,'TopLeft','MinCorner'),(0xE7BF,'TopRight','MinXMaxY'),(0xE7CA,'BottomLeft','MaxXMinY'),(0xE7D5,'BottomRight','MaxCorner'))
for entry,name,operand in CORNERS:FUNCTIONS[entry]=('AppendPreviewClip'+name,'Добавление угла '+{'TopLeft':'сверху слева','TopRight':'сверху справа','BottomLeft':'снизу слева','BottomRight':'снизу справа'}[name]+' при нулевом запрете углов')
ENDS={0xE7B4:0xE7BF,0xE7BF:0xE7CA,0xE7CA:0xE7D5,0xE7D5:0xE7E0,0xE830:0xE83B,0xE83B:0xE846,0xE846:0xE84E,0xE84E:0xE85D}
LABELS={}
DOCUMENTS={('D3D',entry):('PreviewClipTail','точные флаги, оборачивание страницы, физические точки и углы после настоящей настройки') for entry in FUNCTIONS}
CONTINUATIONS={0xE846:0xE84E}
FUNCTION_SCOPES={0xE846:'point_source_then_append'}
ORDERED_INCLUDES={'AppendPreviewClipSecond':0,'AppendPreviewClipPoint':1}
DATA_WRITES={0xC22B:(1,'Source/D3D/Data/PreviewContourSize.asm')}
CONTRACTS={('D3D',0xE84E):(
 ['HL не является входом, DE содержит D строку и E колонку, два независимых байта',
  'BC сохраняемый контекст, AF - входной Carry сохраняется в результате, A не используется',
  'PreviewContourSize.Value.ByteCount содержит исходный байтовый курсор N, включая нечётные и граничные значения',
  'страница C8 и физический байт курсора доступны для записи, CPU-SP указывает на настоящий адрес возврата'],
 ['HL=C800+((N+2) AND FF), DE и BC сохранены',
  'AF - A=(N+2) AND FF, F от второго INC L, Carry равен входному',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
  'записаны E в C800+N, D в C800+((N+1) AND FF), затем новый курсор в ByteCount',
  'старший адрес C8 при оборачивании L не увеличивается, переход FF к 00 исходно разрешён'],
 ['HL, AF, два байта страницы C8 и ByteCount'],
 ['полный выходной буфер не проверяется, нечётный курсор и перезапись начала сохраняются как в исходнике',
  'F не является результатом проверки геометрической допустимости, размер сравнивает внешний диспетчер']),
 ('D3D',0xE846):(
 ['HL и DE не являются параметрами, BC сохраняемый контекст, AF - только Carry участвует в результате',
  'PreviewClipSecond.Value содержит координатные слова, ByteCount задаёт байтовый курсор C8'],
 ['HL=C800+((N+2) AND FF), DE содержит младший FirstAxis в D и младший SecondAxis в E',
  'BC сохранён, AF содержит новый курсор и F второго INC L с входным Carry',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после общего RET равен входному+2",
  'в страницу C8 последовательно записаны колонка и строка второго конца, ByteCount увеличен по модулю 256'],
 ['HL, DE, AF, два байта C8 и ByteCount'],
 ['старшие байты слов не читаются, это упаковка младших байтов, а не насыщение или дополнительное отсечение',
  'фрагмент без RET продолжается в AppendPreviewClipPoint, физический порядок двух файлов обязателен'])}
for entry,field,title in ((0xE830,'SecondAxis','колонок'),(0xE83B,'FirstAxis','строк')):
 CONTRACTS['D3D',entry]=(
  ['HL и DE не являются входами, BC сохраняется, AF - A сохраняется, входной Carry сбрасывается',
   'PreviewClipFirst.Value.'+field+' и PreviewClipSecond.Value.'+field+' содержат два 16-битных слова'],
  ['HL=(второй '+field+'-первый '+field+') AND FFFF, DE содержит первый '+field,
   'BC сохранён, AF - A сохранён, F принадлежит SBC HL, DE с нулевым входным Carry',
   "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2, записей в память нет"],
  ['HL, DE, AF - только F'],
  ['это обёрнутая словная разность '+title+', S не корректируется через P/V для математического знакового сравнения'])
for entry,name,operand in CORNERS:
 CONTRACTS['D3D',entry]=(
  ['HL, DE, BC сохраняемый контекст ветви отказа, AF не является параметром',
   'PreviewClipCorners.Value.BlockCode проверяется целиком, нуль разрешает добавление угла',
   'операнд D3DClipState.'+operand+' содержит выбранные строку и колонку после ConfigurePreviewClip',
   'ByteCount задаёт байтовый курсор, страница C8 доступна для записи'],
  ['при ненулевом BlockCode HL, DE и BC сохранены, A=BlockCode, F от AND A с H=1 и Carry=0',
   'при нулевом BlockCode HL=C800+новый курсор, DE выбранное слово угла, BC сохранён',
   'при добавлении A равен новому курсору, F от второго INC L с Carry=0 после AND A',
   "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
   'при отказе память сохранена, при разрешении записаны два байта угла и новый ByteCount'],
  ['при отказе AF, при добавлении HL, DE, AF, два байта C8 и ByteCount'],
  ['направления угла относятся к физической строке FirstAxis и колонке SecondAxis',
   'исходное слово LD DE сохранено, установщик меняет его операнд на месте, новая область памяти не создаётся'])
COMMENTS={
 0xE830:(['чтение слов колонок второго и первого конца'],None),0xE837:(['сброс входного Carry перед точной разностью без изменения A'],None),0xE838:(['расчёт обёрнутой 16-битной разности колонок'],None),
 0xE83B:(['чтение слов строк второго и первого конца'],None),0xE842:(['сброс входного Carry перед разностью строк'],None),0xE843:(['расчёт обёрнутой 16-битной разности строк'],None),
 0xE846:(['чтение младшего SecondAxis как колонки второго конца'],None),0xE84A:(['чтение младшего FirstAxis как строки, старшие байты координат не используются'],None),
 0xE84E:(['чтение исходного байтового курсора выходного контура'],None),0xE851:(['расчёт адреса C800+N без переноса между страницами'],None),
 0xE854:(['запись колонки перед строкой в исходной паре контура'],None),0xE855:(['продвижение к строковому байту только внутри страницы C8'],None),
 0xE856:(['запись строки после колонки'],None),0xE857:(['расчёт курсора следующей пары, Carry входного AF сохраняется'],None),0xE858:(['сохранение нового байтового размера, LD не меняет флаги второго INC'],None)}
for entry,_,operand in CORNERS:
 COMMENTS[entry]=(['чтение целого байта запрета углов без маскирования отдельных разрядов'],None)
 COMMENTS[entry+3]=(['проверка разрешения добавления выбранного угла'],None)
 COMMENTS[entry+4]=([], 'выход, если BlockCode ненулевой, добавление угла подавлено')
 COMMENTS[entry+5]=(['чтение слова угла из изменяемого операнда '+operand+', исходные байты сохранены'],None)
 COMMENTS[entry+8]=(['продолжение общей записи точки без дополнительного CPU-возврата'],None)


def name_operands(region,address,operation):
 if region!='D3D' or address not in FUNCTIONS:return operation
 data={0xC22C:'PreviewClipFirst.Value.SecondAxis',0xC22E:'PreviewClipFirst.Value.FirstAxis',0xC23C:'PreviewClipSecond.Value.SecondAxis',0xC23E:'PreviewClipSecond.Value.FirstAxis',0xC250:'PreviewClipCorners.Value.BlockCode',0xC22B:'PreviewContourSize.Value.ByteCount'}
 for pointer,label in data.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@'+label+')')
 return operation.replace('#E84E','@D3D.AppendPreviewClipPoint.Entry').replace('LD H, #C8','LD H, @PreviewPolygonConst.PointPage')
