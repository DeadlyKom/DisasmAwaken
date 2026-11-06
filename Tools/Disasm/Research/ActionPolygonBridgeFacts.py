"""Точные короткие переходники, каждое физическое тело публикуется отдельным исходником."""
SPECS={
 'ActionPolygonSelectRight':(0xD268,0xD26B,'SelectPolygonRightEdge','Передача управления правому обновлению без изменения контекста',
    ['подготовлен контекст UpdatePolygonRightEdge, адрес возврата не требуется'],
    ['все основные, альтернативные и индексные регистры, SP, I/IM/IFF и paging сохранены, R меняется',
     'управление передано UpdatePolygonRightEdge.Entry, память и порты не записываются'],
    ['R, остальной контекст сохраняется'],{0xD268:(['Передача управления правому обновлению без CALL и без дополнительного CPU-возврата.'],None)},
    '#D3AD','@Action.UpdatePolygonRightEdge.Entry'),
 'ActionPolygonWrapLeft':(0xD26B,0xD272,'WrapPolygonLeftEdge','Оборачивание обратного поиска к последней First кольца',
    ['HL содержит страницу 90 и нулевой младший индекс после достижения начала кольца',
     'DE содержит D текущей строки и E первоначальной Second, BC и AF принадлежат обновлению левого ребра',
     'LastIndex содержит последний нечётный индекс, временный контекст уже сохранён UpdatePolygonLeftEdge'],
    ['HL сохраняет H, L=LastIndex, A=LastIndex, F сохраняется',
     "DE, BC, HL', DE', BC', AF', IX, IY, SP, I/IM/IFF и paging сохраняются, R меняется",
     'управление передано UpdatePolygonLeftEdge.ReadNextRow, память и порты не записываются'],
    ['HL, только L, AF, только A, R'],{0xD26B:(['Чтение последнего нечётного индекса и продолжение обратного поиска в той же странице.'],None)},
    '#D27E','@Action.UpdatePolygonLeftEdge.ReadNextRow'),
 'ActionPolygonWrapRight':(0xD3A8,0xD3AD,'WrapPolygonRightEdge','Оборачивание прямого поиска к первой First кольца',
    ['HL содержит страницу 90, прямой поиск достиг последнего нечётного индекса',
     'DE содержит D текущей строки и E первоначальной Second, временный контекст сохранён UpdatePolygonRightEdge'],
    ['HL сохраняет H, L=1, управление передано UpdatePolygonRightEdge.ReadNextRow',
     "DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, I/IM/IFF и paging сохраняются, R меняется",
     'память и порты не записываются'],['HL, только L, R'],
    {0xD3A8:(['Выбор первой First по нечётному индексу 1 без изменения страницы контура.'],None)},
    '#D3BC','@Action.UpdatePolygonRightEdge.ReadNextRow'),
 'ActionPolygonWrapLeftTop':(0xD503,0xD50A,'WrapPolygonLeftTop','Оборачивание поиска левого конца верхней горизонтали',
    ['HL содержит страницу 90, обратный верхний поиск достиг нулевого младшего индекса',
     'AF содержит минимальную First, альтернативный A содержит последний нечётный индекс списка'],
    ['HL сохраняет H, L=(входной альтернативный A+1) AND FF, основной A и альтернативный AF сохраняются',
     'F от INC младшего индекса, входной Carry сохранён, управление передано PreparePolygonFill.ReadLeftTop',
     "DE, BC, HL', DE', BC', IX, IY, SP, I/IM/IFF и paging сохраняются, R меняется, память и порты не записываются"],
    ['HL, только L, AF, только F, R'],
    {0xD503:(['Выбор последнего нечётного индекса из альтернативного A с восстановлением обоих AF.'],None),
     0xD506:(['Расчёт промежуточного индекса LastIndex+1 перед следующим DEC L основного поиска.'],None)},
    '#D547','@Action.PreparePolygonFill.ReadLeftTop'),
 'ActionPolygonWrapRightTop':(0xD50A,0xD50F,'WrapPolygonRightTop','Оборачивание поиска правого конца верхней горизонтали',
    ['HL содержит страницу 90, прямой верхний поиск достиг последнего нечётного индекса',
     'основной AF содержит контекст перед обратным EX AF в PreparePolygonFill.ReadRightTop'],
    ['HL сохраняет H, L=1, управление передано PreparePolygonFill.ReadRightTop',
     "DE, BC, AF, HL', DE', BC', AF', IX, IY, SP, I/IM/IFF и paging сохраняются, R меняется",
     'память и порты не записываются'],['HL, только L, R'],
    {0xD50A:(['Выбор первой First по индексу 1 перед восстановлением минимальной строки через EX AF.'],None)},
    '#D557','@Action.PreparePolygonFill.ReadRightTop'),
 'ActionPolygonReturn':(0xD50F,0xD511,'ReturnPolygonFill','Восстановление сохранённого HL и внешний возврат плоского контура',
    ['SP указывает на ранее сохранённый HL, следующее слово содержит внешний адрес возврата',
     'остальные регистры содержат результат раннего пути PreparePolygonFill'],
    ['HL снят с CPU-стека, SP увеличен на четыре и выполнен RET по следующему слову',
     "DE, BC, AF, HL', DE', BC', AF', IX, IY, I/IM/IFF и paging сохраняются, R меняется",
     'память и порты не записываются'],['HL, SP при снятии двух слов, R'],
    {0xD50F:(['Восстановление HL вызывающего и внешнего возврата без смены временного SP.'],None)},None,None)}


def facts(tag):
    start,end,name,description,inputs,outputs,corrupt,comments,old,new=SPECS[tag]
    def operands(region,address,operation):
        if region=='Action' and address==start:
            if old:operation=operation.replace(old,new)
            operation=operation.replace('(#D3B7)','(@ActionPolygonPreparationState.LastIndex)')
        return operation
    notes=['короткий переходник сохраняет исходные адреса и инструкции, новый адрес возврата не создаётся' if start!=0xD50F else 'возврат снимает два существующих слова, дополнительная память не выделяется',
           'проверены точные регистры кроме R и отсутствие записей RAM, полное игровое исполнение этим не доказывается',
           'R/T, IRQ, сборка и нативный запуск не проверены']
    return dict(FUNCTIONS={start:(name,description)},LOCAL={},CONTRACTS={('Action',start):(inputs,outputs,corrupt,notes)},
        COMMENTS=comments,name_operands=operands,
        UNCLASSIFIED_PREFIX_PATH='Source/Resources/17_ACTION/Unclassified028_Before'+name+'.bin',
        UNCLASSIFIED_SUFFIX_PATH='Source/Resources/17_ACTION/Unclassified028_After'+name+'.bin')
