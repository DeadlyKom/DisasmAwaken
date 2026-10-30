"""Однократное включение подтверждённого XOR A #C0C8 в непрерывный исходный код."""

from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]


def main():
    history = ROOT / "Tools/Disasm/Research/History/ConfirmBandContinuation"
    if history.exists():
        raise ValueError("Изменение уже применялось, повторная запись запрещена")
    reports = ROOT / "Tools/Disasm/Reports"
    load = lambda name: json.loads((reports / name).read_text(encoding="utf-8"))
    flow, functions, ranges, inventory = [load(name) for name in
        ("ControlFlow.json", "Functions.json", "SourceMap.json", "Inventory.json")]
    function = next(f for f in functions if f["region"] == "Station" and f["address"] == 0xC093)
    unknown = next(r for r in ranges if r["slot"] == 4 and r["offset"] == 0x60C8)
    code = next(r for r in ranges if r["path"] == function["path"])
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"] + ".sectors.bin")).read_bytes()
    # Проверка границ не допускает поглощения соседних данных или ранее внесённых изменений.
    if (function["end_offset"] != 0x60C8 or unknown["kind"] != "unclassified"
            or unknown["length"] != 1 or (ROOT / unknown["path"]).read_bytes() != b"\xaf"
            or source[0x60C8] != 0xAF):
        raise ValueError("Не совпало исходное состояние продолжения")
    region = next(r for r in flow if r["name"] == "Station")
    if any(i["address"] == 0xC0C8 for i in region["instructions"]):
        raise ValueError("Инструкция уже присутствует")
    region["instructions"].append(dict(address=0xC0C8, operation="XOR A", hex="af", slot=4, offset=0x60C8))
    region["instructions"].sort(key=lambda i: (i["slot"], i["offset"]))
    region["instruction_count"] += 1
    region["code_bytes"] += 1
    region["classified_fraction"] = region["code_bytes"] / region["total_bytes"]
    function["end_offset"] += 1
    code["length"] += 1
    code["sha256"] = hashlib.sha256(source[code["offset"]:code["offset"] + code["length"]]).hexdigest()
    ranges.remove(unknown)
    inventory["instructions"] = sum(r["instruction_count"] for r in flow)
    inventory["physical_bytes_by_kind"] = dict(Counter())
    sizes = Counter()
    for r in ranges:
        sizes[r["kind"]] += r["length"]
    inventory["physical_bytes_by_kind"] = dict(sizes)
    inventory["ranges_by_kind"] = dict(Counter(r["kind"] for r in ranges))
    pending = {}
    for name, value in zip(("ControlFlow.json", "Functions.json", "SourceMap.json", "Inventory.json"),
                           (flow, functions, ranges, inventory)):
        pending[reports / name] = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path = ROOT / function["path"]
    text = path.read_text(encoding="utf-8")
    text = text.replace("#6093..#60C7", "#6093..#60C8")
    marker = "                endmodule"
    position = text.index(marker)
    pending[path] = text[:position] + "                ; сброс Sign перед продолжением видимой верхней полосы\n                XOR A\n" + text[position:]
    path = ROOT / "Source/Files/04_STATIONF.inc"
    text = path.read_text(encoding="utf-8")
    old = ('                assert $ == #60C8\n'
           '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n'
           '                incbin "../Resources/04_STATIONF/Unclassified074.bin"\n')
    if old not in text:
        raise ValueError("Не найдено исходное включение байта")
    text = text.replace(old, "")
    for index, name in enumerate(("UnknownC093", "UnknownC0C9")):
        old = f'                include "../Station/{name}.asm"'
        text = text.replace(old, old.ljust(80) + f"; ({index}) жёсткий порядок, последовательное исполнение")
    pending[path] = text
    # Сохранение всех изменяемых файлов и единственного двоичного байта перед записью.
    for path in (*pending, ROOT / unknown["path"]):
        target = history / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    for path, text in pending.items():
        path.write_text(text, encoding="utf-8")
    resource = (ROOT / unknown["path"]).resolve()
    if not resource.is_relative_to(ROOT / "Source/Resources"):
        raise ValueError("Ресурс находится вне ожидаемой папки")
    resource.unlink()
    print("#C0C8 включён как XOR A, физические байты сохранены в истории")


if __name__ == "__main__":
    main()
