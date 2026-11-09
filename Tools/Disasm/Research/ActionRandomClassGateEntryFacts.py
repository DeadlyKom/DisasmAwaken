"""Отдельный хвостовой переход F68E к проверке случайного слова."""

TAG = 'ActionRandomClassGateEntry'
TITLE = 'хвостовой вход в случайный допуск класса'
CASES = 65536
LOCATION = 'ACTION банка 0'
KEYS = {}
LOCAL = {}
MUTATIONS = ()
FUNCTIONS = {0xF68E: ('EnterRandomClassGate', 'Хвостовой вход в проверку случайного допуска класса')}
ENDS = {0xF68E: 0xF691}
CONTRACTS = {('Action', 0xF68E): (
    ['HL, DE, BC и AF числовых аргументов не задают, IX текущая FActionRecord',
     'выбран ACTION банка 0, подготовлен Stream0, действует входной договор DispatchClassOnHighRandomWord'],
    ['JP передаёт управление DispatchClassOnHighRandomWord с исходным SP и регистрами, R учитывает один дополнительный M1',
     'при полном исполнении выходы, записи и возврат определяются договором DispatchClassOnHighRandomWord'],
    ['HL, DE, BC, AF, HL\', DE\', BC\', R, Stream0 и стек по DispatchClassOnHighRandomWord',
     'остальные регистры и поля по допущенному обработчику класса'],
    ['три байта следуют после RET обработчика StepIdleObjectOffset, штатный вызывающий путь F68E неизвестен',
     '65536 исполнений до внешнего RET сверены с моделью случайного допуска, включая R и восемь банков RAM'],
)}
COMMENTS = {0xF68E: (['Передача исходного возврата проверке случайного допуска класса.'], None)}


def name_operands(region, address, operation):
    if (region, address) == ('Action', 0xF68E):
        return operation.replace('JP #F69E', 'JP @Action.DispatchClassOnHighRandomWord.Entry')
    return operation
