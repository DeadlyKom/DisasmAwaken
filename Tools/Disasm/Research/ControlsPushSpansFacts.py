"""Доказанные внутренние фазы трёх ещё не завершённых рисователей."""
LABELS = {}
COMMENTS = {}
for start,end in ((0xD717,0xD727),(0xD80F,0xD81F),(0xD901,0xD911)):
    for address in range(start,end):
        LABELS['Controls',address] = 'Push'+str(end-address)
    COMMENTS[start] = (['-----------------------------------------','Динамический хвост, SP направлен в растр и AF содержит два байта рисунка',
        'Каждый вход PushN записывает N пар справа налево, прежний CPU-стек восстанавливается после цепочки',
        'IRQ во время этого участка не входят в доказанный договор','-----------------------------------------'],None)
for resume,down in ((0xD81F,0xD82E),(0xD911,0xD920)):
    LABELS['Controls',resume] = 'ResumeRows'
    LABELS['Controls',down] = 'ResumeDown'
    COMMENTS[resume] = (['чтение Mode после заполнения, нуль выбирает движение вверх, ненулевой байт вниз'],None)
    COMMENTS[resume+3] = (['проверка направления следующей строки по нулевому состоянию Mode'],None)
    COMMENTS[resume+4] = (['восстановление CPU-стека из SavedSP перед настоящим CALL помощника строки'],None)
    COMMENTS[resume+8] = ([], 'переход, если Mode ненулевой, выполнить AdvanceRasterDown через ResumeDown')
    COMMENTS[resume+10] = (['шаг вверх, помощник может завершить весь рисователь через сохранённую рамку'],None)
    COMMENTS[down] = (['шаг вниз с тем же возможным нелокальным завершением рисователя'],None)
for address in (0xD706,0xD7FE,0xD8F0):
    COMMENTS[address] = (['вычисление изменяемого смещения JR как 16-A для выбора A операций PUSH AF',
        'после подготовки AF оба его байта равны IXL, затем SP заменяется адресом правой границы растра'],None)


def name_operands(region,function_address,operation):
    if region=='Controls' and function_address in (0xD633,0xD727,0xD833):
        operation=operation.replace('(#D186)','(@ControlsRasterStepState.SavedSP)')
        operation=operation.replace('(#D18B)','(@ControlsEvenSpanState.Mode)')
    return operation
