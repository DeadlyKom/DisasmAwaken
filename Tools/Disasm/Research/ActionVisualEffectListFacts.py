"""Кадровый проход эффектов и продолжение после восстановления стека."""
from ActionVisualEffectResumeFacts import COMMENTS as RESUME_COMMENTS
from ActionVisualEffectResumeFacts import CONTRACTS as RESUME_CONTRACTS


FUNCTIONS = {
    0x6D38: ('UpdateVisualEffects', 'Обход эффектов, продвижение ресурсов и растеризация допущенных записей'),
    0x6DD1: ('ResumeVisualEffect', 'Восстановление стека и банковый вызов рисователя эффекта при положительной глубине'),
}
LOCAL = {0x6D45: 'StoreTime', 0x6D4C: 'SetStride', 0x6D4F: 'NextEffect',
         0x6DB8: 'AdvanceCursor', 0x6DBF: 'StoreCursor'}
LABELS = {('Action', address): name for address, name in LOCAL.items()}
RENAMES = {'Action.Unknown6D38.Entry': 'Action.UpdateVisualEffects.Entry'}
RENAMES.update({f'Action.Unknown6D38.Point{address:04X}': 'Action.UpdateVisualEffects.' + name
                for address, name in LOCAL.items() if address != 0x6D4C})
ADDITIONAL_SYMBOLS = {'Action.UpdateVisualEffects.SetStride': 0x6D4C}
CONTRACTS = {
    ('Action', 0x6D38): (
        ['Enabled и Frames задают разрешение и счётчик, список FVisualEffect завершается отрицательным State',
         'доступны три слова смещения, матрица ACTION и ресурсы VOXAL, банк 0 выбран, IRQ не вмешиваются'],
        ['при выключенном обходе запись и растровый буфер сохраняются',
         'иначе уменьшаются общий счётчик и времена жизни активных записей, обновляются координаты, курсоры и фазы',
         'положительная глубина без переполнения допускает рисователя страницы 3, после него возвращается страница 0',
         'после конечного маркера SP восстанавливается и выполняется внешний RET'],
        ['HL, DE, BC, AF, HL\', DE\', BC\', AF\', IX, IY, R, список, растровый буфер, операнды и рабочий стек'],
        ['сквозная модель проверяет восемь позиций, переходы времени, курсоры, растр и переключения',
         'побочные записи вне списка и буфера и точный полный набор регистров отдельно не сверялись'],
    ),
    ('Action', 0x6DD1): RESUME_CONTRACTS['Action', 0x6DD1],
}
COMMENTS = {**RESUME_COMMENTS,
    0x6D38: (['Проверка разрешения кадрового обхода.'], None),
    0x6D3B: ([], 'выход, если обход выключен'),
    0x6D3C: (['Расчёт оставшегося числа кадров с байтовым оборачиванием.'], None),
    0x6D3F: ([], 'переход, если после уменьшения ещё остались кадры'),
    0x6D41: (['Снятие разрешения на следующий кадр, текущий обход продолжается.'], None),
    0x6D4C: (['Восстановление шага между записями после вызова рисователя.'], None),
    0x6D51: (['Проверка состояния текущей записи.'], None),
    0x6D55: ([], 'выход, если отрицательное состояние отмечает конец списка'),
    0x6D56: ([], 'переход, если запись свободна'),
    0x6D58: (['Уменьшение времени жизни и сдвиг координат с передачей прежних слов в преобразователь.'], None),
    0x6DA7: ([], 'переход, если счётчик ресурса ещё ненулевой, прибавить шаг'),
    0x6DB8: (['Прибавление шага к текущему адресу ресурса по модулю слова.'], None),
    0x6DC6: (['Сохранение настоящего SP перед вычислителем.'], None),
}


def name_operands(region, address, operation):
    if region != 'Action' or address not in FUNCTIONS:
        return operation
    fields = ('SavedHL', 'SavedHL + 1', 'SavedDE', 'SavedDE + 1', 'SavedBC', 'SavedBC + 1',
              'Mode', 'State', 'FramePointer', 'FramePointer + 1', 'FirstFrame', 'FirstFrame + 1',
              'FrameCount', 'FrameReload', 'FrameStride', 'FrameStride + 1', 'FrameWidth', 'FrameHeight')
    for offset, field in enumerate(fields):
        operation = operation.replace(f'IX+#{offset:02X}', 'IX + @FVisualEffect.' + field)
    aliases = {
        '6D39': 'ActionVisualEffectListState.Enabled', '6D3D': 'ActionVisualEffectListState.Frames',
        '6DD2': 'ActionVisualEffectListState.SavedSP',
        'AF48': 'ActionPatchedVectorState.Input0', 'AF56': 'ActionPatchedVectorState.Input1',
        'AF69': 'ActionPatchedVectorState.Input2', 'D9B6': 'ActionPatchedVectorState.Output0',
        'D7C4': 'ActionPatchedVectorState.Output1', 'D7A2': 'ActionPatchedVectorState.Output2',
        'E5B3': 'ActionScaledVectorState.Component0', 'E5D2': 'ActionScaledVectorState.Component1',
        'E5ED': 'ActionScaledVectorState.Component2',
    }
    for operand, alias in aliases.items():
        operation = operation.replace(f'(#{operand})', f'(@{alias})')
    return (operation.replace('LD IX, #A783', 'LD IX, @ActionBankedCallbackState.ContextBase')
            .replace('LD DE, #0012', 'LD DE, FVisualEffect')
            .replace('LD IY, #6DD1', 'LD IY, @Action.ResumeVisualEffect.Entry'))
