"""Панель документации оснащения, исходный LF-текст, пагинация и действие."""
import re
FUNCTIONS={0x6A83:('HandleEquipmentInfoHover','Пустая JP-обёртка наведения документации оснащения'),
 0x6A86:('HandleEquipmentInfoAction','Закрытие либо прокрутка документации оснащения, выбор единицей пустой'),
 0x6AAE:('IgnoreEquipmentInfoHover','Пустое наведение документации оснащения с немедленным RET'),
 0x6AAF:('TryDrawEquipmentInfo','Условное рисование документации только при точном указателе в списке'),
 0x6AB6:('DrawEquipmentInfo','Рамка документации оснащения, поиск и подсчёт LF-текста, печать от TopRow'),
 0x6AC6:('UpdateEquipmentInfo','Поиск LF-описания оснащения, сохранение его начала и полного числа визуальных строк'),
 0x6ADE:('PrintEquipmentInfo','Печать сохранённого описания оснащения с байтовым числом пропускаемых строк')}
RENAMES={'HandleItem39':'HandleEquipmentInfoHover','Unknown6A86':'HandleEquipmentInfoAction','Unknown6AAE':'IgnoreEquipmentInfoHover',
 'Unknown6AAF':'TryDrawEquipmentInfo','DrawItem39':'DrawEquipmentInfo','Unknown6AC6':'UpdateEquipmentInfo','Unknown6ADE':'PrintEquipmentInfo'}
LABELS={('Station',0x6AAD):'NoSelection'}
LABEL_RENAMES={'HandleEquipmentInfoAction.Point6AAD':'HandleEquipmentInfoAction.NoSelection'}
CONTINUATIONS={0x6AAF:0x6AB6}
DOCUMENTS={('Station',a):('EquipmentInfo','LF-описание, сохранённый указатель, полный счётчик и байтовый пропуск') for a in FUNCTIONS}
NOOP=(['нет параметров, обычный CPU-возврат доступен'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",'память, список, окно и страницы не меняются'],
 ['нет, кроме обычного потребления CPU-возврата'],['JP-обёртка наведения не создаёт нового кадра CALL'])
CONTRACTS={('Station',0x6A83):NOOP,('Station',0x6AAE):NOOP,
 ('Station',0x6AC6):(
 ['BC содержит сохраняемый для поиска контекст, A и HL входа параметрами не являются',
  'EquipmentInfoState.TextIndex содержит байтовый номер LF-записи от D1BA, выбран банк станции 0',
  'существуют TextIndex+1 LF и читаемый запас выбранного текста, окно и шрифт подготовлены',
  'каждый сухой проход CountTextRows продвигает текст либо возвращает Carry, стек и изменяемые операнды доступны'],
 ['HL указывает на результат последнего сухого прохода, DE содержит число проходов по модулю 65536, включая последний',
  'BC и AF принадлежат последнему SkipJustifyRow, Carry установлен',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
  'Style=1, SourcePointer содержит начало выбранной записи, LineCount равен полному DE',
  'CursorX обнулён перед счётом, CursorY=8 задаётся перед каждым проходом, bitmap не меняется'],
 ['HL, DE, BC, AF, Style, SourcePointer, LineCount, курсор и изменяемые операнды сухого прохода'],
 ['номер записи не ограничивается каталогом, FF пропускает 256 LF, существование записи не проверяется',
  'буфер указателей не создаётся, SourcePointer является словом внутри LD HL печатателя',
  'при Height<14 получается один проход без потребления текста, исходная возможность непродвижения сохранена']),
 ('Station',0x6ADE):(
 ['HL содержит полное слово TopRow, для пропуска используется только его младший байт',
  'SourcePointer подготовлен UpdateEquipmentInfo, текст, окно, глифы и стек удовлетворяют PrintFromRow'],
 ['перед PrintFromRow DE равен входному HL, HL равен SourcePointer, BC=0800',
  'HL, DE, BC и AF являются результатом PrintFromRow, ранний Carry сохраняет D и остаток E согласно его договору',
  "HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены, SP после RET равен входному+2",
  'начальный курсор X=0, Y=8, затем курсор и bitmap содержат фактически выполненный вывод'],
 ['HL, DE, BC, AF, курсор, bitmap и изменяемые операнды PrintFromRow и глифов'],
 ['TopRow=256 пропускает ноль строк, TopRow=257 одну, старший байт лишь передаётся в D',
  'обёртка не ограничивает вход по LineCount и не переключает страницы, недопустимость конечного потока обеспечивает вызывающий код']),
 ('Station',0x6AB6):(
 ['ItemIndex является существующим операндом индекса FInterfaceItem, штатно 39, либо Entry временно содержит C9',
  'для обычного Entry действуют договоры DrawCaptionItem, UpdateEquipmentInfo и PrintEquipmentInfo',
  'TopRow подготовлен, банк станции 0 выбран, IRQ корректно пробуждает рамку и сохраняет контекст'],
 ['при исходном LD HL нарисована рамка и заголовок, SourcePointer и LineCount обновлены, печать использует TopRow',
  'HL, DE, BC и AF принадлежат PrintEquipmentInfo, альтернативные и индексные регистры сохранены кроме рабочего AF\' рамки',
  'Style=1, TopRow не меняется, геометрия, курсор и bitmap принадлежат рамке и печати',
  'страница не переключается самим рисователем, I, IFF и IM сохраняются при договоре IRQ, SP после RET входному+2',
  'при временном C9 сохраняются регистры, флаги и память, SP после RET входному+2'],
 ["HL, DE, BC, AF, AF', окно, курсор, bitmap, SourcePointer, LineCount и изменяемые операнды помощников"],
 ['неудача вывода заголовка не прерывает последующий подсчёт и печать описания',
  'полнота всех записей каталога и всех писателей TextIndex этим локальным контрактом не утверждается']),
 ('Station',0x6AAF):(
 ['HL и BC сохраняемый контекст TestDrawPointer, текущий список имеет исходный ограничитель',
  'для найденного исходного рисователя выполняется договор DrawEquipmentInfo'],
 ['при отсутствии точного указателя HL и BC сохранены, DE=DrawEquipmentInfo.Entry, AF принадлежит TestDrawPointer',
  'при совпадении и временном C9 в рисователе HL и BC сохранены, DE=6AB6, AF=0050',
  'при совпадении исходного рисователя выполняется весь DrawEquipmentInfo с его результатом',
  'SP после обычного возврата входному+2, альтернативные и индексные регистры согласно выбранной ветви'],
 ["DE, AF, остальные регистры и память только по реально вызванному DrawEquipmentInfo"],
 ['проверяется точный адрес 6AB6, чужой рисователь с тем же индексом 39 не считается совпадением',
  'Z=1 после TestDrawPointer оставляет последовательное исполнение следующего файла, порядок include жёсткий']),
 ('Station',0x6A86):(
 ['HL, DE, BC, AF и IX удовлетворяют RepaintAndFlag и CloseMenuOnRow',
  'для прокрутки выполняются договоры UpdateEquipmentInfo, PrintEquipmentInfo и ScrollWindowRows',
  'TopRow допустим для списка строк, окно безопасно для очистки, ввод и IRQ удовлетворяют прокрутке'],
 ['при Carry RepaintAndFlag немедленно возвращается его контекст, включая обязательный Carry после настоящего рисования',
  'при Carry=0 и его A=1 выполняется пустая ветвь после DEC A с основным AF=0042',
  'при совпадении символьных строк CloseMenuOnRow удаляет только текущий ключ, после его Z=1 выполняется RET',
  'иначе UpdateEquipmentInfo заново ищет запись и считает строки, RenderCall=PrintEquipmentInfo, EndLimit=LineCount',
  'ScrollWindowRows получает A=8 и HL=TopRow, полный результат HL сохраняется в TopRow',
  'выходные регистры прокрутки соответствуют её договору, обычный выход даёт DE исходного PointerXY, AF=0044 и страницу 10',
  'SP после обычного возврата входному+2, альтернативные и индексные регистры согласно фактически исполненным помощникам'],
 ["HL, DE, BC, AF, AF', BC' по прокрутке, список, экраны, указатель, окно, SourcePointer, LineCount, TopRow и операнды"],
 ['в отличие от справки действие не удаляет связанные панели оснащения, закрывается только документация',
  'верхний индекс хранится словом, но callback использует его младший байт для числа пропусков',
  'исходные ранние выходы, байтовые переполнения и ограничения геометрии не исправлены'])}
COMMENTS={
 0x6A83:(['передача наведения в пустой обработчик без нового CPU-возврата'],None),
 0x6A86:(['перерисовка и обработка геометрии до действия документации'],None),
 0x6A89:([],'выход, если RepaintAndFlag вернул Carry, дальнейшее действие подавлено'),
 0x6A8A:(['проверка селектора 1, выбор в документации не выполняется'],None),
 0x6A8B:([],'переход, если возвращённый селектор равен 1, завершить без выбора'),
 0x6A8E:(['условное закрытие текущей панели по совпадению символьных строк Y'],None),
 0x6A91:([],'выход, если CloseMenuOnRow совпал со строкой и выполнил удаление'),
 0x6A92:(['обновление начала текущего LF-описания и его числа визуальных строк'],None),
 0x6A95:(['обновление callback прокрутки на печать сохранённого описания'],None),
 0x6A9B:(['чтение полного предела строк из операнда LineCount'],None),
 0x6AA1:(['подготовка отступа 8 и сохранённого слова TopRow'],None),
 0x6AA9:(['сохранение полного итогового индекса прокрутки'],None),
 0x6AAD:(['пустая ветвь выбора документации'],None),
 0x6AAE:(['пустое наведение, подсветка строк документации не рисуется'],None),
 0x6AAF:(['поиск точного указателя рисователя в текущем списке'],None),
 0x6AB5:([],'выход, если точный указатель рисователя отсутствует в списке'),
 0x6AB6:(['чтение изменяемого индекса документации оснащения'],None),
 0x6AB9:(['рисование рамки и заголовка с подготовкой геометрии содержимого'],None),
 0x6ABC:(['повторный поиск и подсчёт выбранного описания'],None),
 0x6ABF:(['чтение полного слова верхней строки перед байтовым пропуском'],None),
 0x6AC2:(['печать сохранённого описания с исходным TopRow'],None),
 0x6AC6:(['обновление политики печати, ненулевой Style разрешает перенос'],None),
 0x6ACB:(['поиск TextIndex плюс одного LF от исходного блока документации'],None),
 0x6AD3:(['обновление слова начала текста непосредственно в LD HL печатателя'],None),
 0x6AD6:(['подсчёт сухих визуальных строк без изменения bitmap'],None),
 0x6AD9:(['обновление полного числа строк в операнде действия панели'],None),
 0x6ADE:(['передача полного TopRow в DE, только E задаёт число пропусков'],None),
 0x6ADF:(['чтение сохранённого начала выбранного LF-описания'],None),
 0x6AE2:(['подготовка начального курсора X=0, Y=8'],None),
 0x6AE5:(['пропуск E сухих строк и последующая выровненная печать'],None)}
TARGETS={0x6AAE:'Station.IgnoreEquipmentInfoHover.Entry',0xCBEB:'Station.RepaintAndFlag.Entry',0x6AAD:'Station.HandleEquipmentInfoAction.NoSelection',
 0xC85E:'Station.CloseMenuOnRow.Entry',0x6AC6:'Station.UpdateEquipmentInfo.Entry',0x6ADE:'Station.PrintEquipmentInfo.Entry',0x6AA4:'EquipmentInfoState.TopRow',
 0xA1D6:'Station.ScrollWindowRows.Entry',0x6AB6:'Station.DrawEquipmentInfo.Entry',0xCB64:'Station.TestDrawPointer.Entry',0xC287:'Station.DrawCaptionItem.Entry',
 0xBD26:'TextWindow.Style',0xD1BA:'EquipmentInfoConst.TextBase',0xA390:'Station.SkipLfRecords.Entry',0x6AE0:'EquipmentInfoState.SourcePointer',
 0xA82D:'Station.CountTextRows.Entry',0x6A9C:'EquipmentInfoState.LineCount',0xA843:'Station.PrintFromRow.Entry'}
MODIFIED_WRITES=((0x6A98,0xA265,'Station',0xA264,2,2),(0x6A9E,0xA235,'Station',0xA234,2,2),(0x6AA9,0x6AA4,'Station',0x6AA3,2,5),
 (0x6AC8,0xBD26,'Station',0xBD25,1,2),(0x6AD3,0x6AE0,'Station',0x6ADF,2,5),(0x6AD9,0x6A9C,'Station',0x6A9B,2,5))


def name_operands(region,address,operation):
 if region!='Station' or address not in FUNCTIONS:return operation
 for old,new in RENAMES.items():operation=operation.replace('@Station.'+old+'.','@Station.'+new+'.')
 for old,new in LABEL_RENAMES.items():operation=operation.replace('@Station.'+old,'@Station.'+new)
 return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
