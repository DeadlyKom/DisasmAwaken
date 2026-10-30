"""Первый ближайший вариант из шести курсоров, точный полный перенос при вычислении цели."""
FUNCTIONS={0xC5E8:('SelectNearestMapVariant','Выбор первого ближайшего варианта карты по текущим парам координат')}
DOCUMENTS={('Map',0xC5E8):('NearestMapVariant','шесть курсоров, необычные количества и полная арифметика целевой пары')}
LABELS={('Map',address):name for address,name in ((0xC60D,'AfterFirst'),(0xC61A,'AfterSecond'),(0xC627,'AfterThird'),
 (0xC634,'AfterFourth'),(0xC641,'AfterFifth'),(0xC64E,'StoreChoice'))}
CONTRACTS={('Map',0xC5E8):(
 ['HL - входная упакованная пара Origin, AF - A число вариантов, F не влияет на результат',
  'StationState.PointerXY содержит PointerWord, Cursor0..Cursor5 в MapVariantState указывают на доступные пары X,Y',
  'KARTA выбран и доступен для самомодификации, MapSelection.Variant доступен для записи, обычный стек доступен'],
 ['DE=Target=(PointerWord-(8*((Origin+0404)&FFFF)+0603))&FFFF, D целевой Y, E целевой X',
  'N=A при A=1..5, иначе N=6, рассмотрены первые N курсоров в исходном порядке',
  'MapDistanceState.Minimum содержит минимальную сумму квадратов знаковых байтовых разностей от Target',
  'HL=Cursor[N-1]+1 modulo 65536, BC - C индекс первого минимального варианта 0..N-1',
  'B=0 при N<6, иначе B=(входной A-5)&FF, A и MapSelection.Variant равны C',
  'при N<6 F=42 OR Carry последнего сравнения, при N=6 F сохранён от последнего UpdateMapDistanceMinimum',
  "HL', DE', BC', AF' соответствуют последнему UpdateMapDistanceMinimum, B'=0, C' сохранён",
  'IX, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2'],
 ["HL, DE, BC, AF, HL', DE', BC' только B', AF', Minimum и MapSelection.Variant"],
 ['первый кандидат всегда уменьшает начальное FFFF, поскольку сумма квадратов не превышает 32768',
  'при равных расстояниях индекс не меняется, получается первый из ближайших кандидатов',
  'количество 0 не означает пустой список, оно и любое A>=6 приводят к рассмотрению шести курсоров',
  'Origin складывается и масштабируется целым словом, переносы между координатными байтами не разделяются',
  'курсорные операнды и исходные пары не меняются, формат остальной части потоков ещё разбирается',
  'помощник расстояния учитывает знаковые байтовые разности, [его отдельный договор](../../Docs/MapDistanceMinimum.md)',
  'достижимость восстановлена через [действия интерфейса](../../Docs/StationEventActions.md)'])}
COMMENTS={
 0xC5E8:(['чтение текущей упакованной позиции указателя для преобразования в координаты вариантов'],None),
 0xC5EC:(['расчёт смещённой входной пары Origin+0404 с общим словным переносом'],None),
 0xC5F0:(['масштабирование всей смещённой пары в восемь раз тремя удвоениями слова'],None),
 0xC5F3:(['расчёт полного смещения вариантов добавлением исходной пары 0603'],None),
 0xC5F7:(['расчёт разности текущего указателя и полного смещения после очистки Carry'],None),
 0xC5FC:(['сброс изменяемого минимума к FFFF, любой первый квадрат расстояния меньше этого слова'],None),
 0xC602:(['подготовка оставшегося количества, ноль исходным кодом не отсекается'],None),
 0xC64E:(['сохранение индекса первого ближайшего варианта в общем состоянии карты'],None)}
for index,load,call,skip,choice in ((0,0xC603,0xC606,0xC609,0xC60B),(1,0xC610,0xC613,0xC616,0xC618),
 (2,0xC61D,0xC620,0xC623,0xC625),(3,0xC62A,0xC62D,0xC630,0xC632),(4,0xC637,0xC63A,0xC63D,0xC63F),
 (5,0xC644,0xC647,0xC64A,0xC64C)):
 COMMENTS[load]=(['чтение текущего курсора координат варианта '+str(index)],None)
 COMMENTS[call]=(['проверка строгого улучшения текущего минимального расстояния'],None)
 COMMENTS[skip]=([], 'переход, если вариант '+str(index)+' не ближе прежнего, сохранить выбранный индекс')
 COMMENTS[choice]=(['обновление выбранного индекса после строгого улучшения минимума'],None)
for address in (0xC60D,0xC61A,0xC627,0xC634,0xC641):
 COMMENTS[address]=(['расчёт оставшегося количества после очередного кандидата'],None)
 COMMENTS[address+1]=([], 'переход, если исходное количество кандидатов исчерпано, сохранить выбранный индекс')


def name_operands(region,address,operation):
 if region=='Map' and address==0xC5E8:
  operation=operation.replace('(#6307)','(@StationState.PointerXY)').replace('(#9848)','(@MapSelection.Variant)').replace('(#C668)','(@MapDistanceState.Minimum)')
  operation=operation.replace('LD BC, #0404','LD BC, @MapVariantConst.OriginBias').replace('LD BC, #0603','LD BC, @MapVariantConst.TargetBias').replace('LD HL, #FFFF','LD HL, @MapMathConst.InitialMinimum')
  for index,operand in enumerate((0xC6CA,0xC6E7,0xC704,0xC721,0xC73E,0xC75B)):
   operation=operation.replace('(#'+format(operand,'04X')+')','(@MapVariantState.Cursor'+str(index)+')')
 return operation
