"""Физический CP866-поток сценария LANG, читаемый DB без конвертера при сборке."""
import re
PATH='Source/Text/Data/MarketScript.asm'
PREFIX='Source/Resources/05_LANG/BeforeMarketScript.bin'
TAIL='Source/Resources/05_LANG/AfterMarketScript.bin'
START=0xA8F
ORIGIN=0xC000+START
SECTIONS={9:'BuyGoods',10:'SellGoods',11:'SellAllGoods',1:'BuyShip',2:'SellShip',5:'BuyEquipment',6:'SellEquipment',16:'ParkingFee',17:'ParkingCheck',15:'InitialCheck'}
NOTES={
 b'T':'пересчёт исходной байтовой загрузки командой T',
 b'?X=9:{':'проверка события покупки одного товара',
 b'?G=Qn:M09':'исходная проверка остатка с незарегистрированным Q, интерпретатор пропускает строку',
 b'?G.c>c:M01':'отказ покупки при цене больше кредитов',
 b'?G.m>J:M03':'проверка загрузки с добавлением выбранного товара относительно вместимости J',
 b'?g]120:M06':'отказ покупки при полном байте груза не меньше 120',
 b'=g+1,=c-G.c,=G-1,T,^':'прибавление груза, списание цены, уменьшение рынка, пересчёт загрузки и выход',
 b'?X=10:{':'проверка события продажи одной единицы груза',
 b'?g=n:M09':'отказ продажи при нулевом полном байте текущего груза',
 b'?G.s=n:M10,=c-1000,=g-g,T':'незаконная продажа по bit7 рынка, сообщение, штраф до нижней границы ноль и очистка количества груза',
 b'?c+G.c>65000:m11':'предупреждение о сумме, строчная m не прекращает дальнейшую продажу',
 b'=g-1,=c+G.c,=G+1,T,^':'уменьшение груза, начисление цены, прибавление рынка, пересчёт загрузки и выход',
 b'?X=11:{':'проверка события продажи всего текущего груза',
 b'?g*G.c+c>65000:m11':'предупреждение о сумме всего груза без прекращения следующей строки',
 b'=c+(G.c*g),=G+g,=g-g,T,^':'начисление стоимости всего полного байта груза, прибавление рынка и очистка количества',
 b'?X=1:{':'исходный блок приобретения корабля, остальные предметные поля разбираются отдельно',
 b'?X=2:{':'исходный блок продажи корабля, остальные предметные поля разбираются отдельно',
 b'?X=5:{':'исходный блок приобретения оснащения, полный игровой договор остаётся в очереди',
 b'?X=6:{':'исходный блок продажи оснащения, полный игровой договор остаётся в очереди',
 b'?X=16:{':'исходный блок платы за стоянку, нативный переход W этой разметкой не проверяется',
 b'?X=17:{':'исходный отдельный блок пересчёта загрузки',
 b'?X=15:{':'исходный блок начальной проверки, полное назначение полей остаётся в очереди',
 b'}':'закрывающая скобка исходного блока, сама команда не восстанавливает стек блока'}


def extract(source):
    end=source.index(0,START)+1
    return source[START:end],end


def parse(text):
    """Независимое чтение фактически записанных DB, включая строки с запятыми."""
    data=bytearray();symbols={};module=None
    token=re.compile(r'\s*(?:"([^"\r\n]*)"|#([0-9A-Fa-f]{2}))\s*(,|$)')
    for line in text.splitlines():
        code=line.split(';',1)[0]
        if not code.strip():continue
        operation=code[16:].strip()
        if operation.lower().startswith('module '):
            module=operation.split()[1];continue
        if operation.lower()=='endmodule' or operation.lower().startswith('assert '):continue
        label=code[:16].strip()
        if label:
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,14}:',label):raise ValueError('Недопустимая метка потока')
            key=module+'.'+label[:-1]
            if key in symbols:raise ValueError('Повторная метка потока')
            symbols[key]=ORIGIN+len(data)
        if not operation.upper().startswith('DB '):raise ValueError('Неподдержанная директива сценария '+operation)
        arguments=operation[3:];position=0
        while position<len(arguments):
            match=token.match(arguments,position)
            if not match:raise ValueError('Неверные байтовые аргументы '+arguments[position:])
            data+=match[1].encode('ascii') if match[1] is not None else bytes([int(match[2],16)])
            position=match.end()
            if match[3]==',':
                if position==len(arguments):raise ValueError('Пустой последний аргумент')
            elif position!=len(arguments):raise ValueError('Лишние данные после аргумента')
    return bytes(data),symbols


def render(source):
    active,end=extract(source);lines=['                module MarketScript','                ; Документация [исходный сценарий и проверенные события товаров](../../../Docs/OriginalTradeScript.md)','                ; строки ASCII остаются строками, CP866-пояснения записаны исходными числовыми байтами','                assert $ == #'+format(ORIGIN,'04X')];position=0;first=True
    while position<len(active):
        if active[position]==0:
            lines.append('Terminator:'.ljust(16)+'DB #00');position+=1;continue
        stop=active.index(13,position);payload=active[position:stop];raw=payload+bytes([13]);label='Entry' if first else None;first=False
        section=re.fullmatch(rb'\?X=(\d+):\{',payload)
        if section:label=SECTIONS[int(section[1])]
        note=NOTES.get(payload)
        if note:lines.append('                ; '+note)
        elif payload.startswith(b' '):lines.append('                ; исходное пропускаемое пояснение CP866, '+payload.decode('cp866').strip())
        elif payload:lines.append('                ; исходная строка остальных ветвей, предметный договор разбирается отдельно')
        if payload and all(32<=b<127 for b in payload) and not any(b in payload for b in (34,59)):
            lines.append(((label+':').ljust(16) if label else ' '*16)+'DB "'+payload.decode('ascii')+'", #0D')
        else:
            for offset in range(0,len(raw),12):
                prefix=(label+':').ljust(16) if label and offset==0 else ' '*16
                lines.append(prefix+'DB '+', '.join('#'+format(b,'02X') for b in raw[offset:offset+12]))
        position=stop+1
    lines+=['                assert $ == #'+format(0xC000+end,'04X'),'                endmodule']
    text='\n'.join(lines)+'\n';data,symbols=parse(text)
    if data!=active:raise ValueError('Разметка DB не сохранила исходный поток')
    return text,symbols,end
