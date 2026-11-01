"""Редактирование подписей среды и игры, сохранение FSettingWord и прямые обёртки наведения."""
import re
FUNCTIONS={0x6AE9:('HandleEnvironmentHover','Передача наведения среды в обработчик её динамического числа строк'),
 0x6AEC:('HandleEnvironmentAction','Закрытие с применением настроек среды, прокрутка, Y/N и ограниченный ввод клавиш или цветов'),
 0x7599:('HandleGameSettingsHover','Передача наведения игры в обработчик её динамического числа строк'),
 0x759C:('HandleGameSettingsAction','Закрытие с применением игровых настроек, прокрутка и редактирование переключателя или клавиши')}
RENAMES={'HandleItem41':'HandleEnvironmentHover','Unknown6AEC':'HandleEnvironmentAction','HandleItem42':'HandleGameSettingsHover','Unknown759C':'HandleGameSettingsAction'}
LABELS={('Station',0x6B02):'ScrollRows',('Station',0x6B2C):'SelectValue',('Station',0x6B4C):'StoreToggle',('Station',0x6B4F):'BeginKeyEdit',
 ('Station',0x6B5E):'ReadKey',('Station',0x6B7A):'CheckBright',('Station',0x6B82):'StoreKey',('Station',0x6B84):'Redraw',
 ('Station',0x75B2):'ScrollRows',('Station',0x75DC):'SelectValue',('Station',0x75FB):'StoreToggle',('Station',0x75FE):'BeginKeyEdit',
 ('Station',0x760D):'ReadKey',('Station',0x7616):'Redraw'}
LABEL_RENAMES={}
for (_,address),label in LABELS.items():
 owner='HandleEnvironmentAction' if address<0x7000 else 'HandleGameSettingsAction';LABEL_RENAMES[owner+'.Point'+format(address,'04X')]=owner+'.'+label
DOCUMENTS={('Station',a):('SettingsPanelActions','применение FSettingWord при закрытии, байтовый выбор, клавиатура и реальные кадры стека') for a in FUNCTIONS}
CONTRACTS={}
for address,helper in ((0x6AE9,'UpdateEnvironmentHover'),(0x7599,'UpdateGameSettingsHover')):
 CONTRACTS['Station',address]=(
  ['выполняется договор '+helper+', IX указывает на соответствующий FInterfaceItem',
   'сохранённый номер строки, список рисования, указатель и окно подготовлены'],
  ['выполнен ровно хвостовой JP в '+helper+', самостоятельного кадра CALL нет',
   'HL, DE, BC, AF, альтернативные и индексные регистры, подсветка и указатель соответствуют его договору',
   'собственный код не меняет I, IFF и IM, SP обычного возврата входному+2'],
  ['только регистры и память, перечисленные договором '+helper],
  ['72 профиля прямого помощника и JP-обёртки дали одинаковые регистры, восемь банков памяти и записи портов'])
for address,kind,last,values,records,top,hover,renderer,conditional in (
 (0x6AEC,'среды',12,'SettingsText.Interface','InterfaceChoices.MouseOption','EnvironmentPanelState.TopRow','PanelHoverState.EnvironmentRow','DrawEnvironmentPanel','TryDrawEnvironmentPanel'),
 (0x759C,'игры',26,'SettingsText.Controls','ControlOptions.Unknown00','GameSettingsPanelState.TopRow','PanelHoverState.GameSettingsRow','DrawGameSettings','TryDrawGameSettings')):
 CONTRACTS['Station',address]=(
  ['HL запасной рисователь, DE ключ панели, BC, AF и IX выполняют договоры RepaintAndFlag и CloseMenuOnRow',
   'для закрытия '+values+' и массив FSettingWord от '+records+' доступны, подпись ограничена нулём',
   'для прокрутки окно безопасно для очистки, ввод, callback, указатель и IRQ удовлетворяют ScrollWindowRows',
   'для выбора младший TopRow и сохранённая строка дают допустимый индекс, родительские поля и стек доступны',
   'для редактирования существуют реальные пробуждения десяти HALT ReadMatrixKey и последующее допустимое нажатие, окно и рисователи подготовлены'],
  ['при Carry RepaintAndFlag возвращается его контекст, выбор, применение и прокрутка подавлены',
   'при Carry=0 и возвращённом A!=1 CloseMenuOnRow удаляет текущий ключ при совпадении символьных Y, затем ParseSettingsLabel применяет всю подпись',
   'закрытие возвращает HL контекста перед ParseSettingsLabel, DE за обработанными FSettingWord, BC у нуля подписи, AF=0054',
   'при несовпадении Y снимается старая XOR-полоса, сохранённая строка=FF, EndLimit='+str(last)+', RenderCall внутреннего RenderRows соответствующего рисователя',
   'ScrollWindowRows получает A=8 и полное слово TopRow, его итоговый HL записан обратно, остальные выходы согласно его договору',
   'выбор единицей при младшем TopRow=FF возвращает основной AF=0050 без редактирования и рисования',
   'иначе индекс равен TopRow.L плюс сохранённая строка по модулю 256, переключатель меняет Y на N, всякое иное старое значение на Y',
   'клавишное поле сначала получает подчёркивание, затем допустимый результат ReadMatrixKey, промежуточные отказы повторяют ввод',
   'после принятого значения BeginScreenUpdate, '+conditional+' и EndScreenUpdate дают A=10, F и HL, DE, BC результата последнего условного рисования',
   'на обычном завершении редактирования страница 10 и UpdateBlocked=0, альтернативные и индексные регистры по выполненным помощникам, SP после RET входному+2'],
  ["HL, DE, BC, AF, AF', BC' по прокрутке, IX по фактическим помощникам, подпись либо FSettingWord по ветви, список, экраны, указатель, TopRow, подсветка и операнды"],
  ['подпись меняется при выборе, FSettingWord записываются только при закрытии, исполнения всех будущих потребителей этим нет',
   'полный TopRow используется прокруткой, выбор читает только младший байт и не отвергает FF сохранённой строки',
   'индекс '+str(last)+' является исходным последним редактируемым индексом, фактическая проверка шага остаётся двухступенчатой в ScrollWindowRows',
   'после записи подчёркивания старое значение не восстанавливается, Cancel не предусмотрен, Caps Shift повторяет ввод',
   'FSettingsEditFrame описывает два сохранённых слова перед рисованием, после POP BC остаётся FSettingsWaitFrame',
   'модель реально сканирует матрицу, но HALT клавиатурной задержки освобождает явно без IRQ и без доказательства времени, IRQ рамки и прокрутки исполняются отдельно'])
CONTRACTS['Station',0x6AEC][3].extend([
 'индексы 0..3 переключают Y/N, 4..9 принимают любую клавишу кроме Caps Shift, 10..11 принимают коды 30..37, от 12 проверяются 30..31',
 'оба предварительных и заключительных обращения к панели условные, отсутствие точного адреса либо C9 может пропустить рисование и сброс подсветки'])
CONTRACTS['Station',0x759C][3].extend([
 'только индекс 0 переключает Y/N, остальные редактируемые индексы 1..26 принимают любую клавишу кроме Caps Shift',
 'перед ожиданием клавиши вызывается прямой DrawGameSettings, заключительный вызов условный, алиас ключа не заменяет точного адреса для последнего',
 'шаблон содержит 43 позиции, из них 16 последних CR-подписей пустые, предел исходной прокрутки остаётся 26, записи сохранены без сокращения'])
COMMENTS={
 0x6AE9:(['передача наведения в существующий обработчик строки среды без нового CPU-кадра'],None),
 0x6AEC:(['перерисовка и обработка геометрии до действия установок среды'],None),0x6AEF:([],'выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено'),
 0x6AF0:(['проверка единицы в возвращённом селекторе действия'],None),0x6AF1:([],'переход, если возвращённый селектор равен 1, выбрать значение'),
 0x6AF4:(['условное удаление текущей панели при совпадении символьных строк Y'],None),0x6AF7:([],'переход, если строки различаются, выполнить прокрутку'),
 0x6AF9:(['обновление физических FSettingWord из всей отредактированной подписи после удаления панели'],None),
 0x6B02:(['подготовка колонки среды и снятие прежней XOR-полосы'],None),0x6B0F:(['сброс сохранённой строки после снятия старой полосы'],None),
 0x6B14:(['обновление callback прокрутки, рамка и настройка повторно не вызываются'],None),0x6B1A:(['подготовка последнего индекса двенадцать и верхнего отступа 8'],None),
 0x6B22:(['чтение полного сохранённого индекса TopRow для прокрутки'],None),0x6B28:(['сохранение полного результата прокрутки'],None),
 0x6B2C:(['проверка FF только младшего байта TopRow'],None),0x6B30:([],'выход, если младший TopRow равен FF, ничего не редактировать'),
 0x6B31:(['расчёт байтового индекса значения, FF сохранённой строки отдельно не отбрасывается'],None),0x6B3E:(['проверка первых четырёх переключателей Y/N'],None),
 0x6B41:([],'переход, если индекс не меньше 4, начать клавиатурное редактирование'),
 0x6B43:(['проверка прежнего Y, только он меняется на N, остальные символы заменяются Y'],None),0x6B48:([],'переход, если прежнее значение равно Y, записать подготовленный N'),
 0x6B4C:(['обновление одного символа переключателя без немедленного изменения FSettingWord'],None),
 0x6B4F:(['обновление редактируемого символа подчёркиванием до начала ожидания клавиши'],None),
 0x6B52:(['создание экранного снимка перед показом промежуточного подчёркивания'],None),
 0x6B55:(['создание FSettingsWaitFrame с ValuePointer поверх внешнего ReturnAddress'],None),
 0x6B56:(['создание FSettingsEditFrame с SavedIndex поверх ValuePointer и ReturnAddress'],None),
 0x6B57:(['условное рисование промежуточного состояния только при точном адресе панели'],None),
 0x6B5D:(['восстановление SavedIndex, на стеке остаётся FSettingsWaitFrame'],None),
 0x6B5E:(['ожидание кода настоящей матрицы после десяти пробуждений HALT'],None),
 0x6B61:(['проверка Caps Shift, эта клавиша не завершает редактирование'],None),0x6B63:([],'переход, если прочитан Caps Shift, снова ждать клавишу'),
 0x6B65:(['сохранение кода клавиши и проверка класса выбранного поля'],None),0x6B69:([],'переход, если индекс меньше 10, принять любую клавишу кроме Caps Shift'),
 0x6B6B:(['проверка однобитового Bright по индексу не меньше 12'],None),0x6B6E:([],'переход, если индекс не меньше 12, проверить цифру 0 либо 1'),
 0x6B70:(['проверка нижней границы цифр Ink и Paper'],None),0x6B72:([],'переход, если код меньше цифры 0, повторить ввод'),
 0x6B74:(['проверка верхней исключающей границы цифры 8 для Ink и Paper'],None),0x6B76:([],'переход, если код не меньше цифры 8, повторить ввод'),
 0x6B7A:(['проверка нижней границы цифр Bright'],None),0x6B7C:([],'переход, если код меньше цифры 0, повторить ввод'),
 0x6B7E:(['проверка верхней исключающей границы цифры 2 для Bright'],None),0x6B80:([],'переход, если код не меньше цифры 2, повторить ввод'),
 0x6B82:(['восстановление ValuePointer из FSettingsWaitFrame, далее на стеке обычный возврат'],None),0x6B83:(['обновление ровно одного символа принятой клавишей либо цифрой'],None),
 0x6B84:(['создание снимка и условная перерисовка принятого значения'],None),0x6B8A:(['возобновление указателя и показ базового экрана'],None),
 0x7599:(['передача наведения игры в существующий обработчик строки без нового CPU-кадра'],None),
 0x759C:(['перерисовка и обработка геометрии перед действием установок игры'],None),0x759F:([],'выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено'),
 0x75A0:(['проверка единицы возвращённого селектора для выбора значения'],None),0x75A1:([],'переход, если возвращённый селектор равен 1, выбрать значение'),
 0x75A4:(['условное удаление текущей панели при совпадении символьных Y'],None),0x75A7:([],'переход, если строки различаются, выполнить прокрутку'),
 0x75A9:(['обновление физических FSettingWord всей игровой подписью после удаления панели'],None),
 0x75B2:(['подготовка игровой колонки и снятие прежней XOR-полосы'],None),0x75BF:(['сброс номера подсветки после снятия старой полосы'],None),
 0x75C4:(['обновление callback на внутренний RenderRows без новой рамки'],None),0x75CA:(['подготовка последнего индекса 26 для исходной прокрутки'],None),
 0x75D0:(['подготовка отступа 8 и полного TopRow'],None),0x75D8:(['сохранение полного итогового индекса прокрутки'],None),
 0x75DC:(['проверка FF только младшего байта TopRow'],None),0x75E0:([],'выход, если младший TopRow равен FF, ничего не редактировать'),
 0x75E1:(['расчёт байтовой суммы TopRow и сохранённой строки, FF строки отдельно не проверяется'],None),
 0x75EF:(['проверка единственного переключателя с индексом ноль'],None),0x75F0:([],'переход, если индекс ненулевой, начать ввод клавиши'),
 0x75F2:(['проверка прежнего Y, он меняется на N, остальные символы заменяются Y'],None),0x75F7:([],'переход, если прежнее значение равно Y, записать подготовленный N'),
 0x75FB:(['обновление одного символа переключателя без записи физических настроек'],None),
 0x75FE:(['обновление символа подчёркиванием перед ожиданием клавиши'],None),
 0x7601:(['создание снимка экрана перед промежуточным состоянием'],None),0x7604:(['создание FSettingsWaitFrame с ValuePointer поверх внешнего возврата'],None),
 0x7605:(['создание FSettingsEditFrame с SavedIndex поверх кадра ожидания'],None),
 0x7606:(['прямое рисование промежуточного состояния игры независимо от точного указателя списка'],None),
 0x760C:(['восстановление SavedIndex, на стеке остаётся ValuePointer и внешний возврат'],None),
 0x760D:(['ожидание кода клавиатурной матрицы после десяти пробуждений HALT'],None),0x7610:(['проверка Caps Shift перед записью принятой клавиши'],None),
 0x7612:([],'переход, если прочитан Caps Shift, повторить ожидание'),0x7614:(['снятие ValuePointer кадра ожидания после принятого кода'],None),
 0x7615:(['обновление ровно одного символа принятой клавишей'],None),0x7616:(['создание снимка и условная перерисовка окончательного значения'],None),
 0x761C:(['возобновление указателя и показ базового экрана'],None)}
TARGETS={0x6B8E:'Station.UpdateEnvironmentHover.Entry',0x7620:'Station.UpdateGameSettingsHover.Entry',0xCBEB:'Station.RepaintAndFlag.Entry',
 0x6B2C:'Station.HandleEnvironmentAction.SelectValue',0xC85E:'Station.CloseMenuOnRow.Entry',0x6B02:'Station.HandleEnvironmentAction.ScrollRows',
 0x9728:'SettingsText.Interface',0x99AE:'InterfaceChoices.MouseOption',0xA191:'Station.ParseSettingsLabel.Entry',0x6C00:'Station.SetupEnvironmentText.Entry',
 0x6B8F:'EnvironmentPanelState.HoverRows',0x6B95:'PanelHoverState.EnvironmentRow',0xA26F:'Station.XorRowIfSelected.Entry',
 0x6BB6:'Station.DrawEnvironmentPanel.RenderRows',0x6B23:'EnvironmentPanelState.TopRow',0xA1D6:'Station.ScrollWindowRows.Entry',
 0x6B4F:'Station.HandleEnvironmentAction.BeginKeyEdit',0x6B4C:'Station.HandleEnvironmentAction.StoreToggle',0x6B84:'Station.HandleEnvironmentAction.Redraw',
 0xA49F:'Station.BeginScreenUpdate.Entry',0x6B9E:'Station.TryDrawEnvironmentPanel.Entry',0xA496:'Station.EndScreenUpdate.Entry',
 0xA116:'Station.ReadMatrixKey.Entry',0x6B5E:'Station.HandleEnvironmentAction.ReadKey',0x6B82:'Station.HandleEnvironmentAction.StoreKey',0x6B7A:'Station.HandleEnvironmentAction.CheckBright',
 0x75DC:'Station.HandleGameSettingsAction.SelectValue',0x75B2:'Station.HandleGameSettingsAction.ScrollRows',0x9736:'SettingsText.Controls',0x99C8:'ControlOptions.Unknown00',
 0x766C:'Station.SetupGameSettingsText.Entry',0x7621:'GameSettingsPanelState.HoverRows',0x7627:'PanelHoverState.GameSettingsRow',
 0x7648:'Station.DrawGameSettings.RenderRows',0x75D3:'GameSettingsPanelState.TopRow',0x75FE:'Station.HandleGameSettingsAction.BeginKeyEdit',
 0x75FB:'Station.HandleGameSettingsAction.StoreToggle',0x7616:'Station.HandleGameSettingsAction.Redraw',0x7637:'Station.DrawGameSettings.Entry',
 0x760D:'Station.HandleGameSettingsAction.ReadKey',0x7630:'Station.TryDrawGameSettings.Entry'}
MODIFIED_WRITES=((0x6B11,0x6B95,'Station',0x6B94,1,5),(0x6B17,0xA265,'Station',0xA264,2,2),(0x6B1D,0xA235,'Station',0xA234,2,2),(0x6B28,0x6B23,'Station',0x6B22,2,5),
 (0x75C1,0x7627,'Station',0x7626,1,5),(0x75C7,0xA265,'Station',0xA264,2,2),(0x75CD,0xA235,'Station',0xA234,2,2),(0x75D8,0x75D3,'Station',0x75D2,2,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 for old,new in (('CP #59','CP @SettingsLabelConst.YesChar'),('LD A, #4E','LD A, @SettingsLabelConst.NoChar'),('LD A, #59','LD A, @SettingsLabelConst.YesChar'),
  ('CP #1D','CP @SettingsEditConst.CapsShift'),('CP #30','CP @SettingsLabelConst.DigitZero'),('CP #38','CP @SettingsEditConst.InkLimit'),('CP #32','CP @SettingsEditConst.BitLimit'),
  ('LD (HL), #5F','LD (HL), @SettingsEditConst.PendingGlyph'),('LD HL, #000C','LD HL, @SettingsEditConst.EnvLastRow'),('LD HL, #001A','LD HL, @SettingsEditConst.GameLastRow'),
  ('CP #04','CP @SettingsEditConst.ToggleCount'),('CP #0A','CP @SettingsEditConst.ColorStart'),('CP #0C','CP @SettingsEditConst.BrightIndex')):operation=operation.replace(old,new)
 return operation
