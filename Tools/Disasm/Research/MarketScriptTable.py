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
 b'?X=1:{':'событие 1, покупка корабля по исходной таблице семи записей',
 b'?X=2:{':'событие 2, продажа текущего корабля с отдельной ветвью нулевого k.s',
 b'?X=5:{':'событие 5, последовательные ограничения и покупка одной единицы оснащения',
 b'?X=6:{':'событие 6, продажа одной единицы кодированного количества',
 b'?k<255=y:M02':'отказ покупки при уже имеющемся корабле, текущий индекс не FF',
 b'?K.c>c:M01':'отказ при цене выбранного корабля больше кредитов',
 b'?K.t<j:M03':'отказ при вместимости выбранного корабля меньше пересчитанной загрузки',
 b'?o.s=n:M07':'отказ при нарушении порога одной из тридцати активных строк оснащения',
 b'+K,=c-K.c,=J:K.t,T,M12,^':'выбор корабля, списание цены, запись вместимости, пересчёт и сообщение успеха',
 b'?k<255=n:M09':'отказ продажи при отсутствии текущего корабля',
 b'?k.s=n:M04,=c+k.c,-K,#':'при нулевом k.s сообщение M04, начисление цены текущего корабля и снятие выбора без сброса вместимости',
 b'?c+K.c>65000:m11':'предупреждение проверяет цену выбранной строки K.c, начисление ниже использует текущий корабль k.c',
 b'=c+k.c,-K,=J:0,T,M12,^':'начисление цены текущего корабля, снятие выбора, сброс вместимости, пересчёт и сообщение успеха',
 b'?O=n:M08':'отказ при пороге станции больше характеристики L текущего ключа',
 b'?255-k@M05':'обратное условие через @, сообщение M05 при текущем корабле FF',
 b'?O.s=n:M07':'отказ при совпадении текущего корабля с четырёхбайтовым набором O.s',
 b'?o.n=y:M13':'отказ при активном соседе в диапазонах выбранной группы оснащения',
 b'?o]O.k:M06':'отказ при количестве не меньше предела 127 либо 1 по прежнему bit7',
 b'?O.c>c:M01':'отказ при цене оснащения больше кредитов',
 b'?j+O.v>J:M03':'отказ при сумме текущей загрузки и веса единицы больше вместимости',
 b'=o+1,=c-O.c,T,^':'увеличение кодированного количества, списание цены и пересчёт загрузки',
 b'?o=n:M09':'отказ при нулевом декодированном количестве',
 b'?c+O.c>65000:m11':'предупреждение о сумме больше 65000 без прекращения продажи',
 b'=o-1,=c+O.c,T,^':'уменьшение кодированного количества, начисление цены с насыщением и пересчёт загрузки',
 b'?X=16:{':'событие 16, проверка кредитов относительно размера ключа и плата за стоянку',
 b'?c-L.u=0:=c:0,M14,W':'при кредитах не больше размера ключа обнулить кредиты, поставить M14 и вызвать переход W',
 b'=c-(L.u*5),^':'списание пяти размеров ключа с насыщением нулём без повторной проверки W в этом событии',
 b'?X=17:{':'событие 17, дополнительный пересчёт загрузки после общего начального T',
 b'T,^':'пересчёт загрузки и завершение сценария',
 b'?X=15:{':'событие 15, пороги статуса 48 и 64 определяют начальный штраф и очистку оснащения',
 b'?u<48:^':'завершение начальной проверки без штрафа при статусе меньше 48',
 b'?u<64:M16,=c-50':'для статуса 48..63 сообщение M16 и списание 50, остановка на конце строки',
 b'm15,=c-1000,=u-48':'для статуса от 64 сообщение без остановки, списание 1000 и уменьшение статуса на 48',
 b'=o6:0,=o7:0,=o8:0,=o9:0,=o10:0':'очистка кодированных количеств оснащения с физическими индексами 5..9',
 b'=o3:0,=o4:0,=o32:0,T,^':'очистка индексов 2, 3 и 31, последний пишет 98AD вне первых тридцати строк, затем пересчёт и выход',
 b'}':'закрывающая скобка исходного блока, сама команда не восстанавливает стек блока'}


def extract(source):
    end=source.index(0,START)+1
    return source[START:end],end


def parse(text, origin=ORIGIN):
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
            symbols[key]=origin+len(data)
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
    active,end=extract(source);lines=['                module MarketScript','                ; Документация [исходный сценарий и проверенные события товаров](../../../Docs/OriginalTradeScript.md)','                ; События [кораблей](../../../Docs/ShipTrade.md) и [оснащения](../../../Docs/EquipmentTrade.md)','                ; События [начальной проверки и стоянки](../../../Docs/StationScripts.md)','                ; строки ASCII остаются строками, CP866-пояснения записаны исходными числовыми байтами','                assert $ == #'+format(ORIGIN,'04X')];position=0;first=True
    while position<len(active):
        if active[position]==0:
            lines.append('Terminator:'.ljust(16)+'DB #00');position+=1;continue
        stop=active.index(13,position);payload=active[position:stop];raw=payload+bytes([13]);label='Entry' if first else None;first=False
        section=re.fullmatch(rb'\?X=(\d+):\{',payload)
        if section:label=SECTIONS[int(section[1])]
        note=NOTES.get(payload,NOTES.get(payload.split(b' ',1)[0]))
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
