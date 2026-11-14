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
    [
     'HL, DE, BC и AF числовых аргументов не задают, альтернативный AF учитывается при отказе выделения эффекта',
     'IX указывает исходную FActionRecord, доступны Components, ClassCode, ModelOffset и поля освобождения',
     'страница 4 содержит OBJECT3D, страница 3 содержит VOXAL, указатели моделей и эффектные и игровые списки с конечными маркерами доступны',
     'ROM по фактическому paging доступна, при генерации детей читаются соседние адреса R и R+1, после FF второй адрес 0100',
     'внешний возврат и временные рамки до восьми байтов под SP в общей RAM не перекрывают код, таблицы и изменяемые данные, IRQ и повторный вход исключены',
    ],
    [
     'ChildMask равна 40 для полного класса 8 и A0 для остальных, значение записано до чтения OBJECT3D',
     'по ModelOffset прочитан исходный заголовок OBJECT3D, его старший байт определяет Mode большого эффекта',
     'при наличии слота создан большой эффект с ресурсом C400, State=8 и параметрами 14/14/0280, обход включён и Frames не меньше 16 даже при отказе',
     'для полного класса ниже 16 запрашиваются от двух до пяти игровых детей по R, фактически создаётся столько, сколько найдено слотов до маркера',
     'игровой поиск проверяет High=80 и Low=80 напрямую, ReuseByte не проверяется и не очищается',
     'дети получают Components источника, ModelOffset=B8, StateCode=4, LinkFlags=0, ClassCode=10, EffectReserve=10, MissileRepeatDelay=FF, LinkOverride=FF, SavedStateCode=0',
     'Phase0OrLink и LocalPhase1 получают соседние байты ROM по R и R+1, OffsetScaleLow равен ChildMask OR (отдельный R AND 1F), прочие поля сохраняются',
     'HL=EE4D, курсор AY-канала B обновлён, исходная запись получает Component0=8000 и ReuseByte=FF после создания детей',
     'при классе не меньше 16 DE=0280, BC=0012, A=класс, F от CP класса с 10',
     'при полном выполнении запроса детей DE=IX+6, BC=FFEB, A=0/F=42, при достижении маркера DE=0040, BC=0012 до первого ребёнка либо FFEB после него, A=80/F=42',
     "HL', DE', BC' содержат исходные Components, AF' определяется выделением эффекта либо счётчиком и указателем последнего игрового ребёнка, точный результат задан числовой моделью",
     'IY указывает выбранную запись эффекта либо его маркер, IX, I/IM/IFF сохраняются, SP после внешнего RET равен входному SP+2',
     'четыре OUT выдают 14 и 10 при чтении OBJECT3D, затем 13 и 10 при вызове VOXAL, окончательный paging=10',
     'R включает полное чтение заголовка, выделение эффекта, достигнутую генерацию детей и освобождение, точный числовой счёт проверен композиционными моделями',
    ],
    [
     "HL, DE, BC, AF, HL', DE', BC', AF', IY, R, регистр страницы, записи эффектов и объектов, временная рамка стека",
     'ChildMask, Frames и допуск обхода эффектов, режим и параметры VOXAL, курсор AY-канала B, Component0 и ReuseByte исходной записи',
    ],
    [
     'это вход полного вызова EA29, промежуточный выход в EA3D не снимает внешний возврат',
     'жёсткий порядок исполнения, (0) PrepareLargeEffect.asm, (1) AllocateLargeEffect.asm, комментарий продолжения не добавляет JP',
     'прежние проверки 32768 сочетаний класса и чётного индекса ограничены EA3D, 2304 дополнительных профиля ограничены EA6F',
     'режим эффекта берётся из старшего байта заголовка, IX восстанавливается перед дочерними записями',
     'полная цепь EA29 проверена в 51840 сценариях классов 16..255 и 16384 сценариях классов 0..15, включая все R и разные свободные списки',
     'сверены точные регистры, флаги, R, восемь банков, кратность записей и четыре OUT полного входа, State08 проверен дополнительно до внешнего RET',
     'ROM синтетическая, значения 0000 и 0100 различаются, соседний адрес после образца FF равен 0100, а не 0000',
     'полное произведение входов, аппаратные IRQ, точные T, сборка и нативная игра не доказаны',
     'дополнительно полное тело эффекта достигнуто в 1352 сценариях композиции State0E, новая сборка ради правки заголовка не запускалась',
     'литералы 40, A0, C400, 14, 0280, EE4D, 0012, FFEB и коды страниц шестнадцатеричные, граница класса 16, числа сценариев и глубины рамок десятичные',
    ]
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
