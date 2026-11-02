"""Сравнение усечённых числовых ключей двух трёхбайтовых компонентов."""
FUNCTIONS = {0xDAB9:('CompareComponents','Сравнение двух компонентов после перехода IY к следующей трёхбайтовой записи')}
LOCAL = {0xDAD9:'AcceptComponent',0xDADC:'RejectComponent'}
LABELS = {('Controls',address):name for address,name in LOCAL.items()}
RENAMES = {'Controls.UnknownDAB9.Entry':'Controls.CompareComponents.Entry',
    'Controls.UnknownDAB9.PointDAD9':'Controls.CompareComponents.AcceptComponent',
    'Controls.UnknownDAB9.PointDADC':'Controls.CompareComponents.RejectComponent'}
CONTINUATIONS = {}
CONTRACTS = {('Controls',0xDAB9):(
    ['HL сохраняется, DE входных аргументов не задаёт, BC сохраняется, AF входных аргументов не задаёт',
     'IX указывает опорный FComponent24, IY указывает предыдущую запись сравниваемой последовательности',
     'банк 1 выбран, после IY+3 доступны поля Middle и High текущего FComponent24, индексы оборачиваются по слову',
     'на CPU-стеке внешний возврат, дополнительный стек не требуется, IRQ не вмешиваются'],
    ['HL сохраняется, DE содержит D=High текущей записи AND HighMask и E=3, BC сохраняется',
     'NZ возвращается при опорном High AND HighMask меньше DirectLimit либо при опорном 15-битовом ключе не меньше текущего',
     'Z возвращается только при опорном High не меньше DirectLimit и меньшем опорном ключе, A=0 и F=44',
     'при прямом допуске A=опорный High OR 01, F от OR, при большем High A=опорный High и F от CP D',
     'при равных High и не меньшем опорном Middle A=опорный Middle OR 01, F от OR',
     "HL', DE', BC', AF', IX, I, IM и IFF сохраняются, IY увеличивается на три, SP=входной SP+2",
     'R получает 14 M1 при прямом допуске, 15 при большем опорном High, 16 при меньшем, 22 при сравнении Middle'],
    ['DE, AF, IY, R'],
    ['ключ равен 256*(High AND HighMask)+Middle, Low и бит 7 High не участвуют в сравнении',
     'бит 7 High здесь только исключён маской, его общий игровой смысл этим помощником не доказывается',
     'IY увеличивается до проверки, а не только при принятом компоненте, записи RAM отсутствуют',
     'векторный вызывающий D95F проверяет до трёх компонентов через CALL NZ, его общий алгоритм ещё не завершён',
     'причина игрового выбора DirectLimit=0A остаётся вне локального договора'])}
COMMENTS = {
    0xDAB9:(['поиск следующей трёхбайтовой записи, исходный IY указывает предыдущую запись последовательности'],None),
    0xDABE:(['чтение старшей части текущего компонента без исключённого разряда 7'],None),
    0xDAC4:(['чтение старшей части опорного компонента с той же числовой маской'],None),
    0xDAC9:(['проверка прямого допуска по малой старшей части опорного компонента'],None),
    0xDACB:([], 'переход, если опорная старшая часть меньше DirectLimit, принять компонент через AcceptComponent'),
    0xDACD:(['проверка порядка старших частей двух усечённых ключей'],None),
    0xDACE:([], 'переход, если опорная старшая часть меньше текущей, отклонить компонент через RejectComponent'),
    0xDAD0:([], 'выход, если опорная старшая часть больше текущей, вернуть NZ и F от CP D'),
    0xDAD1:(['проверка средних байтов только при равных старших частях, младшие байты не читаются'],None),
    0xDAD7:([], 'переход, если опорный Middle меньше текущего Middle, отклонить компонент через RejectComponent'),
    0xDAD9:(['формирование NZ с нечётным ненулевым A без унификации исходных путей возвращаемых F'],None),
    0xDADC:(['формирование отказа A=0, F=44, Z установлен'],None)}


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address==0xDAB9:
        operation=operation.replace('LD DE, #0003','LD DE, @FComponent24')
        operation=operation.replace('AND #7F','AND @ComponentCompareConst.HighMask')
        operation=operation.replace('CP #0A','CP @ComponentCompareConst.DirectLimit')
        for index in ('IX','IY'):
            operation=operation.replace('('+index+' + #02)','('+index+' + @FComponent24.High)')
            operation=operation.replace('('+index+' + #01)','('+index+' + @FComponent24.Middle)')
    return operation
