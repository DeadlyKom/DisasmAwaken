"""Восстановление CPU-SP и обход активных Next исходной очереди."""
import re
FUNCTIONS={0xEEF1:('RenderPreviewQueue','Обход связанной очереди, загрузка параметров узла и выбор внутреннего либо отсечённого рисователя'),
 0xEEEE:('RestorePreviewStack','Восстановление CPU-SP из изменяемого операнда и последовательный вход в рисование очереди')}
ENDS={0xEEEE:0xEEF1,0xEEF1:0xEF5E}
CONTINUATIONS={0xEEEE:0xEEF1}
FUNCTION_SCOPES={0xEEEE:'restore_cpu_stack_then_render_queue'}
ORDERED_INCLUDES={'RestorePreviewStack':0,'RenderPreviewQueue':1}
LABELS={('D3D',a):name for a,name in ((0xEEF9,'NextObject'),(0xEF52,'ClippedFaces'),(0xEF55,'ResumeNode'),(0xEF57,'CheckNext'))}
DOCUMENTS={('D3D',a):('PreviewQueueRender','восстановление настоящего SP, десять полей узла, выбор рисователя и неизменность Next') for a in FUNCTIONS}
DATA_WRITES={0xCEFA:(2,'Source/D3D/Data/PreviewDrawState.asm'),0xC21E:(2,'Source/D3D/Data/PreviewObjectAngles.asm'),0xC220:(1,'Source/D3D/Data/PreviewObjectAngles.asm')}
CONTRACTS={('D3D',0xEEEE):(
 ['SP временно принадлежит данным предыдущей фазы, прежнее значение не читается',
  'PreviewQueueBuildState.SavedSP содержит CPU-SP, сохранённый BuildPreviewQueue до смены стека',
  'на восстановленном CPU-стеке доступен настоящий адрес возврата всей фазы'],
 ['SP равен сохранённому слову, управление последовательно переходит к RenderPreviewQueue.Entry',
  "HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, I, IFF и IM сохранены",
  'память не записывается, самостоятельного RET здесь нет'],
 ['SP'],
 ['исходное слово операнда 0000 сохраняется, при реальном входе EC28 оно предварительно заменено настоящим SP',
  'проверены все 65536 слов SP, новая машинная инструкция для продолжения не добавлена']),
 ('D3D',0xEEF1):(
 ['HL имеет сохраняемый младший L только для пустой очереди, DE, BC и AF не задают параметры обхода',
  "HL', DE', BC', AF', IX, IY исходный контекст вложенных матриц, проектора, классификатора и рисователя",
  'PreviewDrawState.Head задаёт ацикличную цепочку на странице C7, индекс 1 конец, индекс 0 допустим',
  'поля каждого FPreviewQueueNode доступны продвижением только L, ModelOffset задаёт допустимую пару указателей модели',
  'параметры исходных помощников, таблицы строк, операнды границ и настоящий CPU-стек подготовлены'],
 ['HL адрес Next последнего обработанного узла, при пустой цепочке H=C7 и L входной',
  'DE и BC, альтернативные и индексные регистры принадлежат последнему исполненному помощнику',
  'AF содержит A=1,F=42 от CP 1 при завершении цепочки',
  'Flags, ModelOffset, три параметра ориентации и четыре изменяемых слова загружены из последнего узла',
  'узлы C7, их Next и Head не изменяются, матрицы, проекции, состояние рисователей и bitmap рабочие',
  'SP после RET равен входному+2, I, IFF и IM сохраняются, банк не переключается'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по помощникам, параметры объекта, матрицы, проекция, коды сторон, bitmap, рабочие операнды и CPU-стек"],
 ['пустая очередь меняет только H и AF, остальные основные, альтернативные и индексные регистры сохраняются',
  'каждый узел безусловно проходит BuildPreviewModelMatrix, ComposePreviewMatrix, ProjectPreviewModelGroups и ClassifyPreviewVertices',
  'нулевой результат классификатора либо общая внешняя сторона пропускают рисование, младшая тетрада выбирает DBE9 либо DD4F',
  'после любого пути адрес Next восстанавливается со стека, следующий узел не вычисляется прибавлением 14',
  '144 цепочки и 816 узлов проверены с реальными помощниками и всеми 11 смещениями моделей',
  'все конечные регистры непустой цепочки, независимый bitmap кадра, IRQ и нативный запуск не доказаны'])}
COMMENTS={
 0xEEEE:(['восстановление настоящего CPU-стека из операнда, записанного началом EC28'],None),
 0xEEF1:(['чтение головы активной очереди и выбор страницы физических узлов'],None),
 0xEEF9:(['-----------------------------------------','Параметры очередного объекта','-----------------------------------------','сохранение адреса Next узла для возврата после рисования'],None),
 0xEEFA:(['переход к паре Flags и ModelOffset, продвижение остаётся внутри страницы C7'],None),
 0xEEFF:(['запись пары флагов и байтового смещения модели в состояние рисования'],None),
 0xEF03:(['чтение первых двух параметров ориентации из полей AngleFirst и AngleSecond'],None),
 0xEF07:(['сохранение первых двух параметров в физическом экземпляре ориентации'],None),
 0xEF0B:(['чтение и сохранение третьего параметра AngleThird'],None),
 0xEF10:(['чтение FirstResult и подготовка изменяемого слова первого результата проектора'],None),
 0xEF18:(['чтение SecondResult и подготовка изменяемого слова второго результата'],None),
 0xEF20:(['чтение ThirdResult и подготовка изменяемого слова третьего результата'],None),
 0xEF28:(['чтение SecondInput для изменяемого операнда второй исходной координаты'],None),
 0xEF30:(['выбор физических Flags и ModelOffset для построения матрицы объекта'],None),
 0xEF33:(['построение исходной матрицы модели по трём параметрам ориентации'],None),
 0xEF36:(['композиция матрицы объекта с матрицей сцены'],None),
 0xEF39:(['проекция физических групп выбранной модели в страницу C6'],None),
 0xEF3C:(['классификация записанных вершин по текущему окну и накопление общего кода'],None),
 0xEF3F:([],'переход, если классификатор вернул Z=1, пропустить рисование объекта'),
 0xEF41:(['сохранение общего кода и проверка общей внешней стороны по дополнению старшей тетрады'],None),
 0xEF45:([],'переход, если дополнение старшей тетрады ненулевое, пропустить объект с общей внешней стороной'),
 0xEF47:(['проверка младшей тетрады общего кода для выбора рисователя'],None),
 0xEF4A:([],'переход, если есть внешние вершины, выбрать полный поток с отсечением'),
 0xEF4C:(['рисование полностью внутренней проекции проходом DD4F'],None),
 0xEF52:(['рисование смешанной проекции проходом DBE9 с отсечением'],None),
 0xEF55:(['-----------------------------------------','Следующий узел и завершение цепочки','-----------------------------------------','восстановление адреса Next и чтение исходной ссылки узла'],None),
 0xEF57:(['проверка точного маркера конца, нулевой индекс остаётся допустимым узлом'],None),
 0xEF59:([],'выход, если прочитанный индекс равен 1, активная цепочка завершена'),
 0xEF5A:(['выбор младшего адреса следующего узла без изменения страницы C7'],None)}
TARGETS={0xCF02:'PreviewDrawState.Value.Head',0xCEFA:'PreviewDrawState.Value.Flags',0xC21E:'PreviewObjectAngles.Value.First',0xC220:'PreviewObjectAngles.Value.Third',
 0xDAF6:'PreviewTransformState.ResultFirst',0xDA38:'PreviewTransformState.ResultSecond',0xDA16:'PreviewTransformState.ResultThird',0xEB8D:'PreviewTransformState.InputSecond',
 0xEF5E:'D3D.BuildPreviewModelMatrix.Entry',0xD54C:'D3D.ComposePreviewMatrix.Entry',0xD896:'D3D.ProjectPreviewModelGroups.Entry',0xDF46:'D3D.ClassifyPreviewVertices.Entry',
 0xDD4F:'D3D.RenderPreviewInsideFaces.Entry',0xDBE9:'D3D.RenderPreviewClippedFaces.Entry'}
TARGETS.update({a:'D3D.RenderPreviewQueue.'+name for (_,a),name in LABELS.items()})


def name_operands(region,address,operation):
 if region!='D3D' or address!=0xEEF1:return operation
 operation=re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)],operation)
 return operation.replace('LD H, #C7','LD H, @PreviewQueueConst.Page').replace('CP #01','CP @PreviewQueueConst.EndMarker').replace('AND #F0','AND @PreviewClipDispatchConst.ComplementMask').replace('AND #0F','AND @PreviewClipDispatchConst.SideMask')
