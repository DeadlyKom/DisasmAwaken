"""Обновление документации из проверяемых реестров, сборку не запускает."""

from pathlib import Path
from collections import Counter
import json
import re
import argparse
from CandidateWorkspace import create_candidate, require_candidate


ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = ROOT


def load(name):
    return json.loads((ROOT/"Tools/Disasm/Reports"/name).read_text(encoding="utf-8"))


def write(path, text):
    target = ROOT/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip()+"\n",encoding="utf-8")


def link(function, prefix="../"):
    return f"[{function['region']}.{function['name']}]({prefix}{function['path']})"


def main():
    require_candidate(PROJECT_ROOT, ROOT)
    functions = load("Functions.json")
    source_map = load("SourceMap.json")
    flow = load("ControlFlow.json")
    screens = load("Screens.json")
    manifest = json.loads((ROOT/"Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    by_region = {r["name"]:r for r in flow}
    index = ["# Реестр исходных фрагментов", "",
             "Число файловых фрагментов не равно числу логических процедур. Фрагмент",
             "может содержать общий хвост, дополнительный вход или продолжение после",
             "косвенного вызова. Статус Unknown означает неустановленное назначение,",
             "его нельзя считать выполненным семантическим разбором.", "",
             "| Регион | Фрагментов | Описано | Подробности |", "| --- | ---: | ---: | --- |"]
    mutations = []
    for region in flow:
        name = region["name"]
        local = [f for f in functions if f["region"] == name]
        described = sum(f["semantic_status"]=="described" for f in local)
        index.append(f"| {name} | {len(local)} | {described} | [Факты](FunctionDetails/{name}.md) |")
        details = [f"# {name}", "", "Операционные факты ниже получены из исходных инструкций.",
                   "Список непосредственных чтений и записей не включает косвенные обращения",
                   "через HL, DE, BC, IX/IY и эффекты вызываемых подпрограмм.", ""]
        for function in local:
            body = [i for i in region["instructions"] if i["slot"]==function["slot"] and
                    function["offset"] <= i["offset"] < function["end_offset"]]
            calls, reads, writes, ports, indirect = set(), set(), set(), set(), set()
            for instruction in body:
                operation = instruction["operation"]
                for target in re.findall(r"CALL (?:[A-Z]+,)?#([0-9A-F]+)",operation):
                    calls.add(int(target,16))
                read = re.match(r"LD [A-Z]+,\(#([0-9A-F]+)\)",operation)
                store = re.match(r"LD \(#([0-9A-F]+)\),([A-Z]+)",operation)
                if read:
                    reads.add(int(read[1],16))
                if store:
                    address = int(store[1],16)
                    writes.add(address)
                    size = 1 if store[2] in ("A","B","C","D","E","H","L") else 2
                    for target in region["instructions"]:
                        if target["address"] <= address < target["address"] + len(bytes.fromhex(target["hex"])):
                            mutations.append(dict(region=name,writer=instruction["address"],target=address,
                                                  target_instruction=target["address"],size=size,
                                                  target_operation=target["operation"],path=function["path"]))
                            break
                if operation.startswith(("OUT ","IN ")):
                    ports.add(operation)
                if operation in ("JP (HL)","JP (IX)","JP (IY)"):
                    indirect.add(operation)
            listing = lambda values: ", ".join(f"`#{v:04X}`" for v in sorted(values)) or "нет непосредственных обращений"
            details.extend(["## "+function["name"], "", link(function,"../../"), "",
                            function["description"]+".", "",
                            f"Вход `#{function['address']:04X}`, запись {function['slot']}, "
                            f"смещения `#{function['offset']:04X}..#{function['end_offset']-1:04X}`.", "",
                            f"- Прямые вызовы: {listing(calls)}.",
                            f"- Непосредственные чтения: {listing(reads)}.",
                            f"- Непосредственные записи: {listing(writes)}.",
                            "- Ввод и вывод: "+(", ".join(f"`{p}`" for p in sorted(ports)) or "нет")+".",
                            "- Косвенное завершение: "+(", ".join(f"`{p}`" for p in sorted(indirect)) or "нет в этом фрагменте")+".", ""])
        write(f"Docs/FunctionDetails/{name}.md","\n".join(details))
    index.extend(["", "Все фрагменты:", "", "| Вход | Исходник | Назначение |", "| --- | --- | --- |"])
    for function in functions:
        index.append(f"| #{function['address']:04X} | {link(function)} | {function['description']} |")
    write("Docs/Functions.md","\n".join(index))

    # Сохранение адресов записей в инструкции без объявления каждой записи ошибкой.
    lines = ["# Изменяемые инструкции", "", "Это непосредственные записи внутрь размеченных инструкций того же",
             "представления памяти. Они включают сохранение SP, операнды и переключаемые",
             "ветви. Не перечисляют все косвенные записи и генерируемые области.", "",
             "| Регион | Запись из | Адрес записи | Исходная инструкция | Исходник |",
             "| --- | --- | --- | --- | --- |"]
    for item in mutations:
        lines.append(f"| {item['region']} | #{item['writer']:04X} | #{item['target']:04X} | "
                     f"`{item['target_operation']}` | [{Path(item['path']).name}](../{item['path']}) |")
    write("Docs/ModifiedCode.md","\n".join(lines))
    write("Tools/Disasm/Reports/ModifiedCode.json",json.dumps(mutations,ensure_ascii=False,indent=2))

    # Публикация исходного сценария без изменения его дисковых байтов.
    raw = (ROOT/"Tools/Disasm/Extracted/Active/05_LANG.C.bin").read_bytes()
    script = raw[0xA8F:].split(b"\0",1)[0].decode("cp866").replace("\r\n","\n").replace("\r","\n")
    write("Docs/MarketScript.txt",script)
    language = ["# Таблицы торгового языка LANG.C", "", "Подробный разбор хранится отдельно в [ScriptLanguage](ScriptLanguage.md).", "",
                "Вход интерпретатора — `#C000`, начало текста — `#CA8F`.",
                "Символы и таблицы проверены по самому файлу. [Исходный сценарий](MarketScript.txt)",
                "сохранён в UTF-8 для чтения, сборка использует исходные байты CP866.", "",
                "Сценарий содержит покупку и продажу товаров, кораблей и оборудования,",
                "плату за стоянку и начальные проверки. Поле `c` используется как кредиты,",
                "`X` выбирает событие. Полное предметное назначение остальных полей ещё",
                "требует сверки со структурами и писателями состояния.", "",
                "Сравнение возвращает слово 0 или 1 в DE. Слова выражений помещаются",
                "через HL альтернативного набора. Операнды и методы работы со стеком",
                "разбираются в исходниках Text, арифметические ограничения — в [Arithmetic](Arithmetic.md).", "",
                "Ниже все 102 трёхбайтовые записи семейства таблиц `#C935..#CA66`.",
                "Одинаковый символ в разных подтаблицах имеет разное назначение.", "",
                "| Адрес записи | Символ | Обработчик |", "| --- | --- | --- |"]
    for offset in range(0x935,0xA67,3):
        token = chr(raw[offset]).replace("|","\\|")
        address = int.from_bytes(raw[offset+1:offset+3],"little")
        function = next((f for f in functions if f["region"]=="Text" and f["address"]==address),None)
        language.append(f"| #{offset+0xC000:04X} | `{token}` | "+(link(function) if function else f"#{address:04X}")+" |")
    write("Docs/ScriptTokens.md","\n".join(language))

    # Инвентаризация физического содержимого и известных структур.
    formats = ["# Форматы данных", "", "Объявления находятся в `Includes/Structs/Include.inc`.", "",
               "| Тип | Размер | Подтверждённое назначение |", "| --- | --- | --- |",
               "| FTrDosEntry | #10 | исходная запись каталога |",
               "| FPackedHeader | #06 | HR, распакованная и упакованная длины |",
               "| FVisualEffect | #12 | запись эффекта, свободное состояние +7 |",
               "| FInterfaceItem | #10 | прямоугольник, флаги и два обработчика интерфейса |",
               "| FProjectedPoint | #05 | X, Y и составной код отсечения вершины |",
               "| FScriptToken | #03 | символ и указатель обработчика, 102 физических экземпляра |",
               "| FExpressionCall | #06 | левый операнд, адрес операции и правый операнд на стеке выражений |", "",
               "Три физических экземпляра FTexturePhase занимают по #06 байт и содержат Phase, Step и StepDelta. См. [Intro](Intro.md).", "",
               "Поля Unknown сохраняют неустановленное назначение. Объявление структуры",
               "само по себе не выделяет новую область памяти.", "",
               "В данных интерфейса сохранены 46 физических инициализаторов, затем #80.",
               "В `Source/Screens` сохранены 20 упакованных блоков с заголовками и хвостами.",
               "Остальные неклассифицированные диапазоны нельзя считать автоматически ресурсами",
               "или автоматически кодом, даже если они находятся в Source/Resources.", "",
               "| Запись | Имя | Параметр | Длина | Секторов | Хвост |", "| --- | --- | --- | ---: | ---: | ---: |"]
    for entry in manifest["entries"]:
        formats.append(f"| {entry['slot']} | {entry['name']}.{entry['extension']}"+
                       (" (удалена)" if entry["deleted"] else "")+
                       f" | #{entry['parameter']:04X} | {entry['length']} | {entry['sector_count']} | {entry['tail_length']} |")
    write("Docs/DataFormats.md","\n".join(formats))
    gallery = ["# Станционные фоны", "", "Формат знакомест описан в [Rendering](Rendering.md).",
               "Распаковка выполнена исходной процедурой #9EFF в изолированной модели.", ""]
    for screen in screens:
        gallery.extend([f"## Запись {screen['slot']}, блок {screen['index']}", "",
                        f"![Распакованный блок](Images/Screens/{screen['slot']:02d}_{screen['index']:02d}.png)", ""])
    write("Docs/Screens.md","\n".join(gallery))

    counts = Counter(item["kind"] for item in source_map)
    sizes = Counter()
    for item in source_map:
        sizes[item["kind"]] += item["length"]
    inventory = dict(fragments=len(functions),described=sum(f["semantic_status"]=="described" for f in functions),
                     unknown=sum(f["semantic_status"]=="unknown" for f in functions),
                     instructions=sum(r["instruction_count"] for r in flow),
                     physical_bytes_by_kind=dict(sizes),ranges_by_kind=dict(counts),
                     full_semantic_analysis_complete=False)
    write("Tools/Disasm/Reports/Inventory.json",json.dumps(inventory,ensure_ascii=False,indent=2))
    validation = ["# Проверки и ограничения", "", "## Подтверждено", "",
                  "- Извлечение всех 44 записей и восстановление 655360 байт по физическим компонентам.",
                  "- Предыдущая сборка средствами SjASMPlus и побайтовое совпадение существующего TRD.",
                  "- Ограниченное исполнение исходных станционного и полётного модулей с моделью TR-DOS.",
                  "- Распаковка 20 блоков исходным распаковщиком, установлен формат станционных знакомест.",
                  "- 1210 примеров торговой арифметики и 208 примеров масштабированного умножения.", "",
                  "Первичные результаты находятся в `Tools/Disasm/Reports`, журнал сборки — `Tmp/Build.log`.", "",
                  "После изменения расположения материалов, символов и оформления новая сборка не выполнялась.",
                  "Статическая сверка текущих исходников выполняется отдельно и не доказывает их компилируемость.", "",
                  "## Текущее покрытие", "",
                  f"- Исходных фрагментов: {inventory['fragments']}.",
                  f"- Именовано по установленному назначению или роли интерфейса: {inventory['described']}.",
                  f"- Назначение Unknown: {inventory['unknown']}.",
                  f"- Размеченных инструкций: {inventory['instructions']}.", "",
                  "Количество байтов кода не является процентом завершённости разбора. В образе",
                  "есть ресурсы, копии модулей, генерируемый код и ещё не классифицированные диапазоны.", "",
                  "## Не подтверждено", "",
                  "- Достижение экрана станции и подробный игровой прогон обоих образов в Unreal.",
                  "- Все игровые ветви, сохранения, финал, взаимодействия и косвенные вызовы.",
                  "- Точные регистровые контракты всех фрагментов и назначение всех полей.",
                  "- Полнота семантического разбора, пока остаются Unknown и непрослеженные входы.", "",
                  "Модели начинают исполнение с уже загруженного STATIONF или ACTION и заменяют",
                  "вызовы интерфейса TR-DOS. Они не подменяют настоящую проверку старта с диска.",
                  "Результат следует считать воспроизводимой исследовательской основой, а не",
                  "завершённым объяснением каждой процедуры игры."]
    # Сохранение границ новых изолированных проверок отдельно от прежней сборки.
    extra_checks = (
        ("GlyphRenderVerification.json", "Глифы, все варианты сдвига, граничные битовые строки и отказы проверены без IRQ. См. [GlyphRendering](GlyphRendering.md)."),
        ("TextRowVerification.json", "Байтовое продвижение текстовой строки проверено для всех курсоров и высот. См. [GlyphRendering](GlyphRendering.md)."),
        ("TextMeasureVerification.json", "Два измерителя текста проверены на исходной и пяти граничных таблицах ширин, без вывода пикселей. См. [Font](Font.md)."),
        ("FontResourceVerification.json", "Таблица ширин и восемь строк каждого глифа выделены с точным восстановлением прежнего двоичного диапазона. См. [Font](Font.md)."),
        ("RegisterCellsVerification.json", "Регистрация ключа и видимого прямоугольника карты проверена на искусственной таблице свободных пар. См. [CellMap](CellMap.md)."),
        ("RegisteredBitmapVerification.json", "Регистрация с заливкой bitmap и возвратом указателя Flags проверена без IRQ. См. [Interface](Interface.md)."),
        ("CellMapVerification.json", "Адресация карты владельцев и снятие индексной пары проверены отдельно от всего восстановления фона. См. [CellMap](CellMap.md)."),
        ("StationCoreVerification.json", "Перенесённые входы страницы и объединение четырёх слов проверены без аппаратного переключения банков и IRQ. См. [StationCore](StationCore.md)."),
        ("InsetTextWindowVerification.json", "Внутреннее текстовое окно с отступами проверено без вывода глифов. См. [TextWindow](TextWindow.md)."),
        ("ItemBitmapVerification.json", "Заливка элемента с отсечением проверена на искусственно заданной геометрии записей 0 и 45 без IRQ. См. [Interface](Interface.md)."),
        ("FillRectangleVerification.json", "Заполнение прямоугольника проверено на исходных инструкциях и игровых таблицах без отсечения и IRQ. См. [StationSpans](StationSpans.md)."),
        ("ItemFieldVerification.json", "Адрес поля интерфейсной записи проверен отдельно от чтения данных и допустимости индексов. См. [Interface](Interface.md)."),
        ("TextWindowVerification.json", "Настройка текстового окна и его одноместный снимок проверены без вывода пикселей шрифта. См. [TextWindow](TextWindow.md)."),
        ("StationSpanVerification.json", "Узоры, счётчик отсечения и коррекция экранного адреса станции проверены отдельно. См. [StationSpans](StationSpans.md)."),
        ("StationSpanWriterVerification.json", "Писатель полосы проверен с четырьмя комбинациями изменяемых кодов краёв. См. [StationSpans](StationSpans.md)."),
        ("FrameRasterSetupVerification.json", "Подготовитель рамки проверен с искусственными адресными таблицами, содержимое игровых таблиц этим не доказано. См. [StationSpans](StationSpans.md)."),
        ("InsetFrameVerification.json", "Рамка со скосами проверена с исходным построителем адресных таблиц, без IRQ и нативного запуска. См. [StationSpans](StationSpans.md)."),
        ("BandFrameVerification.json", "Оба вида верхней полосы рамки проверены с исходным построителем адресных таблиц, без IRQ и нативного запуска. См. [StationSpans](StationSpans.md)."),
        ("BasicLoaderVerification.json", "Первый загрузчик проверен до входа TR-DOS, ROM и дисковое чтение не исполнялись. См. [Loader](Loader.md)."),
        ("TexturePhaseVerification.json", "Три состояния текстурных фаз и все младшие байты курсора проверены без внешних IRQ. См. [Intro](Intro.md)."),
        ("DecimalVerification.json", "Десятичный считыватель проверен на всех числах 0..99999 и дополнительных разделителях. См. [ScriptLanguage](ScriptLanguage.md)."),
        ("ExpressionCallVerification.json", "Запись бинарного вызова проверена с шестью исходными обработчиками, произвольные обработчики этим не доказаны. См. [ScriptLanguage](ScriptLanguage.md)."),
        ("TokenDispatchVerification.json", "Поиск токенов и запись операторов проверены отдельно от полного сценария. См. [ScriptLanguage](ScriptLanguage.md)."),
        ("SelectionIndexVerification.json", "Байтовые суммы индексов проверены по всему входному диапазону, корректность всего интерфейса этим не доказана."),
        ("MusicSlideVerification.json", "Установка скольжения тона C проверена отдельно от воспроизведения произвольных команд. См. [Music](Music.md)."),
        ("MapMathVerification.json", "Квадраты и корень разности квадратов проверены по полному диапазону байтовых аргументов и Carry. См. [MapMath](MapMath.md)."),
        ("MapRasterVerification.json", "Растровые переходы и нелокальные выходы проверены отдельно от полного рисования карты. См. [MapRaster](MapRaster.md)."),
    )
    for report_name, text in extra_checks:
        path = ROOT / "Tools/Disasm/Reports" / report_name
        if path.exists() and json.loads(path.read_text(encoding="utf-8")).get("passed"):
            position = validation.index("## Текущее покрытие")
            validation[position:position] = [text, f"Отчёт — [результат проверки](../Tools/Disasm/Reports/{report_name}).", ""]
    unknown_contracts = [f for f in functions if "Unknown, регистровый контракт ещё не доказан"
                         in (ROOT / f["path"]).read_text(encoding="utf-8")]
    position = validation.index(f"- Размеченных инструкций: {inventory['instructions']}.")
    named_unknown = sum(f["semantic_status"] == "described" for f in unknown_contracts)
    validation.insert(position + 1, f"- Без доказанного регистрового контракта: {len(unknown_contracts)}, включая {named_unknown} именованных фрагментов.")
    # Сохранение пользовательского подтверждения отдельно от результатов изолированных моделей.
    unreal_path = ROOT / "Tools/Disasm/Reports/UnrealVerification.json"
    if unreal_path.exists():
        unreal = json.loads(unreal_path.read_text(encoding="utf-8"))
        checks = unreal.get("manual_checks", {})
        manual_lines = []
        if checks.get("original", {}).get("game_start_verified"):
            manual_lines.append("- Запуск оригинала в Unreal подтверждён пользователем сообщением «запустился».")
        if checks.get("rebuilt", {}).get("game_start_preliminarily_confirmed"):
            manual_lines.append("- Запуск пересобранного образа в Unreal предварительно подтверждён пользователем сообщением «вроде тоже запустился».")
        position = validation.index("Первичные результаты находятся в `Tools/Disasm/Reports`, журнал сборки — `Tmp/Build.log`.")
        validation[position:position] = manual_lines + ([""] if manual_lines else [])
    intro_path = ROOT / "Tools/Disasm/Reports/IntroVerification.json"
    if intro_path.exists():
        intro = json.loads(intro_path.read_text(encoding="utf-8"))
        if all(item.get("passed") for item in intro.get("results", [])):
            position = validation.index("## Текущее покрытие")
            validation[position:position] = [
                "Изолированные проверки вступления описаны в [Intro](Intro.md), включая",
                "генерируемые цепочки, восстановление SP и граничное обращение к ПЗУ.", ""]
    music_path = ROOT / "Tools/Disasm/Reports/MusicVerification.json"
    if music_path.exists():
        music = json.loads(music_path.read_text(encoding="utf-8"))
        if music.get("passed"):
            position = validation.index("## Текущее покрытие")
            validation[position:position] = [
                f"Музыкальный проигрыватель проверен на {music['ticks_checked']} тиках до петли позиций,",
                "48 преобразованных указателях PT3 и 28 записях глушения AY. Это проверка портов,",
                "без прослушивания звука. См. [Music](Music.md).", ""]
    effects_path = ROOT / "Tools/Disasm/Reports/EffectsVerification.json"
    if effects_path.exists():
        effects = json.loads(effects_path.read_text(encoding="utf-8"))
        if effects.get("passed"):
            position = validation.index("## Текущее покрытие")
            validation[position:position] = [
                "Арифметика VOXAL проверена на 65280 сочетаниях деления, 1024 сочетаниях",
                "семибитного умножения и 324 сочетаниях с входным IY. Отличия за пределами",
                "подтверждённых контрактов сохранены в отчёте. См. [Effects](Effects.md).", ""]
    final_path = ROOT / "Tools/Disasm/Reports/FinalVerification.json"
    if final_path.exists():
        final = json.loads(final_path.read_text(encoding="utf-8"))
        if final.get("passed"):
            position = validation.index("## Текущее покрытие")
            validation[position:position] = [
                "Построитель финальной сцены создал проверенную цепочку 10552 байта, отдельно",
                "подтверждён полный перенос bitmap и атрибутов с восстановлением SP без IRQ.",
                "Raster-синхронизация не проверена. См. [Final](Final.md).", ""]
    write("Docs/Validation.md","\n".join(validation))
    print(json.dumps(inventory,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="Новая папка внутри Tools/Disasm/Research/Candidates")
    arguments = parser.parse_args()
    ROOT = create_candidate(PROJECT_ROOT, arguments.output, "documentation")
    main()
