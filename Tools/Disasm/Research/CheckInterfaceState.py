"""Проверка объединения четырёх входных байтов и чтения единственного бита контура."""

from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "Tools/Disasm"), str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1")]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, D, E, PC, SP
from CheckGlyphRenderer import and_flags


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    entry = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (entry["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    memory[0x6322:0x7F8C] = source[0x5CE:0x2238]
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    simulator = Simulator(memory)
    observed = {}
    dis = decoder(memory)

    def execute(start, value, key=0):
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[D], simulator.registers[E] = key >> 8, key & 255
        simulator.registers[PC] = start
        while simulator.registers[PC] != 0x3FFF:
            pc = simulator.registers[PC]
            if 0x9E97 <= pc < 0x9EA5 and f"{pc:04X}" not in observed:
                instruction = dis.disassemble(pc, pc+1, "h")[0]
                raw = bytes(memory[pc:pc+len(instruction.bytes)])
                if raw != source[pc-0x6000:pc-0x6000+len(raw)]:
                    raise ValueError("Изменились исходные инструкции чтения бита")
                observed[f"{pc:04X}"] = raw.hex()
            simulator.run()
        expected_flags = and_flags(value) if start == 0x9E97 else and_flags(value) & ~0x10
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (value, expected_flags, 0x8000):
            raise ValueError("Не совпал результат объединения входов либо чтения контура")
        for reg in (*range(2, 12), *range(16, 24)):
            expected = key >> 8 if reg == D else key & 255 if reg == E else initial[reg]
            if simulator.registers[reg] != expected:
                raise ValueError("Изменён сохраняемый регистр")

    # Проверка всех сочетаний каждой пары отдельно, включая потерю старшего бита перед финальным OR.
    action_cases = 0
    for first in range(256):
        for second in range(256):
            for shifted in (False, True):
                values = (first, second, 0, 0) if shifted else (0, 0, first, second)
                for address, value in zip((0x66EC, 0x6585, 0x66ED, 0x658A), values):
                    memory[address] = value
                expected = (((values[0] | values[1]) << 1) | values[2] | values[3]) & 255
                execute(0x9C43, expected)
                action_cases += 1
    generator = random.Random(0x9C43)
    for _ in range(8192):
        values = [generator.randrange(256) for _ in range(4)]
        for address, value in zip((0x66EC, 0x6585, 0x66ED, 0x658A), values):
            memory[address] = value
        execute(0x9C43, (((values[0] | values[1]) << 1) | values[2] | values[3]) & 255)
        action_cases += 1
    # Проверка адресного переполнения на всех индексах, без записи в произвольные области памяти.
    for key in range(65536):
        execute(0x9E97, memory[(0xF101+16*key) & 65535] & 1, key)
    # Проверка всех флаговых байтов в каждой действительной физической записи интерфейса.
    for key in range(46):
        address = 0xF101+16*key
        for flags in range(256):
            memory[address] = flags
            execute(0x9E97, flags & 1, key)
    report = dict(passed=True, method="original_action_merge_and_frame_bit_against_byte_formula",
                  action_cases=action_cases, frame_bit_index_cases=65536, frame_bit_flag_cases=46*256,
                  source_sha256=hashlib.sha256(source).hexdigest(), original_visited=observed,
                  hardware_meaning_of_input_bits_proved=False, irq_enabled=False,
                  native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/InterfaceStateVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "original_visited"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
