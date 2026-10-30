"""Проверка всех байтовых размеров переключения геометрии и условного продолжения действия."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1")]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, PC, SP, IXh, IXl
from CheckGlyphRenderer import and_flags
from CheckStationSpans import subtract_flags


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    dis = decoder(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    memory[0x9CA6:0x9CA8] = [0, 0xE0]
    observed = {}
    cases = restored = expanded = 0
    for key in (0, 45):
        record = 0xF0FD+16*key
        memory[0x7001:0x7003] = list(key.to_bytes(2, "little"))
        for width in range(256):
            for height in range(256):
                saved = [(3*width+height) & 255, (width+5*height) & 255,
                         (width ^ height) & 255, (width+height) & 255]
                original = [0xFD, 0xFE, width, height, 0xAB, 0xCD, 0x12, 0x34, *saved, 0, 0x70, 0x56, 0x78]
                memory[record:record+16] = original
                memory[0xE000:0xE084] = [0x55]*132
                memory[0xE000:0xE004] = [0, 0x70, 1, 1]
                memory[0x9A82] = 0xA5
                memory[0x9B16] = 0x5A
                memory[0x7FFE:0x8000] = [0xFF, 0x3F]
                simulator.registers[:] = initial
                simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
                simulator.registers[PC] = 0xCC30
                if width >= 16 or height >= 8:
                    expected_geometry = saved
                    result_a = saved[3]
                    compare = subtract_flags(width, 16) if width >= 16 else subtract_flags(height, 8)
                    result_f = (compare & 0xC4) | (result_a & 0x28) | 1
                    restored += 1
                else:
                    expected_geometry = [6, 4, 20, 10]
                    result_a, result_f = height, 0x81
                    expanded += 1
                while simulator.registers[PC] != 0x3FFF:
                    pc = simulator.registers[PC]
                    if 0xCC30 <= pc < 0xCC81 and f"{pc:04X}" not in observed:
                        instruction = dis.disassemble(pc, pc+1, "h")[0]
                        raw = bytes(memory[pc:pc+len(instruction.bytes)])
                        if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                            raise ValueError("Изменились инструкции переключения геометрии")
                        observed[f"{pc:04X}"] = raw.hex()
                    simulator.run()
                if (memory[record:record+16] != expected_geometry+original[4:] or memory[0x9A82] != 0
                        or memory[0x9B16] != 0x5A or memory[0xE000:0xE004] != [0, 0x70, 1, 1]):
                    raise ValueError("Не совпала геометрия либо изменены соседние поля и состояние указателя")
                if (simulator.registers[A], simulator.registers[F], simulator.registers[H]*256+simulator.registers[L],
                        simulator.registers[D]*256+simulator.registers[E], simulator.registers[IXh]*256+simulator.registers[IXl],
                        simulator.registers[SP]) != (result_a, result_f, key, key, record, 0x8000):
                    raise ValueError(f"Не совпал выход переключения {width}/{height}/{key}")
                for reg in (*range(2, 4), *range(10, 12), *range(16, 24)):
                    if simulator.registers[reg] != initial[reg]:
                        raise ValueError("Изменён сохраняемый регистр геометрии")
                cases += 1
    # Проверка продолжения до выбора следующего входа, хвосты уже проверяются отдельными полными моделями.
    for af in range(65536):
        value, flags = af >> 8, af & 255
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = value, flags
        simulator.registers[PC] = 0xCC2C
        while simulator.registers[PC] not in (0x3FFF, 0xCC30, 0xCC81):
            pc = simulator.registers[PC]
            if f"{pc:04X}" not in observed:
                instruction = dis.disassemble(pc, pc+1, "h")[0]
                raw = bytes(memory[pc:pc+len(instruction.bytes)])
                if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                    raise ValueError("Изменились инструкции условного продолжения")
                observed[f"{pc:04X}"] = raw.hex()
            simulator.run()
        target = 0x3FFF if flags & 1 else 0xCC81 if value else 0xCC30
        result_f = flags if flags & 1 else and_flags(value)
        expected_sp = 0x8000 if flags & 1 else 0x7FFE
        if (simulator.registers[PC], simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (
                target, value, result_f, expected_sp):
            raise ValueError("Продолжение выбрало неверный выход")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Развилка изменила сохраняемый регистр")
    report = dict(passed=True, method="original_bounds_toggle_all_byte_dimensions_and_action_tail_all_af",
                  geometry_cases=cases, restored=restored, expanded=expanded, action_tail_cases=65536,
                  source_sha256=hashlib.sha256(source).hexdigest(), original_visited=observed,
                  draw_or_pointer_calls_executed=False, irq_enabled=False,
                  native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/BoundsToggleVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
