"""Кнопка Контракт, точные абсолютные ROM-чтения и полное центрирование по доказанному профилю AF."""
import re
from DeferredActionAdapterFacts import CONTRACTS as ADAPTER_CONTRACTS
from DrawAdapterFacts import CONTRACTS as DRAW_CONTRACTS
FUNCTIONS={0x7CBC:('InstallContractMapCallback','Установка отложенного центрирования карты кнопкой Контракт'),
 0x7CC6:('CenterContractMap','Выбор четырёхбайтового ключа и центрирование карты контракта с исходными абсолютными чтениями ROM'),
 0x7CF8:('DrawContractButton','Центрируемая кнопка Контракт с исходным текстовым индексом 20 и изменяемым индексом элемента 18')}
RENAMES={'HandleItem18':'InstallContractMapCallback','Unknown7CC6':'CenterContractMap','DrawItem18':'DrawContractButton'}
LABELS={('Station',0x7CBF):'BindCallback',('Station',0x7CCE):'AdvanceCursor',('Station',0x7CD9):'CheckNonzero'}
LABEL_RENAMES={'InstallContractMapCallback.Point7CBF':'InstallContractMapCallback.BindCallback',
 'CenterContractMap.Point7CCE':'CenterContractMap.AdvanceCursor','CenterContractMap.Point7CD9':'CenterContractMap.CheckNonzero'}
DOCUMENTS={('Station',a):('ContractMap','исходная подсказка, абсолютный ROM 0001, сохранение курсора и полный путь к карте') for a in FUNCTIONS}
CONTRACTS={('Station',0x7CBC):tuple([line.replace('ConfirmShipModelTrade','CenterContractMap') for line in part] for part in ADAPTER_CONTRACTS['Station',0x79BD]),
 ('Station',0x7CF8):tuple(list(part) for part in DRAW_CONTRACTS['Station',0x7CF8]),
 ('Station',0x7CC6):(
 ['HL, DE и AF входа не являются выбранным ключом, BC сохраняется до общего центрирующего хвоста',
  'ContractMapState.Cursor доступен для записи, оба абсолютных чтения ContractMapConst.RomProbe доступны в текущем отображении ROM',
  'для возвращения локальной петли требуется ненулевое первое чтение, при постоянном нуле локального выхода нет',
  'рассчитанные четыре байта выбранного ключа читаемы, действует договор CenterKeyAndRefreshMap с готовой геометрией и списками',
  'полный путь требует исходных KARTA 1, станции 0, шрифта, таблиц, двух экранов и корректного IRQ в HALT',
  'для профиля ROM[0001]=AF стабилен, выбранный ключ находится в первых двух словах MissionOffer.Entry независимо от старого курсора'],
 ['MissionOffer.Entry.MessageIndex всегда получает DecodedMessageConst.AlienSignal перед проверками',
  'перед первым чтением Cursor увеличивается в HL, ненулевой байт с bit7=0 сохраняет увеличенный адрес, с bit7=1 заменяет его MapAuxiliaryCodes.State',
  'нулевое первое чтение повторяет INC HL без сохранения Cursor, SP на этой петле не меняется',
  'после ненулевого первого чтения Cursor записан, затем нулевое второе чтение даёт RET с HL=Cursor, DE и BC сохранены, AF=0054',
  'иначе адрес ключа=(MissionOffer.Entry+4*(Cursor-MapAuxiliaryCodes.State)) AND FFFF, DE=FirstWord и HL=SecondWord перед общим хвостом',
  'до хвоста BC, альтернативные и индексные регистры, I, IFF и IM сохранены, собственных переключений страниц нет',
  'при стабильном AF Cursor всегда MapAuxiliaryCodes.State, выбирается ключ предложения MissionOffer.Entry, смена старого курсора следующий контракт не выбирает',
  'общий хвост определяет выбранную систему и вариант по списку A, центрирует начало и перерисовывает карту с условной панелью сведений',
  'после полного хвоста HL, DE, BC, AF, альтернативные пары и IX соответствуют RefreshStoredMapPanels, IY сохранён при договоре IRQ',
  'полный путь возвращает страницу 10 и возобновляет указатель, обычный SP после возврата входному+2, собственного запроса Pending нет'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX по общему рисунку, MessageIndex, Cursor, выбранный ключ, начало карты, экран и рабочие данные помощников"],
 ['подсказка исходного элемента 18 говорит о следующем выбранном контракте, фактический профиль AF всегда выбирает первое предложение',
  'обе инструкции LD A,(0001) сохранены, они не читают содержимое адреса HL, предполагаемая ошибка оригинала не исправляется',
  'положительные и изменяющиеся ROM-байты описаны формулой, вся последующая область MissionOffer не объявляется массивом контрактных ключей',
  'неизвестные промежуточные поля предложения и игровые значения нетипичного положительного ROM сохраняют отдельную неопределённость',
  'локальная 48K-часть pentagon.rom побайтово совпала с ROM прежней модели, файл 48for128.rom отличается одним байтом 006D, оба содержат AF по 0001',
  'полное действие проверено 96 случаями и 240 IM2, процесс Unreal не исследовался, независимый bitmap всей карты не вычислялся'])}
CONTRACTS['Station',0x7CF8][3].append('исходный TextIndex=20 выбирает подпись Контракт и подсказку о центрировании следующего выбранного контракта')
COMMENTS={0x7CBC:(['переход к установке отложенного центрирования контракта'],None),0x7CBF:(['выбор CenterContractMap как новой цели callback'],None),
 0x7CC2:(['сохранение цели и общая развилка геометрии либо активации, немедленного центрирования нет'],None),
 0x7CC6:(['выбор предупреждения об иносигнале для последующей расшифровки'],None),0x7CC8:(['обновление числового селектора сообщения перед любыми ROM-проверками'],None),
 0x7CCB:(['чтение изменяемого курсора, исходно база кодов MapAuxiliaryCodes.State'],None),0x7CCE:(['расчёт следующего адреса курсора, его содержимое не используется в следующем чтении'],None),
 0x7CCF:(['чтение абсолютного ROM-адреса RomProbe, исходные байты 3A 01 00 сохранены'],None),0x7CD2:(['проверка знака и нуля первого абсолютного байта ROM'],None),
 0x7CD3:([],'переход, если первое чтение неотрицательно, проверить его ноль с увеличенным курсором'),
 0x7CD6:(['замена курсора базой кодов при установленном bit7 ROM, профиль AF выбирает именно этот путь'],None),
 0x7CD9:([],'переход, если первое чтение равно нулю, повторить увеличение без сохранения курсора'),
 0x7CDB:(['обновление сохраняемого курсора только после ненулевого первого чтения'],None),0x7CDE:(['повторное абсолютное чтение того же ROM-адреса, не чтение через HL'],None),
 0x7CE1:(['проверка нуля второго ROM-чтения после записи курсора'],None),0x7CE2:([],'выход, если второе чтение равно нулю, сохранить уже записанный курсор'),
 0x7CE3:(['выбор базы кодов для вычисления относительного индекса'],None),0x7CE6:(['расчёт относительного индекса по модулю 65536, AND перед ним очистил Carry'],None),
 0x7CE8:(['расчёт удвоенного относительного индекса'],None),0x7CE9:(['расчёт четырёхбайтового смещения ключа'],None),0x7CEA:(['выбор базы первого ключа предложения, положительный ROM может дать другие физические поля'],None),
 0x7CED:(['расчёт физического адреса выбранных четырёх байтов с оборачиванием слова'],None),0x7CEE:(['чтение первого слова ключа в DE и второго в HL для общего центрирования'],None),
 0x7CF6:(['передача ключа общему центрированию и полному рисунку карты с исходным возвратом'],None),
 0x7CF8:(['чтение изменяемого индекса кнопки Контракт, штатно 18'],None)}
TARGETS={0x7CBF:'Station.InstallContractMapCallback.BindCallback',0x7CC6:'Station.CenterContractMap.Entry',0xCC21:'Station.ActivateInterfaceCallback.Entry',
 0x98BF:'MissionOffer.Entry.MessageIndex',0x99A3:'MapAuxiliaryCodes.State',0x7CCC:'ContractMapState.Cursor',0x0001:'ContractMapConst.RomProbe',
 0x7CCE:'Station.CenterContractMap.AdvanceCursor',0x7CD9:'Station.CenterContractMap.CheckNonzero',0x98B0:'MissionOffer.Entry',0x7D14:'Station.CenterKeyAndRefreshMap.Entry',0xC2DF:'Station.DrawCenteredItem.Entry'}
MODIFIED_WRITES=((0x7CDB,0x7CCC,'Station',0x7CCB,2,5),)


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 if address==0x7CC6:operation=operation.replace('LD A, #01','LD A, @DecodedMessageConst.AlienSignal')
 return operation
