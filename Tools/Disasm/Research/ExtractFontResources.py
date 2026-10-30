"""Однократное выделение исходной таблицы ширин и восьмибайтовых глифов без изменения дисковых байтов."""

from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm"))
from VerifySources import main as verify_sources


def main():
    verify_sources()
    history = ROOT / "Tools/Disasm/Research/History/BeforeFontResources"
    if history.exists():
        raise ValueError("Выделение ресурсов уже выполнялось")
    reports = ROOT / "Tools/Disasm/Reports"
    source_map = json.loads((reports / "SourceMap.json").read_text(encoding="utf-8"))
    old = next(r for r in source_map if r["slot"] == 4 and r["offset"] == 0x2238)
    if old["kind"] != "unclassified" or old["length"] != 0x1820:
        raise ValueError("Не совпали исходные границы ресурса")
    raw = (ROOT / old["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != old["sha256"]:
        raise ValueError("Изменён исходный двоичный блок")
    pieces = (
        (0x2238, 0x2900, old["path"], "unclassified", None, None),
        (0x2900, 0x2A00, "Source/Station/Resources/FontWidths.bin", "binary_resource", 0x8900, "FONT_WIDTHS_256"),
        (0x2A00, 0x3200, "Source/Station/Resources/FontGlyphs.bin", "binary_resource", 0x8A00, "FONT_256_GLYPHS_8_ROWS"),
        (0x3200, 0x3A58, "Source/Resources/04_STATIONF/Unclassified044Tail.bin", "unclassified", None, None),
    )
    records = []
    payloads = {}
    for start, end, path, kind, origin, fmt in pieces:
        target = ROOT / path
        if path != old["path"] and target.exists():
            raise ValueError("Новый ресурс уже существует " + path)
        data = raw[start - 0x2238:end - 0x2238]
        payloads[target] = data
        record = dict(slot=4, offset=start, length=end-start, kind=kind, path=path,
                      origin=origin, sha256=hashlib.sha256(data).hexdigest())
        if fmt:
            record["format"] = fmt
        records.append(record)
    if b"".join(payloads.values()) != raw:
        raise ValueError("Нарушено побайтовое восстановление исходного блока")
    index = source_map.index(old)
    source_map[index:index + 1] = records
    include = ROOT / "Source/Files/04_STATIONF.inc"
    text = include.read_text(encoding="utf-8")
    marker = '                incbin "../Resources/04_STATIONF/Unclassified044.bin"'
    if text.count(marker) != 1:
        raise ValueError("Не найдено единственное включение исходного блока")
    replacement = [marker]
    for record in records[1:]:
        replacement += [f"                assert $ == #{record['offset']:04X}",
                        "                ; " + ("исходный ресурс " + record["format"] if record["kind"] == "binary_resource"
                                                else "Unknown, исходные байты после шрифта"),
                        '                incbin "../' + record["path"][7:] + '"']
    pending = {include: text.replace(marker, "\n".join(replacement)).encode("utf-8"),
               reports / "SourceMap.json": (json.dumps(source_map, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
               **payloads}
    inventory_path = reports / "Inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    totals = Counter()
    for record in source_map:
        totals[record["kind"]] += record["length"]
    inventory["physical_bytes_by_kind"] = dict(totals)
    inventory["ranges_by_kind"] = dict(Counter(r["kind"] for r in source_map))
    pending[inventory_path] = (json.dumps(inventory, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    # Сохранение единственного исходного блока и всех заменяемых текстов до записи новых файлов.
    for path in pending:
        if path.exists():
            target = history / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    for path, data in pending.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    verify_sources()
    report = {"method": "original_range_split_with_complete_byte_reconstruction", "passed": True,
              "original_path": old["path"], "original_sha256": old["sha256"],
              "original_length": len(raw), "records": records, "assembly_executed": False}
    (reports / "FontResourceVerification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Выделено 256 байтов ширины и 2048 байтов глифов, исходные байты сохранены")


if __name__ == "__main__":
    main()
