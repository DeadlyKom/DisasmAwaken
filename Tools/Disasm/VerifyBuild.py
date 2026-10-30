"""Проверка уже собранного TRD, ассемблер не запускается."""

from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    original = (ROOT / "Tools/Disasm/Disk/original.trd").read_bytes()
    result = (ROOT / "Awakenv02.trd").read_bytes()
    # Проверка длины и всех физических байтов перед анализом отдельных записей.
    if len(result) != len(original):
        raise ValueError("Размер собранного образа отличается от оригинала")
    if result != original:
        offset = next(i for i, pair in enumerate(zip(result, original)) if pair[0] != pair[1])
        raise ValueError(f"Первое отличие по физическому смещению #{offset:06X}")
    allocations = []
    for entry in manifest["entries"]:
        offset = entry["offset"]
        data = result[offset:offset+entry["allocated_length"]]
        # Проверка каждой области, включая удалённые файлы и нестандартные хвосты.
        if digest(data) != entry["sectors_sha256"]:
            raise ValueError(f"Отличаются сектора записи {entry['slot']}")
        allocations.append(dict(slot=entry["slot"], deleted=entry["deleted"],
                                allocated_length=len(data), sha256=digest(data)))
    report = dict(method="independent_python_full_image_comparison", assembly_performed=False,
                  byte_identical=True, size=len(result), sha256=digest(result),
                  source_sha256=manifest["sha256"], allocations=allocations)
    path = ROOT / "Tools/Disasm/Reports/ImageVerification.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"PASS: {len(result)} identical bytes, {len(allocations)} disk allocations")
    print("SHA256", report["sha256"])


if __name__ == "__main__":
    main()
