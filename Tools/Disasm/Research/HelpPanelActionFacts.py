"""Действия справки, связанное закрытие, прокрутка и выбор LF-записи через CR-список."""
import re
FUNCTIONS={0x6978:('HandleHelpTextHover','Пустая JP-обёртка наведения панели текста справки'),
 0x697B:('HandleHelpTextAction','Закрытие связанной пары либо прокрутка LF-текста, выбор единицей ничего не делает'),
 0x69A7:('IgnoreHelpTextHover','Пустой обработчик наведения текста справки с немедленным RET'),
 0x69E0:('HandleHelpContentsAction','Закрытие пары, прокрутка CR-заголовков либо выбор раздела с перерисовкой обеих панелей')}
RENAMES={'HandleItem23':'HandleHelpTextHover','Unknown697B':'HandleHelpTextAction','Unknown69A7':'IgnoreHelpTextHover','Unknown69E0':'HandleHelpContentsAction'}
LABELS={('Station',0x698E):'ScrollRows',('Station',0x69A6):'NoSelection',('Station',0x69F4):'ScrollTitles',('Station',0x6A1E):'SelectSection'}
LABEL_RENAMES={'HandleHelpTextAction.Point698E':'HandleHelpTextAction.ScrollRows','HandleHelpTextAction.Point69A6':'HandleHelpTextAction.NoSelection',
 'HandleHelpContentsAction.Point69F4':'HandleHelpContentsAction.ScrollTitles','HandleHelpContentsAction.Point6A1E':'HandleHelpContentsAction.SelectSection'}
DOCUMENTS={('Station',a):('HelpPanelActions','полный селектор, закрытие двух ключей, прокрутка и отсутствие проверки FF подсветки') for a in FUNCTIONS}
NOOP=(['нет параметров, обычный адрес возврата доступен в CPU-стеке'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",'память, список рисования, курсор и страницы не меняются'],
 ['нет, кроме обычного потребления CPU-возврата'],['HandleHelpTextHover выполняет JP к IgnoreHelpTextHover, отдельного кадра CALL не создаёт'])
CONTRACTS={('Station',0x6978):NOOP,('Station',0x69A7):NOOP,
 ('Station',0x697B):(
 ['HL запасной рисователь текущего элемента, DE его ключ, BC и AF контекст RepaintAndFlag',
  'IX, указатель и геометрия выполняют договор перерисовки, действует договор CloseMenuOnRow и DropItemDraw',
  'для прокрутки HelpPanelState.LineCount и кэш подготовлены, TopLine допустим, окно и ввод удовлетворяют ScrollWindowRows'],
 ['при Carry RepaintAndFlag немедленно возвращается его контекст, последующие действия подавлены',
  'при Carry=0 и возвращённом A=1 выполняются DEC A и RET, основной AF=0042, выбор раздела не производится',
  'при совпадении символьных строк указателя и окна удаляется текущий ключ, затем первый ключ ContentsIndex',
  'иначе RenderCall=PrintHelpLine, EndLimit=LineCount, A=8 и HL=TopLine передаются ScrollWindowRows',
  'после прокрутки полный итоговый HL записан в TopLine, остальные выходы определяет договор ScrollWindowRows',
  'HL, DE, BC, AF, альтернативные и индексные регистры соответствуют фактически выполненным помощникам, SP после возврата входному+2'],
 ["HL, DE, BC, AF, AF', BC' при прокрутке, список, экраны, указатель, TopLine и операнды ScrollWindowRows по ветви"],
 ['удаление ищет первый совпадающий индекс, переносит фиксированные 128 байтов и учитывает алиасы рисователя',
  'CloseMenuOnRow удаляет текущую панель до второго DropItemDraw, X указателя не участвует в сравнении',
  'прокрутка принудительно завершает на странице 10 и восстанавливает исходные координаты указателя']),
 ('Station',0x69E0):(
 ['HL, DE, BC, AF и IX удовлетворяют RepaintAndFlag, CloseMenuOnRow, XorRowIfSelected и ScrollWindowRows',
  'для выбора раздела ContentsTop и IndexRow задают существующую LF-запись после байтового сложения, обе панели доступны',
  'для перерисовки выполняются договоры DrawHelpText и DrawHelpContents, IRQ сохраняет рабочий контекст',
  'для прокрутки геометрия безопасна, исходный банк станции 0 выбран и аппаратное переключение не заблокировано'],
 ['при Carry RepaintAndFlag немедленно возвращается его контекст, при A=1 и Carry=0 выполняется SelectSection',
  'в прочих случаях совпадение символьных строк удаляет текущий ключ, затем первый ключ TextIndex',
  'при несовпадении отключается перенос, прежняя XOR-полоса снимается, IndexRow=FF',
  'прокрутка получает RenderCall=DrawHelpContents.RenderTitles, EndLimit=7, A=8, HL=ContentsTop, итоговый HL записан в ContentsTop',
  'SelectSection при младшем ContentsTop=FF возвращает AF=0050 без сброса TopLine, смены записи и рисования',
  'иначе TopLine=0, выбранный байт равен ContentsTop.L+IndexRow по модулю 256 и записан через Help.SelectText',
  'после выбора BeginScreenUpdate, DrawHelpText, DrawHelpContents и EndScreenUpdate дают итоговые HL, DE, BC последнего рисователя и A=10 с сохранённым его F',
  'IndexRow после перерисовки равен FF, VisibleTitles обновлён, ContentsTop сохранён, банк и страница равны 10, SP после возврата входному+2'],
 ["HL, DE, BC, AF, AF', IX и BC' по фактическим помощникам, список, экраны, курсор, указатель, TopLine, ContentsTop, IndexRow, VisibleTitles, кэш и операнды"],
 ['FF проверяется только в младшем ContentsTop, старший байт не участвует в выборе, IndexRow=FF отдельно не отвергается',
  'все 65280 суммы проверены до SelectText, недопустимые полученные номера не передавались индексатору',
  'номер 7 является последним индексом восьми заголовков, это параметр предела ScrollWindowRows, не число строк окна',
  'открытие скрытого экрана и две перерисовки выполняются только после принятого выбора, временный код рисователей также учитывается их договорами'])}
COMMENTS={
 0x6978:(['передача наведения в пустой обработчик без нового CPU-возврата'],None),
 0x697B:(['перерисовка и обработка геометрии до выбора дальнейшего действия'],None),
 0x697E:([],'выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено'),
 0x697F:(['проверка селектора 1, для текста он не выбирает запись'],None),
 0x6980:([],'переход, если возвращённый селектор равен 1, завершить без выбора'),
 0x6982:(['условное закрытие текущей панели по совпадению символьных строк Y'],None),
 0x6985:([],'переход, если строки различаются, выполнить прокрутку текста'),
 0x6987:(['чтение ключа связанного списка разделов перед вторым удалением'],None),
 0x698E:(['обновление callback прокрутки, используется межбанковая печать текста без рамки'],None),
 0x6994:(['чтение полного числа индексированных строк как предела прокрутки'],None),
 0x699A:(['подготовка верхнего отступа 8 пикселей и сохранённого индекса TopLine'],None),
 0x69A2:(['сохранение полного итогового индекса верхней строки'],None),
 0x69A6:(['пустая ветвь выбора текста, возвращается результат DEC селектора 1'],None),
 0x69A7:(['пустое наведение панели текста, строки здесь не подсвечиваются'],None),
 0x69E0:(['перерисовка и обработка геометрии перед действием списка разделов'],None),
 0x69E3:([],'выход, если RepaintAndFlag вернул Carry, выбор и прокрутка подавлены'),
 0x69E4:(['проверка селектора 1 для перехода к выбору раздела'],None),
 0x69E5:([],'переход, если возвращённый селектор равен 1, выбрать раздел'),
 0x69E8:(['условное удаление текущего списка по совпадению символьных строк Y'],None),
 0x69EB:([],'переход, если строки различаются, снять подсветку и прокрутить список'),
 0x69ED:(['чтение ключа связанной текстовой панели перед вторым удалением'],None),
 0x69F4:(['отключение переноса перед повторной печатью CR-заголовков'],None),
 0x69F7:(['чтение текущих высоты наведения и пиксельного отступа из операнда UpdateIndexListHover'],None),
 0x69FE:(['снятие прежней XOR-полосы, FF не рисует полосу'],None),
 0x6A01:(['сброс номера подсветки после снятия старого изображения'],None),
 0x6A06:(['обновление callback на внутренний вход печати заголовков без новой рамки'],None),
 0x6A0C:(['подготовка предела 7 для восьми исходных CR-заголовков'],None),
 0x6A12:(['подготовка верхнего отступа 8 и полного индекса ContentsTop'],None),
 0x6A1A:(['сохранение полного итогового индекса списка разделов'],None),
 0x6A1E:(['проверка маркера FF только в младшем байте ContentsTop'],None),
 0x6A22:([],'выход, если младший ContentsTop равен FF, не выбирать запись'),
 0x6A25:(['сброс полной прокрутки текстовой панели перед сменой записи'],None),
 0x6A2B:(['расчёт байтового номера LF-записи, IndexRow=FF отдельно не проверяется'],None),
 0x6A2F:(['сохранение номера в альтернативном AF на время выбора банка HELP'],None),
 0x6A36:(['обновление операнда выбранной LF-записи в банке 7'],None),
 0x6A39:(['возврат банка станции перед скрытым обновлением обеих панелей'],None),
 0x6A3E:(['создание экранного снимка и отключение обновления указателя'],None),
 0x6A41:(['перерисовка LF-текста от сброшенной верхней строки'],None),
 0x6A44:(['перерисовка списка, сброс XOR-состояния и обновление видимого числа строк'],None),
 0x6A47:(['возобновление указателя и показ обновлённого базового экрана'],None)}
TARGETS={0xCBEB:'Station.RepaintAndFlag.Entry',0x69A6:'Station.HandleHelpTextAction.NoSelection',0xC85E:'Station.CloseMenuOnRow.Entry',
 0x698E:'Station.HandleHelpTextAction.ScrollRows',0x6A5C:'HelpPanelState.ContentsIndex',0xC873:'Station.DropItemDraw.Entry',0x69CF:'Station.PrintHelpLine.Entry',
 0x699D:'HelpPanelState.TopLine',0xA1D6:'Station.ScrollWindowRows.Entry',0x69A7:'Station.IgnoreHelpTextHover.Entry',0x6A1E:'Station.HandleHelpContentsAction.SelectSection',
 0x69F4:'Station.HandleHelpContentsAction.ScrollTitles',0x69A9:'HelpPanelState.TextIndex',0x6A7E:'Station.DisableTextWrap.Entry',0x6A4C:'HelpPanelState.HoverRows',
 0x6A52:'PanelHoverState.IndexRow',0xA26F:'Station.XorRowIfSelected.Entry',0x6A6C:'Station.DrawHelpContents.RenderTitles',0x6A15:'HelpPanelState.ContentsTop',
 0x6396:'Station.SelectRamBank.Entry',0xDB57:'Help.SelectText.Entry',0xA49F:'Station.BeginScreenUpdate.Entry',0x69A8:'Station.DrawHelpText.Entry',
 0x6A5B:'Station.DrawHelpContents.Entry',0xA496:'Station.EndScreenUpdate.Entry'}
MODIFIED_WRITES=((0x6991,0xA265,'Station',0xA264,2,2),(0x6997,0xA235,'Station',0xA234,2,2),(0x69A2,0x699D,'Station',0x699C,2,5),
 (0x6A03,0x6A52,'Station',0x6A51,1,5),(0x6A09,0xA265,'Station',0xA264,2,2),(0x6A0F,0xA235,'Station',0xA234,2,2),
 (0x6A1A,0x6A15,'Station',0x6A14,2,5),(0x6A28,0x699D,'Station',0x699C,2,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
