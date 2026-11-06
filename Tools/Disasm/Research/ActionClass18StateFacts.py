"""Установка состояния 0A перед исходным общим диспетчером."""
FUNCTIONS = {0xF075: ('SetClass18ObjectState', 'Установка состояния 0A у записи класса 12h перед диспетчеризацией')}
LOCAL = {}; LABELS = {}; CONTINUATIONS = {}
RENAMES = {'Action.UnknownF075.Entry': 'Action.SetClass18ObjectState.Entry'}
CONTRACTS = {('Action', 0xF075): (
    ['IX указывает запись FActionRecord, ветвь F7C6 передаёт сюда ClassCode=12h'],
    ['в байт состояния записано 0A, PC получает вход диспетчера F843, SP, регистры и флаги сохранены'],
    ['байт состояния и R'],
    ['три M1 до диспетчера, исполнение целевого обработчика проверяется отдельно'],
)}
COMMENTS = {0xF075: (['Назначение состояния 0A перед общей косвенной передачей.'], None)}


def name_operands(region, address, operation):
    if region == 'Action' and address == 0xF075:
        return operation.replace('IX + #0A', 'IX + @FActionRecord.Unknown0A')
    return operation
