"""Вход EA29, настройка дочернего кода и чтение заголовка."""
FUNCTIONS = {0xEA29: ('PrepareLargeEffect', 'Настройка дочернего кода и чтение заголовка большого эффекта')}
LOCAL = {0xEA34: 'StoreChildMask'}
LABELS = {('Action', 0xEA34): 'StoreChildMask'}
RENAMES = {
    'Action.UnknownEA29.Entry': 'Action.PrepareLargeEffect.Entry',
    'Action.UnknownEA29.PointEA34': 'Action.PrepareLargeEffect.StoreChildMask',
}
CONTINUATIONS = {0xEA29: 0xEA3D}
LOCATION = {0xEA29: 'код ACTION банка 0'}
CONTRACTS = {('Action', 0xEA29): (
    ['IX указывает исходную запись, ClassCode и байтовое смещение модели доступны',
     'страница 4 содержит OBJECT3D, выбор страниц разрешён, SP в общей RAM, IRQ не вмешиваются'],
    ['ChildMask равна #40 для класса 8 и #A0 для остальных',
     'HL получает исходный заголовок из OBJECT3D, IX и SP сохранены',
     'в 7FFD выданы #14 и #10, исполнение продолжается в AllocateLargeEffect'],
    ['HL, AF, R, ChildMask, регистр страницы и временные слова стека'],
    ['проверены все классы и все исходные чётные индексы модели',
     'смысл продолжения и границы проверки его выделения описаны отдельно'],
)}
COMMENTS = {
    0xEA29: (['Проверка класса для выбора ChildMask.'], None),
    0xEA30: ([], 'переход, если класс отличается от 8, оставить #A0'),
    0xEA37: (['Чтение заголовка из страницы OBJECT3D.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address != 0xEA29:
        return operation
    return (operation.replace('IX+#12', 'IX + @FActionRecord.ClassCode')
            .replace('IX+#06', 'IX + @FActionRecord.ModelOffset')
            .replace('(#EAC4)', '(@ActionLargeEffectContinuationState.ChildMask)'))


def qualify_mutations(modified, flow, functions):
    writer = next(f for f in functions if f['region'] == 'Action' and f['address'] == 0xEA29)
    target = next(f for f in functions if f['region'] == 'Action' and f['address'] == 0xEA3D)
    assert not any(item['region'] == 'Action' and item['writer'] == 0xEA34 and item['target'] == 0xEAC4
                   for item in modified)
    modified.append(dict(region='Action', writer=0xEA34, target=0xEAC4, target_instruction=0xEAC3,
                         size=1, target_operation='OR #A0', path=writer['path'], writer_bank=0,
                         target_region='Action', target_bank=0, target_slot=17, target_path=target['path'],
                         writer_source_classified=True, target_source_classified=True))
    modified.sort(key=lambda item: (item['region'], item['writer'], item['target']))
