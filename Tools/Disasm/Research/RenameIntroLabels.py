"""Смысловые имена циклов вступления по проверенным исходным алгоритмам."""
import contextlib
import io
import json
import re
import sys

from CheckIntro import ROOT
sys.path.insert(0, str(ROOT / 'Tools/Disasm'))
from VerifySources import main as verify


LABELS = {
    'InitializeIntro': {'Point65B0': ('EnterStation', 'передача перенесённому загрузчику станции')},
    'BuildAlternatingTexture': {
        'Point6645': ('BeginRow', 'начало 256-байтовой строки'),
        'Point6647': ('ConvertPair', 'деление чётного байта и копирование нечётного')},
    'ExpandTextureRows': {
        'Point6733': ('BeginRow', 'начало очередной 64-байтовой строки'),
        'Point6737': ('AddTextureBias', 'добавление IXL к очередному байту'),
        'Point6747': ('RepeatRow', 'повторение образца до длины страницы')},
    'BuildTextureLookup': {
        'Point6784': ('NextParameter', 'чтение следующего из 63 параметров'),
        'Point67A4': ('Accumulate', 'накопление 128 координат с шагом DE'),
        'Point67B4': ('StoreLookup', 'адресация и запись пары индекс и IYL'),
        'Point67D6': ('BeginGapPass', 'начало одного из двух проходов заполнения'),
        'Point67D9': ('CheckGap', 'проверка второго байта очередной пары'),
        'Point67E7': ('NextPair', 'продолжение после исходной либо восстановленной пары')},
    'BuildAttributeWriter': {
        'Point6935': ('WriterRow', 'начало одной из восьми строк писателя'),
        'Point6939': ('WriterWord', 'генерация POP HL и LD (nn),HL')},
    'CombineAttributeNibbles': {
        'Point6967': ('AttributeRow', 'выбор младшей тетрады строки'),
        'Point6971': ('AttributeCell', 'объединение тетрады строки и тетрады столбца')},
    'BuildScreenTables': {
        'Point69BC': ('MirrorIndex', 'отражение исходной половины координат'),
        'Point69CA': ('FirstTableRow', 'два экранных указателя первой таблицы'),
        'Point69E3': ('CountFirstRow', 'счётчик после коррекции экранного адреса'),
        'Point69ED': ('SecondTableRow', 'указатели второй таблицы со сдвигом H на два')},
    'RepeatPattern': {'Point6A21': ('CopyPattern', 'перенос очередной копии образца')},
    'RunTimedEffect': {'Point6A4E': ('CheckSpace', 'проверка Space перед очередным кадром')},
    'FillBitmap': {
        'Point6A6C': ('FillScanline', 'заполнение 32 байтов экранной строки'),
        'Point6ABE': ('CountScanline', 'счётчик после расчёта следующей строки')},
    'InitializeColumnEffect': {
        'Point6ADD': ('ColumnTable', 'начало одной из 16 таблиц столбцов'),
        'Point6AE3': ('CheckUpper', 'проверка верхнего ограничения страницы E8'),
        'Point6AE9': ('CheckLower', 'проверка нижнего ограничения страницы D8'),
        'Point6AEE': ('StoreColumn', 'сохранение допустимой страницы либо нуля'),
        'Point6B05': ('CopyTail', 'перенос 32-байтового табличного хвоста'),
        'Point6B28': ('TextureRow', 'начало страницы преобразуемой текстуры'),
        'Point6B2A': ('SumSquare', 'сумма соседних пикселей квадрата 2 на 2')},
    'InitializeLookupEffect': {
        'Point6CDA': ('WriterRow', 'начало одной из 38 строк писателя'),
        'Point6CDC': ('WriterWord', 'генерация очередного четырёхбайтового звена'),
        'Point6CF9': ('BuildNibble', 'выделение старшей тетрады индекса'),
        'Point6D24': ('PointerRow', 'начало строки из 16 указателей'),
        'Point6D27': ('CheckUpper', 'проверка верхней границы 80'),
        'Point6D2E': ('CheckLower', 'проверка нижней границы 70'),
        'Point6D34': ('StorePage', 'преобразование ограниченного значения в страницу'),
        'Point6D49': ('CountPtrRow', 'счётчик строк после изменения стартовой страницы'),
        'Point6D4F': ('WarmPhases', 'одно из 40 подготовительных обновлений фаз')},
    'BuildIntroTexture': {'Point6D9A': ('CopySampleRow', 'перенос 128 байтов из середины страницы')},
    'BuildMirroredTexture': {
        'Point6DF0': ('MirrorRow', 'подготовка и копирование очередных 32 байтов'),
        'Point6DFE': ('MirrorPixel', 'нормализация и отражение очередного байта строки'),
        'Point6E15': ('MirrorHalf', 'обратное копирование первой половины во вторую')},
}


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    path = ROOT / 'Tools/Disasm/Reports/Symbols.json'
    symbols = json.loads(path.read_text(encoding='utf-8'))
    renames = {}
    docs = ['# Внутренние входы алгоритмов вступления', '',
            'Адресные метки заменены именами операций из разобранных алгоритмов.',
            'Адреса, инструкции, самомодификация и последовательные продолжения сохранены.',
            'Переименование не доказывает новые варианты выполнения.', '',
            '| Процедура | Адрес | Имя | Операция |', '| --- | --- | --- | --- |']
    for owner, labels in LABELS.items():
        for old, (new, purpose) in labels.items():
            assert len(new) <= 14
            before, after = 'Intro.' + owner + '.' + old, 'Intro.' + owner + '.' + new
            assert after not in symbols
            address = symbols.pop(before)
            symbols[after] = address
            renames[before] = after
            docs.append(f'| [{owner}](../Source/Intro/{owner}.asm) | #{address:04X} | {new} | {purpose} |')
    assert len(renames) == 44
    pending = {path: (json.dumps(symbols, ensure_ascii=False, indent=2) + '\n').encode('utf-8')}
    # Обновление только точных символов и определений, метки с похожим префиксом не затрагиваются.
    for folder, patterns in (('Source', ('*.asm', '*.inc')), ('Docs', ('*.md',))):
        for pattern in patterns:
            for path in (ROOT / folder).rglob(pattern):
                before = path.read_text(encoding='utf-8')
                text = before
                for old, new in renames.items():
                    text = re.sub(re.escape(old) + r'(?![\w.])', new, text)
                if path.parent == ROOT / 'Source/Intro' and path.stem in LABELS:
                    for old, (new, _) in LABELS[path.stem].items():
                        text, count = re.subn(r'^' + old + r':\s+', (new + ':').ljust(16), text, flags=re.M)
                        assert count == 1
                    marker = '; Документация [Intro](../../Docs/FunctionDetails/Intro.md)'
                    assert text.count(marker) == 1
                    text = text.replace(marker, marker + '\n                ; Имена внутренних входов [алгоритмы вступления](../../Docs/IntroInternalLabels.md)')
                if text != before:
                    lines = []
                    for line in text.splitlines():
                        code, sep, note = line.partition(';')
                        # Сохранение колонки комментария только на строках с изменённой ссылкой.
                        if sep and any(new in code for new in renames.values()):
                            line = code.rstrip().ljust(80) + ';' + note
                        lines.append(line)
                    pending[path] = ('\n'.join(lines) + '\n').encode('utf-8')
    docs += ['', 'Проверка положения всех кодовых меток выполняется',
             '[CheckSourceLabels](../Tools/Disasm/Research/CheckSourceLabels.py),',
             'инструкции сравнивает [VerifySources](../Tools/Disasm/VerifySources.py).', '']
    pending[ROOT / 'Docs/IntroInternalLabels.md'] = '\n'.join(docs).encode('utf-8')
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/IntroInternalLabels'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeIntroInternalLabels'
    assert not candidate.exists() and not history.exists()
    original = {path: path.read_bytes() if path.exists() else None for path in pending}
    for path, raw in pending.items():
        target = candidate / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for path, before in original.items():
        assert path.read_bytes() == before if before is not None else not path.exists()
        if before is not None:
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
    for path, raw in pending.items():
        path.write_bytes(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    report = dict(passed=True, renamed_internal_labels=44, instructions_changed=0,
                  physical_bytes_preserved=True, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/IntroInternalLabelsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
