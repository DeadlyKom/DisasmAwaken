"""Договор внешнего callback закрытия, синтетический callback явно изменяет регистры, без HALT."""

from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Tools/Disasm/Research/vendor/skoolkit-10.1"))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, B, C, D, E, H, L, PC, SP


def main():
    manifest = json.loads((ROOT / "Tools/Disasm/Disk/Manifest.json").read_text(encoding="utf-8"))
    item = next(e for e in manifest["entries"] if e["slot"] == 4)
    source = (ROOT / (item["path"]+".sectors.bin")).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    simulator = Simulator(memory)
    initial = get_registers({"SP": 0x7FFE, "HL": 0x1357, "DE": 0x247A, "BC": 0x36C9,
                             "IX": 0x2468, "IY": 0x5C3A, "^HL": 0x369C,
                             "^DE": 0x47AD, "^BC": 0x58BE, "^AF": 0x69CF}, None, False)
    # Синтетический callback меняет основные, альтернативные и индексные регистры, сохраняя договор возврата по стеку.
    prefix = bytes.fromhex("01efbe11efcddd215634fd216745d921ab8911bc9a01cdabd9083ebcb708")
    postfix = bytes.fromhex("e5f1213412c9")
    memory[0x9CA6:0x9CA8] = [0, 0xE0]
    for value in range(65536):
        key = 45 if value & 1 else 0
        record = 0xF0FD+16*key
        memory[record+4] = 0x10
        memory[0x7001:0x7003] = list(key.to_bytes(2, "little"))
        memory[0xE000:0xE084] = [0x55]*132
        memory[0xE000:0xE004] = [0, 0x70, 1, 1]
        memory[0x9E78] = 1+value % 255
        memory[0x9E7E:0x9E80] = list(key.to_bytes(2, "little"))
        memory[0x9E8B:0x9E8D] = [0, 0x50]
        program = prefix+b"\x21"+value.to_bytes(2, "little")+postfix
        memory[0x5000:0x5000+len(program)] = program
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.run(start=0x9E77, stop=0x5000)
        # Проверка момента вызова, активность сброшена, прежний callback пока остаётся установленным.
        if (memory[0x9E78], memory[0x9E8B:0x9E8D], simulator.registers[H]*256+simulator.registers[L],
                simulator.registers[D]*256+simulator.registers[E], simulator.registers[A], simulator.registers[F]) != (
                0, [0, 0x50], 0x7000, key, 0, 0x44):
            raise ValueError("Не совпал контекст входа callback закрытия")
        simulator.run(stop=0x3FFF)
        result_a, callback_f = value >> 8, value & 255
        expected_f = (callback_f & 0xC4) | (result_a & 0x28) | 1
        if (simulator.registers[A], simulator.registers[F], simulator.registers[H]*256+simulator.registers[L],
                simulator.registers[D]*256+simulator.registers[E], simulator.registers[B]*256+simulator.registers[C],
                simulator.registers[SP]) != (result_a, expected_f, 0x1357, 0x247A, 0xBEEF, 0x8000):
            raise ValueError("Закрытие не сохранило HL,DE либо неверно перенесло AF,BC callback")
        expected = get_registers({"IX": 0x3456, "IY": 0x4567, "^HL": 0x89AB,
                                  "^DE": 0x9ABC, "^BC": 0xABCD, "^AF": 0xBCA8}, None, False)
        for reg in (*range(8, 12), *range(16, 24)):
            if simulator.registers[reg] != expected[reg]:
                raise ValueError("Закрытие неожиданно восстановило регистр внешнего callback")
        if memory[0x9E8B:0x9E8D] != [0x58, 0x9A] or memory[0x9E78] != 0:
            raise ValueError("Не сброшен адрес callback после возврата")
    # Проверка неактивного входа с произвольными прежними флагами, callback не должен вызываться.
    for flags in range(256):
        memory[0x9E78] = 0
        memory[0x9E8B:0x9E8D] = [0, 0x50]
        memory[0x7FFE:0x8000] = [0xFF, 0x3F]
        simulator.registers[:] = initial
        simulator.registers[A], simulator.registers[F] = flags ^ 0xA5, flags
        simulator.run(start=0x9E77, stop=0x3FFF)
        if (simulator.registers[A], simulator.registers[F], simulator.registers[SP]) != (0, 0x54, 0x8000):
            raise ValueError("Не совпал неактивный вход закрытия")
        if memory[0x9E8B:0x9E8D] != [0, 0x50]:
            raise ValueError("Неактивный вход сбросил callback")
        for reg in (*range(2, 12), *range(16, 24)):
            if simulator.registers[reg] != initial[reg]:
                raise ValueError("Неактивный вход изменил сохраняемый регистр")
    report = dict(passed=True, method="original_close_callback_protocol_with_explicit_synthetic_register_clobber",
                  callback_af_cases=65536, inactive_cases=256, toggle_suppressed_by_bit4=True,
                  source_sha256=hashlib.sha256(source).hexdigest(), external_callback_is_fixture=True,
                  irq_enabled=False, native_execution_verified=False, assembly_executed=False)
    (ROOT / "Tools/Disasm/Reports/CloseCallbackVerification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
