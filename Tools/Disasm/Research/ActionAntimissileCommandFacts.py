"""Противоракетная команда из физического указателя клавиатуры 722E."""
TAG='ActionAntimissileCommand'
TITLE='поиск ракеты противоракетной командой и общий вход вывода'
CASES=197716
FUNCTIONS={0x722E:('ActivateAntimissileSystem','Поиск первой ракеты класса 11 с целью 1A, установка признаков противоракетной обработки и вывод сегмента')}
ENDS={0x722E:0x72BE}
KEYS={0x722E:0x14}
LOCAL={0x724F:'CheckEndMarker',0x7255:'NextRecord',0x72BB:'RestoreIndex'}
MUTATIONS=((0x7235,0xA85F,1,0xA85E,'Source/Action/UpdateFrame.asm'),
 (0x7243,0xECA9,2,0xECA8,'Source/Action/UpdateAyEffects.asm'),
 (0x729B,0xD9B6,2,0xD9B5,'Source/Action/ProjectRenderVertex.asm'),
 (0x729F,0xAF48,2,0xAF47,'Source/Action/ComputePatchedVector.asm'),
 (0x72A3,0xAF56,2,0xAF55,'Source/Action/ComputePatchedVector.asm'),
 (0x72A7,0xAF69,2,0xAF68,'Source/Action/ComputePatchedVector.asm'),
 (0x72AE,0xD7C4,2,0xD7C3,'Source/Action/ProjectRenderVertex.asm'),
 (0x72B4,0xD7A2,2,0xD7A1,'Source/Action/ProjectRenderVertex.asm'))
CONTRACTS={('Action',0x722E):(
 ['HL, DE, BC и AF числовых аргументов не задают, ненулевая CommandDelay запрещает команду',
  'список начинается по A100, шаг 40, свободная запись имеет High=80, конечный маркер имеет Low=High=80',
  'до маркера доступны ClassCode, TargetIndex, LinkFlags и ViewPosition',
  'банк 0 выбран, Controls банка 1 содержит очередь, действуют договоры QueueTextItemBank1 и CheckAndToggleLinkedOverlay.CheckDepthSigns',
  'проекционные таблицы и экран подготовлены, изменяемые операнды доступны для записи, paging разблокирован',
  'обычный стек допускает тридцать два дополнительных байта и не пересекает рабочие области детей, IRQ и повторный вход исключены'],
 ['при ненулевой задержке HL, DE и BC сохраняются, A равен задержке, F соответствует AND A, RAM и paging сохраняются',
  'иначе задержка получает 5, сообщение F32D передаётся до поиска, CursorA получает EDC1 независимо от наличия ракеты',
  'выбирается первая активная запись ClassCode=11 и TargetIndex=1A, StateCode не проверяется',
  'при достижении маркера HL указывает его Low, DE=0040, A=80, F=42, BC содержит пару TargetIndex:ClassCode последней просмотренной активной записи либо исходную BC',
  'у выбранной записи LinkFlags получает старое значение OR 09 до проверок её векторного контекста',
  'при ViewPosition.X.High=80 HL указывает выбранную запись, DE=0040, BC=1A11, A=80, F=41, альтернативные регистры сохраняются',
  'иначе три слова выбранной записи переходят в альтернативные BC, HL и DE, главные BC=0003, HL=00B0, DE=FFFF',
  'Output0 и Input0..Input2 получают 0003, Output1 получает 00B0, Output2 получает FFFF, исходные операнды не восстанавливаются',
  'после CALL внутреннего CheckDepthSigns действуют его проверки знаков, signed overflow и полный договор проекции, клиппинга и XOR-сегмента',
  'IX восстанавливается на всех возвращающихся путях, SP после внешнего RET равен исходному SP+2, I, IM и IFF сохраняются',
  'при нулевой задержке OUT 7FFD получает 11,10, итоговый paging равен 10, отказ очереди не отменяет поиск и изменения записи'],
 ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IY по договору сегмента, R, задержка, CursorA, LinkFlags, шесть изменяемых слов, очередь, экран и буферы детей, paging и CPU-стек по пути'],
 ['оборудование PS1 и PS2 здесь не проверяется, бит 3 LinkFlags впоследствии выбирает их порог в CheckRecordEffectThreshold',
  'ветвь ViewPosition.X.High=80 сохраняет уже установленные биты 0 и 3, отрицательная глубина и отказ проекции также их не отменяют',
  'внутренний вход E835 пропускает поиск связанной записи и случайное создание обратной связи полной процедуры E804',
  '197716 сценариев исполняют исходный обработчик, настоящую очередь, внутренний вход, проекцию и растеризатор',
  'сверены регистры кроме R и тактов, все банки RAM и кратность записей вне тридцати двух временных байтов обычного стека',
  'полное совместное произведение входов, IRQ, сборка и нативная игра не проверялись'])}
COMMENTS={
 0x722E:(['Проверка задержки перед повторной противоракетной командой.'],None),
 0x7232:([],'выход, если CommandDelay ненулевой, сохранить состояние'),
 0x7233:(['Обновление задержки и постановка сообщения до поиска подходящей ракеты.'],None),
 0x7240:(['Выбор звукового потока независимо от результата поиска.'],None),
 0x7246:(['Подготовка адреса перед первой записью, NextRecord добавит размер FActionRecord.'],None),
 0x724F:(['Проверка младшего байта свободной записи, пара 8080 завершает список.'],None),
 0x7253:([],'выход, если Low свободной записи равен 80, ракета не найдена'),
 0x7255:(['Поиск следующей записи, активность определяется только High первой компоненты.'],None),
 0x7259:([],'переход, если High равен 80, проверить конечный маркер'),
 0x725B:(['Чтение ClassCode и TargetIndex исходными операциями над младшим байтом адреса.'],None),
 0x7267:(['Проверка класса ракеты, код состояния записи здесь не ограничивается.'],None),
 0x726A:([],'переход, если ClassCode не равен 11, продолжить поиск'),
 0x726C:(['Проверка цели ракеты, только код 1A выбирается противоракетной командой.'],None),
 0x726F:([],'переход, если TargetIndex не равен 1A, продолжить поиск'),
 0x7271:(['Сохранение вызывающего IX и выбор найденной физической FActionRecord.'],None),
 0x7277:(['Обновление признаков обратной связи и противоракетного выбора порога до всех векторных отказов.'],None),
 0x727F:(['Проверка маркера векторного контекста выбранной записи.'],None),
 0x7285:([],'переход, если ViewPosition.X.High равен 80, восстановить IX без отмены LinkFlags'),
 0x7287:(['Подготовка трёх слов выбранной записи и сохранение их в альтернативном наборе.'],None),
 0x7298:(['Обновление исходных изменяемых операндов, фиксированный второй контекст имеет BC=3, HL=176 и DE=-1.'],None),
 0x72B8:(['Вызов внутреннего входа проверки двух контекстов, поиск связи и случайная обратная ссылка E804 пропускаются.'],None),
 0x72BB:(['Восстановление IX на обоих путях после установки LinkFlags.'],None)}


def name_operands(region,function_address,operation):
    if region!='Action' or function_address!=0x722E:return operation
    replacements={'(#A85F)':'(@ActionMissileLaunchState.CommandDelay)',
      '(#ECA9)':'(@ActionAyEffectState.CursorA)',
      '#EDC1':'@ActionAyStreams.AntimissRow00',
      'CALL #6040':'CALL @Action.QueueTextItemBank1.Entry',
      'CALL #E835':'CALL @Action.CheckAndToggleLinkedOverlay.CheckDepthSigns',
      'LD DE, #0040':'LD DE, @FActionRecord'}
    for address,name in ((0xD9B6,'Output0'),(0xAF48,'Input0'),(0xAF56,'Input1'),(0xAF69,'Input2'),(0xD7C4,'Output1'),(0xD7A2,'Output2')):
        replacements['(#'+format(address,'04X')+')']='(@ActionPatchedVectorState.'+name+')'
    for offset,field in ((12,'LinkFlags'),(26,'ViewPosition.X.Low'),(27,'ViewPosition.X.High'),(28,'ViewPosition.Y.Low'),(29,'ViewPosition.Y.High'),(30,'ViewPosition.Depth.Low'),(31,'ViewPosition.Depth.High')):
        replacements['(IX + #'+format(offset,'02X')+')']='(IX + @FActionRecord.'+field+')'
        replacements['(IX+#'+format(offset,'02X')+')']='(IX + @FActionRecord.'+field+')'
    for address,name in LOCAL.items():replacements['#'+format(address,'04X')]='@Action.ActivateAntimissileSystem.'+name
    for before,after in replacements.items():operation=operation.replace(before,after)
    return operation


def prepare(pending,symbols,root):
    old='бит 0 задаёт обратную связь E804, бит 1 установленную связь создателя или State08, бит 2 ближнюю область State08, биты 7..3 неизвестны'
    new='бит 0 задаёт обратную связь E804, бит 1 установленную связь, бит 2 ближнюю область State08, бит 3 противоракетный выбор порога PS1/PS2, биты 7..4 неизвестны'
    for relative in ('Includes/Structs/Include.inc','Source/Action/Data/ObjectRecords.asm','Tools/Disasm/Research/ActionObjectRecords.py'):
        path=root/relative;text=path.read_text('utf-8');assert old in text
        text=text.replace(old,new).replace('? ? ? ? ? A L B, маски B=01, L=02, A=04','? ? ? ? P A L B, маски B=01, L=02, A=04, P=08')
        text=text.replace('Ноль сбрасывает три известных признака и неизвестные биты','Ноль сбрасывает четыре известных признака и неизвестные биты')
        pending[path]=text.encode('utf-8')
    path=root/'Docs/ActionObjectRecords.md';text=path.read_text('utf-8')
    text=text.replace('`? ? ? ? ? A L B`','`? ? ? ? P A L B`').replace('разрядов 7..3 не выдумывается','разрядов 7..4 не выдумывается')
    text=text.replace('три известных признака и пять неизвестных разрядов','четыре известных признака и четыре неизвестных разряда')
    text+='\nБит 3 `P`, маска `08`, устанавливает [ActivateAntimissileSystem](../Source/Action/ActivateAntimissileSystem.asm) у первой ракеты класса `11` с целью `1A`. В [CheckRecordEffectThreshold](../Source/Action/CheckRecordEffectThreshold.asm) этот бит выбирает пороги по PS1/PS2 для связи `1A`. Нулевой бит оставляет Link1ABaseLimit. Отказ векторного вывода бит не отменяет. [Договор команды](ActionAntimissileCommand.md).\n'
    pending[path]=text.encode('utf-8')
    path=root/'Source/Action/CheckAndToggleLinkedOverlay.asm';text=path.read_text('utf-8')
    needle='CheckDepthSigns:LD A, D';assert text.count(needle)==1
    block=['Внутренний вход CheckDepthSigns, самостоятельный CALL из ActivateAntimissileSystem.',
      'Документация [противоракетный вызов](../../Docs/ActionAntimissileCommand.md).',
      'In:',
      "  HL, DE, BC задают первый выбранный контекст, HL', DE', BC' второй, AF числового аргумента не задаёт",
      '  Output0, Output1 и Output2 подготовлены, действуют договоры ToggleTargetOverlay и его детей',
      '  IX сохраняется, IY и альтернативные регистры определяются достигнутым путём, требуется стек дочернего вывода',
      'Out:',
      '  EXX выполняется на каждом пути, оба отрицательных DE дают A=AND старших байтов, F от AND A и Carry=0',
      '  иначе сохраняются рабочие векторы до трёх проверок Output0-BC, Output2-DE и HL-Output1',
      '  при signed overflow F соответствует SBC с последующим SCF, Carry=1, очередная разность не сохраняется в HL',
      '  при трёх допусках действует ToggleTargetOverlay, затем IX восстанавливается и AND A сбрасывает Carry',
      '  SP после RET равен входному SP+2, поиск связи, чтение R и создание обратной ссылки пропускаются',
      'Corrupt:',
      "  HL, DE, BC, AF, HL', DE', BC', AF', IY, R, экран, буферы и CPU-стек по договору дочернего вывода"]
    text=text.replace(needle,'\n'.join('                ; '+line for line in block)+'\n'+needle)
    pending[path]=text.encode('utf-8')
    path=root/'Tools/Disasm/Research/ActionLinkedOverlayFacts.py';text=path.read_text('utf-8')
    text+='\n# Сохранение договора самостоятельного внутреннего входа при отдельном экспорте кандидата.\n'
    text+='COMMENTS[0xE835]=('+repr([COMMENTS.get(0xE835,(['Проверка совместного знака двух глубин.'],None))[0][0]]+block)+',None)\n'
    pending[path]=text.encode('utf-8')
