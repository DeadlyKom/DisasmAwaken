"""Точечное применение ручного разбора из Knowledge, Contracts и Notes.

Не является частью сборки. Перед записью сохраняет затрагиваемые файлы,
требует неизвестный исходный фрагмент и проверяет совпадение его инструкций
с реестром. Не заменяет полный экспорт исходников.
"""

from pathlib import Path
import argparse
import json
import re
import shutil
import sys

from Knowledge import FUNCTIONS
from Contracts import CONTRACTS
from SemanticNames import LABELS, name_operands, documentation_links
from SourcePresentation import format_function, instructions, continuity
from MusicNotes import COMMENTS as MUSIC_COMMENTS
from TextNotes import COMMENTS as TEXT_COMMENTS
from MapNotes import COMMENTS as MAP_COMMENTS
from BasicNotes import COMMENTS as BASIC_COMMENTS
from IntroNotes import COMMENTS as INTRO_COMMENTS, NOTES as INTRO_NOTES
from StationNotes import COMMENTS as STATION_COMMENTS
from ValidateNotes import validate_notes

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from VerifySources import main as verify_sources


def promote(region, address, refresh=False):
    # Проверка всех текущих инструкций и данных до подготовки точечного изменения.
    verify_sources()
    functions_path = ROOT / "Tools/Disasm/Reports/Functions.json"
    functions = json.loads(functions_path.read_text(encoding="utf-8"))
    function = next(f for f in functions if f["region"] == region and f["address"] == address)
    if function["semantic_status"] != "unknown" and not refresh:
        raise ValueError("Требуется неизвестный фрагмент, повторное продвижение запрещено")
    name, description = FUNCTIONS[region][address]
    contract = CONTRACTS[region, address]
    old_name, old_path = function["name"], function["path"]
    old_description = function["description"]
    new_path = f"Source/{region}/{name}.asm"
    if (ROOT / new_path).exists() and new_path != old_path:
        raise ValueError("Новый исходник уже существует")
    current = (ROOT / old_path).read_text(encoding="utf-8")
    flow = json.loads((ROOT / "Tools/Disasm/Reports/ControlFlow.json").read_text(encoding="utf-8"))
    decoded = [i for group in flow if group["name"] == region for i in group["instructions"]
               if function["offset"] <= i["offset"] < function["end_offset"] and i["slot"] == function["slot"]]
    comments = {"Music": MUSIC_COMMENTS, "Text": TEXT_COMMENTS, "Map": MAP_COMMENTS,
                "Basic": BASIC_COMMENTS, "Intro": INTRO_COMMENTS, "Station": STATION_COMMENTS}.get(region, {})
    validate_notes(flow, {region: comments})
    if len(instructions(current)) != len(decoded):
        raise ValueError("Фрагмент содержит неизвестные ручные изменения инструкций")
    replacements = {f"{region}.{old_name}.": f"{region}.{name}.",
                    f"/{region}/{old_name}.asm": f"/{region}/{name}.asm"}
    for (label_region, label_address), label in LABELS.items():
        if label_region == region and address <= label_address < address + function["end_offset"] - function["offset"]:
            replacements[f"{region}.{name}.Point{label_address:04X}"] = f"{region}.{name}.{label}"

    def rename(text, path=None):
        previous = text
        for before, after in replacements.items():
            text = text.replace(before, after)
        # Обновление имени файла в комментарии продолжения только при совпадении полного региона и функции.
        text = "\n".join(line.replace("продолжение в " + old_name + ".asm", "продолжение в " + name + ".asm")
                         if "@" + region + "." + name + "." in line else line
                         for line in text.split("\n"))
        # Переименование локального заголовка ограничено документацией выбранного региона.
        if path == ROOT / f"Docs/FunctionDetails/{region}.md":
            text = re.sub(r"\b" + re.escape(old_name) + r"\b", name, text)
        if path and path.suffix == ".md":
            text = "\n".join(line.replace(old_name + ".asm]", name + ".asm]").replace("[" + old_name + "]", "[" + name + "]")
                             .replace("[" + region + "." + old_name + "]", "[" + region + "." + name + "]")
                             if f"/{region}/{name}.asm" in line else line for line in text.split("\n"))
        # Проверка изменившихся строк сохраняет линейку правых комментариев при удлинении имени.
        if path and path.suffix in (".asm", ".inc") and text != previous:
            updated = []
            for old_line, line in zip(previous.splitlines(), text.splitlines()):
                if line != old_line and ";" in line and not line.lstrip().startswith(";"):
                    code, comment = line.split(";", 1)
                    if len(code.rstrip()) >= 80:
                        raise ValueError("Не помещается переименованная инструкция: " + code)
                    line = code.rstrip().ljust(80) + ";" + comment
                updated.append(line)
            text = "\n".join(updated) + ("\n" if text.endswith("\n") else "")
        return text

    history = ROOT / f"Tools/Disasm/Research/History/Before{name}"
    if history.exists():
        if not refresh:
            raise ValueError("История этого изменения уже существует")
        # Создание новой неизменяемой версии истории при уточнении уже разобранного контракта.
        revision = 2
        while history.exists():
            history = ROOT / f"Tools/Disasm/Research/History/Before{name}_Update{revision:02d}"
            revision += 1
    pending = {}
    for base in ("Source", "Docs", "Tools/Disasm/Reports"):
        for path in (ROOT / base).rglob("*"):
            if not path.is_file() or path.suffix not in (".asm", ".inc", ".json", ".md") or "Runtime" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            updated = rename(text, path)
            refresh_description = (old_description != description and base == "Docs"
                                   and path.name in ("Functions.md", region + ".md"))
            if updated != text or refresh_description:
                pending[path] = updated

    inputs, outputs, corrupt, notes = contract
    if region == "Intro":
        notes = [*notes, *INTRO_NOTES.get(address, [])]
    lines = [" " * 16 + "module " + region, " " * 16 + "module " + name,
             *documentation_links(region, address),
             "; -----------------------------------------", "; " + description,
             f"; исходная запись {function['slot']}, файловые смещения #{function['offset']:04X}..#{function['end_offset']-1:04X}",
             "; In:", *[";   " + s for s in inputs], "; Out:", *[";   " + s for s in outputs],
             "; Corrupt:", *[";   " + s for s in corrupt], "; Note:", *[";   " + s for s in notes],
             "; -----------------------------------------"]
    code_lines = [line for line in current.splitlines()
                  if line.strip() and not line.lstrip().startswith(";")
                  and not line[16:].strip().lower().startswith(("module ", "endmodule"))]
    local_labels = {}
    for instruction, original in zip(decoded, code_lines):
        before, right = comments.get(instruction["address"], ([], None))
        lines.extend(" " * 16 + "; " + comment for comment in before)
        op, sep, old_right = original[16:].partition(";")
        op = name_operands(region, address, rename(op.strip()))
        label = original[:16].strip()
        if (region, instruction["address"]) in LABELS:
            label = LABELS[region, instruction["address"]] + ":"
        # Проверка уникальности итоговых меток до записи кандидата и изменения реестров.
        if label:
            local_name = label.removesuffix(":")
            if len(local_name) > 15:
                raise ValueError("Локальная метка не помещается до позиции 16: " + local_name)
            if local_name in local_labels:
                raise ValueError("Повторная локальная метка " + local_name + " по адресам "
                                 + format(local_labels[local_name], "04X") + " и "
                                 + format(instruction["address"], "04X"))
            local_labels[local_name] = instruction["address"]
        text = label.ljust(16) + op
        right = right or (old_right.strip() if sep else None)
        if right:
            if len(text) >= 80:
                raise ValueError("Не помещается правый комментарий: " + text)
            text = text.ljust(80) + "; " + right
        lines.append(text)
    lines += ["", " " * 16 + "endmodule", " " * 16 + "endmodule"]
    following, _ = continuity(functions, flow)
    pending[ROOT / old_path] = format_function("\n".join(lines), following.get(old_path))
    function.update(name=name, description=description, path=new_path, semantic_status="described")
    pending[functions_path] = rename(json.dumps(functions, ensure_ascii=False, indent=2)) + "\n"
    # Регистрация новых внутренних меток, у которых раньше не было адресного имени в Symbols.
    symbols_path = ROOT / "Tools/Disasm/Reports/Symbols.json"
    symbols = json.loads(pending.get(symbols_path, symbols_path.read_text(encoding="utf-8")))
    for instruction in decoded:
        label = LABELS.get((region, instruction["address"]))
        if label:
            symbols[f"{region}.{name}.{label}"] = instruction["address"]
    pending[symbols_path] = json.dumps(symbols, ensure_ascii=False, indent=2) + "\n"
    inventory_path = ROOT / "Tools/Disasm/Reports/Inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["described"] = sum(f["semantic_status"] == "described" for f in functions)
    inventory["unknown"] = sum(f["semantic_status"] == "unknown" for f in functions)
    pending[inventory_path] = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    for path in list(pending):
        if path.suffix == ".md":
            text = pending[path]
            if path.name == region + ".md":
                marker = "## " + name
                if marker in text:
                    position = text.index(marker)
                    text = text[:position] + text[position:].replace(
                        old_description + ".", description + ".", 1)
            elif path.name == "Functions.md":
                text = "\n".join(line.replace(old_description, description)
                                 if region + "." + name in line else line for line in text.splitlines()) + "\n"
                # Обновление чисел выбранного региона после изменения смыслового статуса.
                local = [f for f in functions if f["region"] == region]
                count = sum(f["semantic_status"] == "described" for f in local)
                text = re.sub(r"^\| " + re.escape(region) + r" \| \d+ \| \d+ \|",
                              f"| {region} | {len(local)} | {count} |", text, flags=re.M)
            pending[path] = text
    # Сохранение исходных файлов до применения подготовленного точечного изменения.
    for path in pending:
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    for path, text in pending.items():
        path.write_text(text, encoding="utf-8")
    source, destination = (ROOT / old_path).resolve(), (ROOT / new_path).resolve()
    if not source.is_relative_to(ROOT) or not destination.is_relative_to(ROOT):
        raise ValueError("Путь перемещения вне проекта")
    if source != destination:
        shutil.move(str(source), str(destination))
    print(f"{region}.{name}, обновлено файлов {len(pending)}, исходные версии сохранены в истории")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("region")
    parser.add_argument("address", type=lambda text: int(text, 0))
    parser.add_argument("--refresh", action="store_true", help="Уточнить уже именованную процедуру по ручному контракту")
    args = parser.parse_args()
    promote(args.region, args.address, args.refresh)
