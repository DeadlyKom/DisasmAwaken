"""Извлечение TRD без запуска игры, дизассемблера или сборочных инструментов."""

from pathlib import Path
import argparse
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[2]
SECTOR_SIZE = 256
TRACK_SECTORS = 16
CATALOG_SLOTS = 128
SYSTEM_SIZE = 4096


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def store(relative, data):
    # Сохранение нового артефакта без перезаписи отличающихся пользовательских данных.
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f"Отказ от перезаписи отличающегося файла: {path}")
    if not path.exists():
        path.write_bytes(data)
    return {"path": relative, "size": len(data), "sha256": sha256(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.resolve().read_bytes()

    # Проверка геометрии перед чтением каталога и выделенных областей.
    if len(image) != 655360:
        raise ValueError("Ожидался TRD размером 655360 байт")
    occupied = bytearray(len(image))
    occupied[:SYSTEM_SIZE] = b"\x01" * SYSTEM_SIZE
    entries = []
    components = []
    disk = "Tools/Disasm/Disk"
    components.append(store(f"{disk}/original.trd", image))
    system = store(f"{disk}/System.bin", image[:SYSTEM_SIZE])
    system["offset"] = 0
    components.append(system)

    # Поиск всех непустых записей, включая записи с признаком удаления.
    for slot in range(CATALOG_SLOTS):
        header = image[slot * 16:slot * 16 + 16]
        if header[0] == 0:
            continue
        deleted = header[0] == 1
        raw_name = header[:8].decode("latin1")
        name = ("_" + raw_name[1:] if deleted else raw_name).strip()
        extension = chr(header[8])
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        safe_extension = re.sub(r"[^A-Za-z0-9_.-]", "_", extension)
        category = "Deleted" if deleted else "Active"
        stem = f"Tools/Disasm/Extracted/{category}/{slot:02d}_{safe_name}.{safe_extension}"
        length = int.from_bytes(header[11:13], "little")
        start = int.from_bytes(header[9:11], "little")
        sector_count, sector, track = header[13:16]
        offset = (track * TRACK_SECTORS + sector) * SECTOR_SIZE
        allocated = sector_count * SECTOR_SIZE

        # Проверка исходных границ без предположения о назначении хвостов.
        if sector >= TRACK_SECTORS or offset < SYSTEM_SIZE:
            raise ValueError(f"Недопустимое размещение записи {slot}")
        if length > allocated or offset + allocated > len(image):
            raise ValueError(f"Недопустимая длина записи {slot}")
        if any(occupied[offset:offset + allocated]):
            raise ValueError(f"Пересечение выделенных областей записи {slot}")
        occupied[offset:offset + allocated] = b"\x01" * allocated
        payload = image[offset:offset + length]
        sectors = image[offset:offset + allocated]
        payload_info = store(stem + ".bin", payload)
        sectors_info = store(stem + ".sectors.bin", sectors)
        sectors_info["offset"] = offset
        components.append(sectors_info)
        store(stem + ".header.bin", header)
        store(stem + ".tail.bin", sectors[length:])
        entries.append({
            "slot": slot, "deleted": deleted, "raw_name_hex": header[:8].hex(),
            "name": name, "extension": extension, "parameter": start,
            "length": length, "sector_count": sector_count,
            "first_sector": sector, "first_track": track, "offset": offset,
            "allocated_length": allocated, "tail_length": allocated - length,
            "path": stem, "payload_sha256": payload_info["sha256"],
            "sectors_sha256": sectors_info["sha256"],
        })

    # Сохранение свободных областей с исходными физическими смещениями.
    position = SYSTEM_SIZE
    while position < len(image):
        if occupied[position]:
            position += 1
            continue
        begin = position
        while position < len(image) and not occupied[position]:
            position += 1
        item = store(f"{disk}/Unallocated/{begin:06X}.bin", image[begin:position])
        item["offset"] = begin
        components.append(item)

    # Проверка полного непересекающегося покрытия диска извлечёнными компонентами.
    reconstructed = bytearray(len(image))
    covered = bytearray(len(image))
    physical = [item for item in components if "offset" in item]
    for item in physical:
        data = (ROOT / item["path"]).read_bytes()
        begin = item["offset"]
        end = begin + len(data)
        if any(covered[begin:end]):
            raise ValueError("Повторное покрытие байтов диска")
        reconstructed[begin:end] = data
        covered[begin:end] = b"\x01" * len(data)
    if not all(covered) or reconstructed != image:
        raise ValueError("Извлечённые компоненты не воспроизводят исходный диск")
    manifest = {
        "source_filename": args.image.name, "size": len(image),
        "sha256": sha256(image), "sector_size": SECTOR_SIZE,
        "sectors_per_track": TRACK_SECTORS,
        "system_hex_08e0_0900": image[0x8E0:0x900].hex(),
        "entries": entries, "components": physical,
        "verification": {"covered_bytes": sum(covered),
                         "byte_identical": True,
                         "reconstructed_sha256": sha256(reconstructed),
                         "assembly_performed": False},
    }
    store(f"{disk}/Manifest.json",
          (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"entries": len(entries),
                      "active": sum(not e["deleted"] for e in entries),
                      "deleted": sum(e["deleted"] for e in entries),
                      "components": len(physical),
                      "verification": manifest["verification"]}, indent=2))


if __name__ == "__main__":
    main()
