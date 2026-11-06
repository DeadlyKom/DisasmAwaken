"""Хвост после успешной обработки большого эффекта."""
FUNCTIONS = {0xF7BF: ('ResumeAfterRecordEffect', 'Сброс флагов связи и продолжение обхода объектов')}
LOCAL = {}
CONTRACTS = {('Action', 0xF7BF): (
    ['IX указывает исходную запись после PrepareLargeEffect, SP восстановлен'],
    ['LinkFlags получает ноль, управление передано F735 без нового возврата'],
    ['LinkFlags и R, остальные регистры, AF и SP сохраняются'],
    ['семь исходных байтов выполняются непосредственно после CALL PrepareLargeEffect'],
)}
COMMENTS = {0xF7BF: (['Сброс флагов связи освобождённой записи перед продолжением обхода.'], None)}


def name_operands(region, address, operation):
    if region == 'Action' and address == 0xF7BF:
        return operation.replace('IX+#0C', 'IX + @FActionRecord.LinkFlags').replace(
            'JP #F735', 'JP @Action.UpdateObjects.PointF735')
    return operation
