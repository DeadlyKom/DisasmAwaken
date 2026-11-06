"""Три самостоятельных договора близкой записи, дополнительный вход не выдаётся за доказанный игровой путь."""
FUNCTIONS={
 0xE506:('DispatchCloseRecord','Отбор близкой записи по коду запрета и классу с передачей в следующий режим либо инвертированием компонент'),
 0xE51F:('CheckCloseRecordComponents','Дополнительный отбор по биту 4 ReuseByte и старшим байтам трёх компонент'),
 0xE54A:('ReverseCloseRecordState','Уменьшение кода запрета, инвертирование масштабированных компонент и особое обнуление состояния класса 12')}
ENDS={0xE506:0xE51F,0xE51F:0xE54A,0xE54A:0xE55C}
LOCAL={0xE52D:'CheckComp0',0xE539:'CheckComp1',0xE545:'CheckComp2'}
CONTRACTS={('Action',0xE506):(
 ['HL, DE, BC и AF числовых аргументов не задают, при первом отказе HL, DE и BC сохраняются',
  "HL' адрес читаемой FActionRecord, остальные альтернативные входы числовых аргументов не задают",
  'InhibitCode задаёт полный код запрета, 00 допускает проверку, любой ненулевой байт завершает её',
  'действуют договоры ReverseCloseRecordState и TransferToStationLoader, банк 0 выбран, 7FFD не заблокирован, IRQ не вмешиваются',
  'общая RAM допускает до четырёх дополнительных байтов CPU-стека'],
 ['при InhibitCode не равном нулю HL, DE, BC и IX сохраняются, A=InhibitCode, F от AND A, RAM не меняется, внешний RET увеличивает SP на два',
  "при InhibitCode=0 IX получает HL', оба регистровых набора сохраняют принадлежность после двух EXX",
  'классы 11 и 14 возвращают A=ClassCode, F=42, HL, DE и BC сохраняются, SP увеличивается на два',
  'класс 12 передаёт управление TransferToStationLoader, HL и BC сохраняются, DE=0, AF=1142, PC=DCE3 банка 1, SP остаётся входным',
  'прочие классы переходят без новой рамки CALL в ReverseCloseRecordState, результат соответствует его договору',
  "HL', DE', BC', AF', IY, I, IM и IFF сохраняются в локальных границах, цель DCE3 не исполняется моделью",
  'R получает 3 M1 при запрете, 12 для класса 11, 14 для класса 14, 27 при передаче, 67 при инверсии'],
 ['HL, DE, BC и AF по пути, IX при допуске, R, временный CPU-стек до четырёх байтов, состояние общего хвоста, 7FFD только при передаче'],
 ['это корневой вход, он не проходит через дополнительную проверку E51F после исходного JP по E51C',
  'класс 11 совпадает с подтверждённым ClassCode создаваемой ракеты, игровой смысл класса 14 здесь не выдумывается',
  'передача к подготовке STATIONF не является подтверждённой дисковой загрузкой или возвратом в текущий кадр']) ,
 ('Action',0xE51F):(
 ['HL, DE, BC и AF числовых аргументов не задают, IX адрес читаемой FActionRecord',
  'InhibitCode может быть любым байтом, этот вход не выполняет корневую проверку запрета и не загружает IX из альтернативного HL',
  'действуют договоры ReverseCloseRecordState и TransferToStationLoader, банк 0 выбран, 7FFD не заблокирован, IRQ не вмешиваются',
  'общий CPU-стек допускает четыре дополнительных байта'],
 ['при сброшенном бите 4 ReuseByte либо отказе любой компоненты исполнение переходит ReverseCloseRecordState',
  'допуск компоненты проверяет старший байт, при его отрицательном знаке используется CPL без прибавления единицы',
  'каждая из трёх компонент допускает старшие байты 00..03 и FC..FF, иные значения передают общий хвост инверсии',
  'при установленном бите 4 и допуске всех трёх компонент HL и BC сохраняются, DE=0, AF=1193, SP входной, PC=DCE3 банка 1',
  "IX, альтернативные регистры, IY, I, IM и IFF сохраняются в локальных границах, при инверсии SP увеличивается на два",
  'ClassCode не фильтрует допуск передачи этого дополнительного входа, классы 11 и 14 не игнорируются автоматически'],
 ['HL, DE, BC и AF по пути, R, временный CPU-стек до четырёх байтов, состояние общего хвоста при отказе, 7FFD при передаче'],
 ['внешний игровой вызывающий путь E51F пока не установлен, прямые сценарии модели доказывают локальный договор, а не его фактический вызов',
  'проверка старших байтов не равна вычислению полного модуля слова и не заменяется NEG',
  'после последнего условного JP возможен проход в соседний ReverseCloseRecordState, include имеют жёсткий порядок']) ,
 ('Action',0xE54A):(
 ['HL, DE, BC и AF числовых аргументов не задают, DE и BC сохраняются, IX адрес читаемой FActionRecord',
  'InhibitCode задаёт исходный полный байт, ClassCode определяет дополнительное обнуление UnknownA794',
  'действует договор ReverseScaledVector, состояние доступно для записи, банк 0 выбран, два дополнительных байта CPU-стека доступны, IRQ не вмешиваются'],
 ['InhibitCode уменьшается на один по модулю 256, входной 00 превращается в FF',
  'Component0, Component2, Component1 меняют знак, SignedWord обновляется по договору ReverseScaledVector, EnabledCode получает 1',
  'HL новое SignedWord, DE и BC сохраняются, при классе не 12 A=ClassCode и F от CP с 12',
  'при классе 12 UnknownA794 получает 0 и AF=0044, это условие не заменяется корневым переходом в другой режим',
  "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2, OUT отсутствуют",
  'R получает 51 M1 для классов не 12 и 54 M1 для класса 12'],
 ['HL, AF, R, два байта временного CPU-стека, InhibitCode, три компоненты, SignedWord, EnabledCode, UnknownA794 только при классе 12'],
 ['InhibitCode уменьшается косвенным DEC (HL), писатель существующего операнда по E507 зарегистрирован отдельно',
  'игровой смысл UnknownA794 остаётся неизвестным, обнуление по классу 12 установлено точно'])}
COMMENTS={
 0xE506:(['Проверка полного InhibitCode, ноль допускает обработку записи, любые другие значения завершают её.'],None),
 0xE509:([],'выход, если InhibitCode ненулевой, запись и состояние не обрабатывать'),
 0xE50A:(['Получение адреса записи из альтернативного HL в IX с сохранением обоих регистровых наборов.'],None),
 0xE50F:(['Проверка ClassCode, корневой вход игнорирует класс создаваемой ракеты 11 и отдельный класс 14.'],None),
 0xE514:([],'выход, если ClassCode равен классу ракеты 11, состояние сохранить'),
 0xE517:([],'выход, если ClassCode равен IgnoredClass 14, состояние сохранить'),
 0xE518:(['Проверка класса передачи следующему режиму, другие классы направляются в общий хвост инверсии.'],None),
 0xE51A:([],'переход, если ClassCode не равен TransferClass 12, выполнить ReverseCloseRecordState'),
 0xE51C:(['Передача через TransferToStationLoader без дополнительного адреса возврата, в E51F прохода нет.'],None),
 0xE51F:(['Проверка бита 4 ReuseByte дополнительного входа, это не корневая проверка ClassCode.'],None),
 0xE523:([],'переход, если бит 4 ReuseByte сброшен, выполнить ReverseCloseRecordState'),
 0xE525:(['Проверка старшего байта Component0, для отрицательного значения применяется только инверсия CPL.'],None),
 0xE529:([],'переход, если старший байт Component0 неотрицателен, инверсию не выполнять'),
 0xE52D:(['Проверка нормализованного старшего байта Component0 относительно HighLimit.'],None),
 0xE52F:([],'переход, если проверяемый старший байт Component0 не меньше 4, выполнить общий хвост'),
 0xE531:(['Проверка старшего байта Component1 тем же преобразованием.'],None),
 0xE535:([],'переход, если старший байт Component1 неотрицателен, инверсию не выполнять'),
 0xE539:(['Проверка нормализованного старшего байта Component1 относительно HighLimit.'],None),
 0xE53B:([],'переход, если проверяемый старший байт Component1 не меньше 4, выполнить общий хвост'),
 0xE53D:(['Проверка старшего байта Component2 тем же преобразованием.'],None),
 0xE541:([],'переход, если старший байт Component2 неотрицателен, инверсию не выполнять'),
 0xE545:(['Проверка последней компоненты перед передачей следующему режиму.'],None),
 0xE547:([],'переход, если проверяемый старший байт Component2 меньше 4, выполнить TransferToStationLoader'),
 0xE54A:(['Уменьшение полного InhibitCode по модулю байта, исходное 00 получает FF.'],None),
 0xE54E:(['Инвертирование масштабированных компонент и отдельное обновление SignedWord настоящим дочерним вызовом.'],None),
 0xE551:(['Проверка ClassCode после инверсии, только класс 12 дополнительно обнуляет UnknownA794.'],None),
 0xE556:([],'выход, если ClassCode не равен 12, UnknownA794 сохранить'),
 0xE557:(['Обнуление неизвестного состояния UnknownA794 для класса 12 и формирование AF=0044.'],None)}


def name_operands(region,function_address,operation):
    if region=='Action':operation=operation.replace('(#E507)','(@ActionCloseRecordState.InhibitCode)')
    if region=='Action' and function_address in FUNCTIONS:
        operation=operation.replace('(IX+','(IX + ')
        for offset,name in ((1,'Components.Component0.High'),(3,'Components.Component1.High'),(5,'Components.Component2.High'),(18,'ClassCode'),(24,'ReuseByte')):
            operation=operation.replace('(IX + #'+format(offset,'02X')+')','(IX + FActionRecord.'+name+')')
        operation=operation.replace('LD HL, #E507','LD HL, @ActionCloseRecordState.InhibitCode')
        operation=operation.replace('(#A794)','(@ActionCloseRecordState.UnknownA794)')
        operation=operation.replace('CP #11','CP @ActionMissileCreateConst.MissileClass')
        operation=operation.replace('CP #14','CP @ActionCloseRecordConst.IgnoredClass')
        operation=operation.replace('CP #12','CP @ActionCloseRecordConst.TransferClass')
        operation=operation.replace('CP #04','CP @ActionCloseRecordConst.HighLimit')
        operation=operation.replace('BIT 4,','BIT @ActionCloseRecordConst.ComponentBit,')
        operation=operation.replace('CALL #6EDE','CALL @Action.ReverseScaledVector.Entry')
        operation=operation.replace('#6CE4','@Action.TransferToStationLoader.Entry')
    return operation
