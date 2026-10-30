"""Распаковка экранов исходной процедурой игры в изолированной модели Z80."""

from pathlib import Path
import hashlib
import json
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP
from PIL import Image


def unpack(data):
    memory = [0] * 65536
    station = (ROOT / "Tools/Disasm/Extracted/Active/04_STATIONF.C.bin").read_bytes()
    memory[0x6000:] = station
    memory[0xC000:0xC000+len(data)] = data
    memory[0x5FFE:0x6000] = [0xFF, 0x3F]
    sim = Simulator(memory, {"PC":0x9EFF, "HL":0xC000, "DE":0x4000, "SP":0x5FFE})
    # Проверка выхода по искусственному адресу возврата и ограничения числа шагов.
    for steps in range(1000000):
        if sim.registers[PC] == 0x3FFF:
            return bytes(memory[0x4000:0x5B00]), steps
        if sim.registers[PC] < 0x4000:
            raise ValueError("Неожиданный выход распаковщика в ПЗУ")
        sim.run()
    raise ValueError("Распаковщик превысил предел числа инструкций")


def bitmap(screen):
    image = Image.new("RGB", (256, 192))
    colors = [(0,0,0), (0,0,205), (205,0,0), (205,0,205),
              (0,205,0), (0,205,205), (205,205,0), (205,205,205)]
    # Преобразование адресации пикселей и атрибутов Spectrum в статический кадр.
    for y in range(192):
        address = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
        for column in range(32):
            value = screen[address+column]
            attribute = screen[6144+(y//8)*32+column]
            ink, paper = attribute & 7, (attribute >> 3) & 7
            palette = [tuple(255 if c else 0 for c in rgb) for rgb in colors] if attribute & 64 else colors
            for bit in range(8):
                image.putpixel((column*8+bit, y), palette[ink if value & (128 >> bit) else paper])
    return image


def station_to_native(data):
    screen = bytearray(data)
    # Преобразование формата #9D58..#9D75, восемь строк знакоместа хранятся подряд.
    for cell in range(768):
        column, cell_row = cell % 32, cell // 32
        for row in range(8):
            y = cell_row * 8 + row
            address = ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | column
            screen[address] = data[cell * 8 + row]
    return bytes(screen)


def main():
    records = json.loads((ROOT / "Tools/Disasm/Reports/Screens.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entries = {e["slot"]:e for e in manifest["entries"]}
    report = []
    target = ROOT / "Tools/Disasm/Research/DecodedScreens"
    pictures = ROOT / "Docs/Images/Screens"
    target.mkdir(parents=True, exist_ok=True)
    pictures.mkdir(parents=True, exist_ok=True)
    for record in records:
        slot, index = record["slot"], record["index"]
        raw = (ROOT / (entries[slot]["path"]+".sectors.bin")).read_bytes()
        packed = raw[record["offset"]:record["offset"]+record["packed_size"]]
        screen, steps = unpack(packed)
        name = f"{slot:02d}_{index:02d}"
        (target / (name+".scr")).write_bytes(screen)
        native = station_to_native(screen) if slot == 9 else screen
        bitmap(native).resize((512,384), Image.Resampling.NEAREST).save(pictures / (name+".png"))
        report.append(dict(slot=slot, index=index, instruction_steps=steps,
                           sha256=hashlib.sha256(screen).hexdigest(),
                           method="original_9EFF_in_isolated_skoolkit", flash_phase=0,
                           layout="cell8_then_attributes" if slot == 9 else "spectrum_screen",
                           path=f"Docs/Images/Screens/{name}.png"))
        print(name, steps, "instructions")
    # Сохранение отдельных несжатых экранов выбора из исходного каталога.
    for slot in (31, 32):
        screen = (ROOT / (entries[slot]["path"]+".bin")).read_bytes()
        if len(screen) != 6912:
            raise ValueError("Неверная длина несжатого экрана")
        bitmap(screen).resize((512,384), Image.Resampling.NEAREST).save(pictures / f"{slot:02d}.png")
    (ROOT / "Tools/Disasm/Reports/DecodedScreens.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
