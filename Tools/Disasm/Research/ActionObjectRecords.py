"""Физические 25 начальных записей и маркер, неизвестные поля остаются явными."""
import re
MODULE='ActionObjectRecords'
PATH='Source/Action/Data/ObjectRecords.asm'
START,END=0x4100,0x4780
NAMES=tuple('Record'+format(i,'02X') for i in range(25))+('EndMarker',)
INSTANCE_NOTES = {
    'ActionObjectRecords.Record18.Unknown2C': 'при IY=A72B ROM читает клавиатурные флаги и ставит бит 5, исходное назначение поля неизвестно',
    'ActionObjectRecords.Record18.Unknown32': 'при IY=A72B ROM читает режим клавиатуры, исходное назначение поля неизвестно',
    'ActionObjectRecords.EndMarker.Unknown2B': 'при IY=A72B и переполнении FRAMES ROM увеличивает байт, исходное назначение поля неизвестно',
}

KNOWN={17:('Unknown11','таймер State07, порог State02/10, происхождение ракеты и уведомления State08, количество подбора класса 13'),
       35:('PickupKind','для класса #13 код подбора, используется как байтовый индекс груза и правила, границы не проверяются'),
       21:('LinkOverride','числовой индекс подстановки LinkedIndex, FF запрещает подстановку, ноль разрешён и возвращает Z'),
       22:('SavedStateCode','код состояния для восстановления в обработчиках хода и ожидания'),
       23:('PhaseMoveTimer','байтовый таймер вызовов обработчиков хода первой фазы'),
       37:('TargetCodeStep','числовой предельный шаг подвода второго и третьего фазовых кодов'),
       0x0D:('Phase0OrLink', 'первая локальная фаза либо байтовый индекс опоры, обработчик выбирает трактовку, создатель ракеты пишет #1A'),
       0x0E:('LocalPhase1', 'вторая локальная фаза, ApplyRecordLocalOffsets добавляет #80 по модулю байта'),
       0x10:('OffsetScaleLow', 'младший байт масштаба смещения, локальный расчёт использует его отдельно как беззнаковый масштаб'),
       0x14:('MissileRepeatDelay', 'счётчик повторного пуска ракеты, знаковая ветвь DEC может оставить прежнее значение'),
       0x13:('EffectReserve', 'текущий запас для проверки эффекта и связанных состояний, 60AE записывает 0A либо 32'),
       0x22:('ReserveCeiling', 'предел восстановления запаса, при обходе сравнивается с ним минус один по модулю байта'),
       0x19:('TimedResumeCode', 'прежний полный StateCode, восстанавливаемый при истечении таймера состояния #10'),
       0x24:('OffsetScaleHigh', 'старший байт масштаба смещения, в состоянии ожидания используется как фазовый счётчик'),
       0x20:('ProximityIndex', 'байтовый индекс записи для проверки близости, резервный поиск класса 8 может заменить индекс'),
       0x21:('ProximityClass', 'требуемый полный класс записи для проверки близости, резервный поиск его не меняет'),
       0x26:('WideTargetIndex', 'индекс строки из трёх 32-разрядных компонент широкой цели, шаг строки 12 байтов'),
       6:('ModelOffset','байтовое смещение таблицы указателей 9E00, ReadObjectHeaderWord читает заголовок выбранной модели'),
       7:('OffsetPhase0','байтовый индекс первой фазовой пары вычислителя смещения'),
       8:('OffsetPhase1','байтовый индекс второй фазовой пары, подготовитель добавляет 128'),
       9:('OffsetPhase2','байтовый индекс третьей фазовой пары вычислителя смещения'),
       10:('StateCode','байтовый код выбора обработчика ObjectStateHandlers, 60AE записывает 08'),
       11:('LinkedIndex','индекс связанной записи, 60AE записывает сюда индекс новой ракеты у цели'),
       12:('LinkFlags','бит 0 задаёт обратную связь E804, бит 1 ракетную атаку, бит 2 ракетное поражение в State08, бит 3 противоракетный выбор порога PS1/PS2, биты 7..4 влияют на ненулевость, отдельные роли неизвестны'),
       15:('Phase2OrTarget','третья локальная фаза, индекс цели или порог счётчика, назначение выбирает обработчик'),
       18:('ClassCode','полный код класса, используется FindRecordByCode, создаваемая ракета получает 11'),
       24:('ReuseByte','FF задаёт однократный пропуск поиска, в отдельных состояниях биты 1..0 задают счётчик, бит 2 запрос детей, бит 4 допуск эффекта')}
INIT_NOTES={6:'60AE записывает 90',7:'60AE обнуляет',8:'60AE обнуляет',9:'60AE обнуляет',10:'60AE записывает 08',
 17:'60AE записывает 01',37:'60AE записывает 02'}


def record_byte_fields(start, end):
    return tuple(
        (KNOWN[i][0], 'db', KNOWN[i][1]) if i in KNOWN else (
            f'Unknown{i:02X}', 'db',
            'игровой смысл ещё неизвестен' + (', ' + INIT_NOTES[i] if i in INIT_NOTES else ''))
        for i in range(start, end)
    )


SCHEMA={
 'FActionWord':(('Low','db','младший байт компоненты, формат little-endian'),('High','db','старший байт слова, специальные коды зависят от владельца поля')),
 'FActionComponents':tuple(('Component'+str(i),'FActionWord','в записи смещение '+('XW','YW','ZW')[i]+' из EQUS, в узле Output'+str(i)+', единицы расстояния не установлены') for i in range(3)),
 'FActionViewPosition':tuple((name,'FActionWord','знаковое слово') for name in ('X','Y','Depth')),
 'FActionRecord': (
     ('Components', 'FActionComponents', 'три исходных слова записи, 60AE записывает результаты TransformVectorTransposed'),
     *record_byte_fields(6, 0x1A),
     ('ViewPosition', 'FActionViewPosition',
      'X, Y и глубина после ComputePatchedVector, старший байт X равен 80 до успешного преобразования'),
     *record_byte_fields(0x20, 0x40),
 )}


def layout(structure):
    result={};offset=0
    for field,kind,note in SCHEMA[structure]:
        result[field]=offset
        if kind=='db':offset+=1
        else:
            size,children=layout(kind)
            result.update({field+'.'+name:offset+value for name,value in children.items()});offset+=size
    return offset,result


def structure_text():
    lines=[]
    for structure,fields in SCHEMA.items():
        lines+=['','                ; Исходная физическая раскладка, неизвестные поля не переименованы по предположению']
        if structure=='FActionComponents':
            lines.append('                ; Контексты слов [объект и снимок очереди](../../Docs/ActionComponentContexts.md)')
        lines.append('                struct '+structure)
        for field,kind,note in fields:
            if field=='LinkFlags':
                lines+=['                ; Разряды 7..0, ? ? ? ? P H R B, маски B=01, R=02, H=04, P=08',
                        '                ; B задаёт обратную ссылку E804, R ракетную атаку, H ракетное поражение в State08, P выбор противоракетного порога',
                        '                ; Ноль сбрасывает четыре известных признака и неизвестные биты, отсутствие живой связи этим не доказывается',
                        '                ; 17 исследованных писателей обнуляют байт либо устанавливают биты 0..3 через SET',
                        '                ; иные косвенные писатели и происхождение старших битов этим локальным доказательством не исключены',
                        '                ; Писатели и ограничения [исходные байты и все значения флагов](../../Docs/ActionLinkFlagWrites.md)']
            op='db #00' if kind=='db' else kind
            lines.append((field.ljust(16)+op).ljust(80)+'; '+note)
        size,_=layout(structure);lines+=['                ends','                assert '+structure+' == #'+format(size,'02X')]
        if structure=='FActionComponents':
            lines += ['                assert FActionComponents.Component'+str(i)+' == #'+format(2*i,'02X') for i in range(3)]
    return '\n'.join(lines)+'\n\n'


def render(source):
    lines=['                module '+MODULE,
        '                ; Документация [начальные записи и известные поля](../../../Docs/ActionObjectRecords.md)',
        '                assert $ == #A100'];symbols={}
    def values(structure,blob,address,prefix,indent):
        offset=0
        for index,(field,kind,note) in enumerate(SCHEMA[structure]):
            key=prefix+'.'+field;symbols[key]=address+offset;comma=',' if index+1<len(SCHEMA[structure]) else ''
            note = INSTANCE_NOTES.get(key, note)
            if kind=='db':
                lines.append((' '*indent+'#'+format(blob[offset],'02X')+comma).ljust(80)+'; '+field+', '+note);offset+=1
            else:
                size,_=layout(kind);lines.append((' '*indent+'{').ljust(80)+'; '+field+', '+note)
                values(kind,blob[offset:offset+size],address+offset,key,indent+4)
                lines.append(' '*indent+'}'+comma);offset+=size
        return offset
    for index,name in enumerate(NAMES):
        start=START+64*index;address=0x6000+start;key=MODULE+'.'+name;symbols[key]=address
        lines+=['                ; -----------------------------------------',
            '                ; '+('Отдельный исходный маркер 8080, не дополнительный рабочий слот' if name=='EndMarker' else 'Исходный слот '+format(index,'02X')+', первый компонент 8000 означает начальную доступность'),
            (name+':').ljust(16)+'FActionRecord {']
        assert values('FActionRecord',source[start:start+64],address,key,20)==64;lines.append('                }')
    lines+=['                assert $ == #A780','                endmodule'];text='\n'.join(lines)+'\n'
    raw,parsed=parse(text);assert raw==source[START:END] and parsed==symbols
    return text,symbols


def parse(text):
    clean=[line.partition(';')[0].strip() for line in text.splitlines()];clean=[line for line in clean if line]
    assert clean.pop(0)=='module '+MODULE and clean.pop(0)=='assert $ == #A100'
    raw=bytearray();symbols={};cursor=0
    def values(structure,address,prefix):
        nonlocal cursor
        offset=0
        for index,(field,kind,note) in enumerate(SCHEMA[structure]):
            key=prefix+'.'+field;symbols[key]=address+offset;comma=',' if index+1<len(SCHEMA[structure]) else ''
            note = INSTANCE_NOTES.get(key, note)
            if kind=='db':
                token=clean[cursor];cursor+=1;assert re.fullmatch(r'#[0-9A-F]{2}'+re.escape(comma),token)
                raw.append(int(token[1:3],16));offset+=1
            else:
                assert clean[cursor]=='{';cursor+=1;offset+=values(kind,address+offset,key)
                assert clean[cursor]=='}'+comma;cursor+=1
        return offset
    for index,name in enumerate(NAMES):
        assert clean[cursor]==(name+':').ljust(16)+'FActionRecord {';cursor+=1
        address=0xA100+64*index;key=MODULE+'.'+name;symbols[key]=address
        assert values('FActionRecord',address,key)==64;assert clean[cursor]=='}';cursor+=1
    assert clean[cursor:]==['assert $ == #A780','endmodule'] and len(raw)==END-START
    return bytes(raw),symbols
