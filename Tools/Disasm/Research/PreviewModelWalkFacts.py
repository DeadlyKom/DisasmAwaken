"""Два полных прохода физических групп моделей D819 и D896."""
FUNCTIONS={
 0xD819:('ProjectPlanarModelGroups','Подготовка относительного угла плоского входа и проекция всех физических групп выбранной модели'),
 0xD896:('ProjectPreviewModelGroups','Проекция всех физических групп выбранной модели через общую матрицу и восстановление CPU-стека')}
ENDS={0xD819:0xD85E,0xD896:0xD8BE}
LABELS={('D3D',0xD84A):'ReadGroup',('D3D',0xD8AA):'ReadGroup'}
DOCUMENTS={('D3D',entry):('PreviewModelGroups','исходные заголовки, 22 указателя, 62 группы, полная композиция проекции и точные регистры') for entry in FUNCTIONS}
CONST_MODULE='PreviewModelWalkConst'
CONSTANTS=()
CONTRACTS={}
for entry in FUNCTIONS:
 CONTRACTS['D3D',entry]=(
  ["DE, BC, AF - входной контекст, при пустом списке DE и младший C сохраняются",
   "ModelOffset в PreviewQueueState задаёт одно из 22 смещений 0,2,...,42 исходной страницы указателей D0",
   ("Coeff11..Coeff33 в PreviewMatrixComposeState содержат композицию матриц для общего входа" if entry==0xD896 else "AngleSecond и PreviewSharedSeed.Value.Unknown01 задают второй угол модели и вычитаемый угловой отсчёт"),
   "базы и центры перспективы уже подготовлены, показатель 1..6 читается из выбранного заголовка",
   "модель имеет заголовок из двух байтов, группы Mask/B/C/D и однобайтовый нулевой ограничитель",
   "суммарно не более 50 вершин, рабочая область страницы C6 не пересекается с кодом и CPU-стеком",
   "SP указывает на обычный CPU-возврат, под ним доступны шесть байтов вложенных вызовов и сохранённого указателя",
   "банк 4 доступен для записи, прерывания отключены, NMI и повторный вход исключены"],
  ["HL - адрес байта сразу после нулевого ограничителя групп, DE и BC принадлежат последнему генератору группы",
   "при пустом списке DE сохранён, B содержит показатель заголовка без бита 7, C сохранён",
   "AF - A=0, F=54 от AND нулевой маски перед условным RET",
   "HL', DE', BC', AF', IX и IY принадлежат последней группе, при пустом списке сохраняются",
   "NextOffset равен 4+5*n, где n число спроектированных вершин, все исходы проекции занимают одинаковый шаг",
   "три операнда JR масштаба настроены по заголовку, записи результатов и маркеров отказа выполнены в странице C6",
   ("CosFirst, SinFirst, SinSecond, CosSecond плоского входа не записываются" if entry==0xD896 else "CosFirst=CosSecond=S(delta+64), SinFirst=SinSecond=S(delta), delta=AngleSecond-Unknown01 по модулю 256"),
   "при непустом списке SavedSP генератора содержит входной CPU-SP минус четыре, после общего RET SP равен входному+2",
   "I, IFF и IM сохраняются, обычный CPU-адрес возврата не записывается"],
  ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, шесть байтов под CPU-SP, операнды и буфер проекции",
   "четыре операнда плоских коэффициентов дополнительно меняются только плоским входом"],
  ["первый байт размера заголовка пропускается, показатель и бит 7 читает ConfigurePreviewProjectionScale",
   "маска ноль завершает список до чтения остальных трёх байтов, нулевая группа не равна группе из нулевых координат",
   "после каждого вызова сохраняемый указатель восстанавливается из CPU-стека, рабочий SP восстанавливает генератор",
   "в образе 10 уникальных моделей с 62 группами, 22 указателя включают повторения и парные варианты",
   ("плоская процедура доказана как отдельный вход, её реальный игровой вызывающий путь пока не установлен" if entry==0xD819 else "этот вход вызывается проходом подготовленной очереди по EF39 после композиции матриц"),
   "Unknown01 в этом входе используется как угловой отсчёт, глобальное назначение трёх исходных Seed ещё не установлено"])
COMMENTS={
 0xD819:(["-----------------------------------------","Относительный угол плоской модели","-----------------------------------------","чтение исходного углового отсчёта, более общий смысл Unknown01 пока не установлен"],None),
 0xD81D:(["чтение второго угла текущего распакованного объекта"],None),
 0xD820:(["расчёт относительного угла с байтовым оборачиванием"],None),
 0xD822:(["расчёт индекса косинуса добавлением четверти оборота"],None),
 0xD824:(["поиск косинуса относительного угла в исходной странице синусоиды"],None),
 0xD828:(["обновление двух операндов косинуса плоского поставщика"],None),
 0xD82E:(["поиск синуса по сохранённому относительному углу"],None),
 0xD830:(["обновление двух операндов синуса плоского поставщика"],None)}
for entry,start,read,first,scale,mask,branch,parameters,push,call,pop,jump in (
 (0xD819,0xD836,0xD83C,0xD840,0xD845,0xD84A,0xD84D,0xD84E,0xD856,0xD857,0xD85A,0xD85B),
 (0xD896,0xD896,0xD89C,0xD8A0,0xD8A5,0xD8AA,0xD8AD,0xD8AE,0xD8B6,0xD8B7,0xD8BA,0xD8BB)):
 COMMENTS[start]=(["-----------------------------------------","Указатель модели и масштаб","-----------------------------------------","поиск выбранного указателя по ModelOffset в исходной странице D0"],None)
 COMMENTS[read]=(["чтение слова указателя модели, INC L не переносит переполнение в страницу"],None)
 COMMENTS[first]=(["установка исходного свободного смещения 4 для первой записи проекции"],None)
 COMMENTS[scale]=(["пропуск байта размера заголовка и подготовка трёх JR по показателю следующего байта"],None)
 COMMENTS[mask]=(["-----------------------------------------","Физические четырёхбайтовые группы","-----------------------------------------","чтение маски текущей группы с переходом указателя к первому параметру"],None)
 COMMENTS[mask+2]=(["проверка нулевой маски до чтения трёх параметров"],None)
 COMMENTS[branch]=([],"выход, если маска равна нулю, все группы модели завершены")
 COMMENTS[parameters]=(["сохранение маски в IXL и чтение трёх байтовых параметров группы в B, C, D"],None)
 COMMENTS[push]=(["сохранение указателя следующей группы в обычном CPU-стеке"],None)
 COMMENTS[call]=(["проекция группы через настоящий поставщик произведений, генератор и перспективу"],None)
 COMMENTS[pop]=(["восстановление указателя следующей физической группы после возврата генератора к CPU-стеку"],None)
 COMMENTS[jump]=(["продолжение обхода со следующей физической маски"],None)


def name_operands(region,address,operation):
 if region=='D3D' and address in FUNCTIONS:
  from PreviewQueueFacts import STATE
  from PreviewVertexProductsFacts import STATE as PLANAR_STATE
  for pointer,label in STATE.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@PreviewQueueState.'+label+')')
  for pointer,label in PLANAR_STATE.items():operation=operation.replace('(#'+format(pointer,'04X')+')','(@PreviewPlanarProductsState.'+label+')')
  operation=operation.replace('(#C201)','(@PreviewSharedSeed.Value.Unknown01)').replace('(#D90D)','(@PreviewVertexGroupState.NextOffset)')
  operation=operation.replace('LD H, #D0','LD H, @PreviewQueueBuildConst.ModelPage').replace('LD A, #04','LD A, @FPreviewProjectedVertex.Outcode')
  operation=operation.replace('LD H, #C4','LD H, @PreviewModelMatrixConst.SinePage').replace('ADD A, #40','ADD A, @PreviewModelMatrixConst.QuarterTurn')
  operation=operation.replace('CALL #DBD9','CALL @D3D.ConfigurePreviewProjectionScale.Entry').replace('CALL #D85E','CALL @D3D.ProjectPlanarVertexGroup.Entry').replace('CALL #D8BE','CALL @D3D.PreparePreviewVertexProducts.Entry')
  operation=operation.replace('#D84A','@D3D.ProjectPlanarModelGroups.ReadGroup').replace('#D8AA','@D3D.ProjectPreviewModelGroups.ReadGroup')
 return operation
