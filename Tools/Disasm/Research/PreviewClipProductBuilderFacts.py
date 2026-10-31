"""Четыре производителя кэшей, два входа с готовой разностью и несимметричный E869."""
ITEMS=((0xE5E8,'Top',0xC2DC,0xC2DE),(0xE607,'Bottom',0xC2EA,0xC2EC),(0xE626,'Left',0xC2EE,0xC2FA),(0xE645,'Right',0xC2FC,0xC2FE))
FUNCTIONS={p:('BuildPreviewClip'+name+'Product','Формирование кэша '+name+' относительно границы с исходным порядком аргументов умножения') for p,name,_,_ in ITEMS}
ENDS={p:p+31 for p,_,_,_ in ITEMS}
LABELS={('D3D',0xE5F3):'FromDelta',('D3D',0xE612):'FromDelta'}
INTERNAL_ROOTS=(0xE5F3,0xE612)
DOCUMENTS={('D3D',p):('PreviewClipProducts','производители четырёх кэшей, внутренние входы, разности слов, точные регистры и второй множитель 8000') for p,_,_,_ in ITEMS}
DATA_WRITES={}
for p,name,low,high in ITEMS:
 low_path='Source/D3D/Data/PreviewClipLeftLow.asm' if name=='Left' else 'Source/D3D/Data/PreviewClip'+name+'Product.asm'
 high_path='Source/D3D/Data/PreviewClipLeftHigh.asm' if name=='Left' else low_path
 DATA_WRITES[low]=(2,low_path);DATA_WRITES[high]=(2,high_path)
CONTRACTS={}
COMMENTS={}
for p,name,low,high in ITEMS:
 horizontal=name in ('Top','Bottom')
 first='FirstAxis первого конца минус '+('MinX0' if name=='Top' else 'MaxX0') if horizontal else 'FirstAxis первого конца минус FirstAxis второго'
 second='SecondAxis первого конца минус SecondAxis второго' if horizontal else 'SecondAxis первого конца минус '+('MinY0' if name=='Left' else 'MaxY0')
 initial_bc='слово границы '+('MinX0' if name=='Top' else 'MaxX0') if horizontal else 'FirstAxis второго конца'
 CONTRACTS['D3D',p]=(
  ['HL, DE, BC и AF не являются параметрами полного Entry, два физических конца содержат координатные слова',
   'граница подготовлена ConfigurePreviewClip, старший байт слова LD BC сохраняет исходный нуль',
   "HL', DE', BC', AF' сохраняются, IX контекст коротких ветвей умножителя, IY сохраняется",
   'SP указывает на CPU-возврат, под ним доступны четыре байта вложенного CALL и сохранённого AF']+
  (['внутренний FromDelta принимает DE готовую разность колонок, слова колонок в этом входе не перечитываются'] if horizontal else []),
  ['HL и DE содержат старшее и младшее слова результата MultiplyPreviewSignedWords и записаны в кэш '+name,
   'BC определяется размерной ветвью и знаком умножителя, исходный BC его входа равен '+initial_bc,
   'AF - A равен XOR старших байтов двух аргументов, F от знакового XOR либо старшего SBC при отрицании результата',
   "HL', DE', BC', AF' сохранены, IX сохранён короткими ветвями, длинной заменён младшим словом модуля, IY сохранён",
   'I, IFF и IM сохранены, SP после RET равен входному+2, координатные записи не меняются',
   'записаны четыре байта выбранного кэша и четыре байта под входным SP, другие кэши и промежутки не записываются'],
  ['HL, DE, BC, AF, IX в длинной ветви, четыре байта кэша и четыре байта под CPU-SP'],
  ['первый аргумент HL равен '+first+', второй DE равен '+second,
   'каждая разность формируется отдельно по модулю 65536 с предварительным сбросом Carry',
   'порядок аргументов менять нельзя, для двух длинных модулей и второго 8000 умножитель использует эффективный множитель 256',
   'сам производитель не проверяет коды сторон или геометрическую допустимость, готовность кэша для следующего обработчика проверяется отдельно'])
 if horizontal:
  COMMENTS[p]=(['чтение колонок второго и первого конца для полной подготовки разности'],None)
  COMMENTS[p+7]=(['сброс Carry перед разностью колонок без изменения A'],None)
  COMMENTS[p+8]=(['расчёт разности колонок по модулю 65536'],None)
  COMMENTS[p+10]=(['сохранение разности колонок как второго аргумента DE'],None)
  COMMENTS[p+11]=(['внутренний вход с готовым DE, чтение изменяемого слова граничной строки'],None)
  COMMENTS[p+14]=(['чтение строки первого конца'],None)
 else:
  COMMENTS[p]=(['чтение изменяемого слова граничной колонки'],None)
  COMMENTS[p+3]=(['чтение колонки первого конца'],None)
  COMMENTS[p+6]=(['сброс Carry перед смещением колонки относительно границы'],None)
  COMMENTS[p+7]=(['расчёт смещения колонки, этот аргумент должен остаться вторым'],None)
  COMMENTS[p+9]=(['сохранение смещения колонки в DE'],None)
  COMMENTS[p+10]=(['чтение строк второго и первого конца для первого аргумента HL'],None)
 COMMENTS[p+17]=(['сброс Carry перед первой строковой разностью, заём колонки сюда не переносится'],None)
 COMMENTS[p+18]=(['расчёт строкового аргумента HL по модулю 65536'],None)
 COMMENTS[p+20]=(['вызов настоящего знакового умножителя с сохранением его особенности второго 8000'],None)
 COMMENTS[p+23]=(['запись младшего слова результата в физический кэш '+name],None)
 COMMENTS[p+27]=(['запись старшего слова без изменения флагов умножителя'],None)


def name_operands(region,address,operation):
 if region!='D3D' or address not in FUNCTIONS:return operation
 data={0xC22C:'PreviewClipFirst.Value.SecondAxis',0xC22E:'PreviewClipFirst.Value.FirstAxis',0xC23C:'PreviewClipSecond.Value.SecondAxis',0xC23E:'PreviewClipSecond.Value.FirstAxis',0xC2DC:'PreviewClipTopProduct.Value.LowWord',0xC2DE:'PreviewClipTopProduct.Value.HighWord',0xC2EA:'PreviewClipBottomProduct.Value.LowWord',0xC2EC:'PreviewClipBottomProduct.Value.HighWord',0xC2EE:'PreviewClipLeftLow.Value.Word',0xC2FA:'PreviewClipLeftHigh.Value.Word',0xC2FC:'PreviewClipRightProduct.Value.LowWord',0xC2FE:'PreviewClipRightProduct.Value.HighWord'}
 for pointer,label in data.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@'+label+')')
 return operation.replace('#E869','@D3D.MultiplyPreviewSignedWords.Entry')
