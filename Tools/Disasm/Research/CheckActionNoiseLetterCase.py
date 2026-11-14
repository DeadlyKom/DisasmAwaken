"""Чтение дополнительного флага клавиатуры ROM при смещённом IY."""
import json
from pathlib import Path

from CheckActionNoiseExit import (
    COPY_SEED, NOISE_ENTRY, PERIOD, NoiseIrqMemory, NoiseMatrix, ROM48, ROM128,
    R, Simulator, disk_payload, irq_noise_frame, put, run_to, trace_flight,
)
from CheckIntro import ROOT


FLAG = 0xFD7C
TARGET = 0xFDAB


class LetterA(NoiseMatrix):
    def __init__(self, cpu, keyboard_frame):
        super().__init__(cpu, 100)
        self.keyboard_frame = keyboard_frame

    def read_port(self, registers, port):
        if len(self.reads) + 1 == self.keyboard_frame and port == 0xFDFE:
            return 0xFE
        return super().read_port(registers, port)


def boot_noise(rom, memory_type=NoiseIrqMemory):
    memory = memory_type()
    memory.roms = memory.roms[0], list(rom)
    memory.out7ffd(16)
    put(memory, 0x6000, disk_payload(17))
    memory[0x5C00] = memory[0x5C04] = 255
    memory[0x5C3B] = 8
    cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A}, {'im': 1},
                    config={'frame_duration': PERIOD, 'int_active': 36})
    memory.registers = registers = cpu.registers
    flight = trace_flight(['--frames', '2', '--verify-flight-cycle'], boot_simulator=cpu, save_reports=False)
    assert flight['complete_frame_returns'] == 1
    memory[0x6693] = 0x2E
    run_to(cpu, NOISE_ENTRY)
    return cpu


def run_seeded_frame(cpu, words, seed, previous_iy, wrap=False, *, observe_irq=None):
    run_to(cpu, COPY_SEED)
    cpu.registers[R] = (seed & 128) | ((seed - 2) & 127)
    if wrap:
        # Младшее слово ставится перед переполнением, байт флагов меняет сама ROM.
        put(cpu.memory, 0x5C78, b'\xFF\xFF')
    observed, iy, _, increment = irq_noise_frame(cpu, previous_iy, observe_irq=observe_irq)
    assert observed == seed and iy == words[seed]
    return iy, increment


def check_rom(rom_path):
    rom = Path(rom_path).read_bytes()
    cpu = boot_noise(rom)
    memory, registers = cpu.memory, cpu.registers
    initial = registers.copy()
    banks = [bank.copy() for bank in memory.banks]

    assert rom[0x035A:0x035E] == bytes.fromhex('FD CB 30 5E')
    words = [int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little') for seed in range(256)]
    assert (words[0x06], words[0x5A]) == (0xFD3C, 0xFD7B)
    indexed_offsets = (1, 7, 0x30, 0x40)
    addresses = {(iy + offset) & 0xFFFF for iy in (*words, 0x5C3A) for offset in indexed_offsets}
    assert max(addresses) == 0xFF7E
    assert {(iy + 1) & 0xFFFF for iy in words if iy + 0x30 >= 0xF866} & {
        (iy + 0x40) & 0xFFFF for iy in words
    } == {FLAG}

    profiles = []
    for wraps, target_bit in ((7, 0), (8, 0), (8, 8)):
        memory.watch_tail = False
        for bank, saved in zip(memory.banks, banks):
            bank[:] = saved
        memory.out7ffd(16)
        registers[:] = initial
        put(memory, 0x5C78, bytes(3))
        ports = LetterA(cpu, wraps + 2)
        cpu.set_tracer(ports)
        assert memory[FLAG] == memory[TARGET] == 0
        memory[TARGET] = target_bit
        memory.watch_tail = True
        memory.tail_accesses.clear()
        iy, increment = run_seeded_frame(cpu, words, 0x06, 0x5C3A)
        assert increment is None
        for index in range(wraps):
            iy, increment = run_seeded_frame(cpu, words, 0x5A if index == wraps - 1 else 0x06, iy, wrap=True)
            assert increment == dict(address=FLAG, old=index, new=index + 1, bank0=True)
        assert iy == 0xFD7B
        flag_writes = [value for mode, pc, address, value in memory.tail_accesses
                       if (mode, pc, address) == ('write', 0x0045, FLAG)]
        assert flag_writes == list(range(1, wraps + 1))
        memory.tail_accesses.clear()
        _, increment = run_seeded_frame(cpu, words, 0, iy)
        assert increment is None
        reads = [row for row in memory.tail_accesses if row[2] == TARGET]
        assert reads == ([('read', 0x035A, TARGET, target_bit)] if wraps == 8 else [])
        assert ('write', 0x030B, FLAG, wraps | 0x20) in memory.tail_accesses
        run_to(cpu, COPY_SEED)
        assert ports.reads == [255] * (wraps + 2)
        profiles.append(dict(rom_frame_increments=flag_writes, test_byte=target_bit,
                             test_accesses=reads, key_value=memory[0x5C08]))
    assert [row['key_value'] for row in profiles] == [0xE6, 0x61, 0x41], profiles
    return dict(rom=Path(rom_path).name, profiles=profiles, all_256_noise_seeds_enumerated=True,
                max_effective_indexed_address=max(addresses), effective_offsets=indexed_offsets)


def main():
    profiles = [check_rom(path) for path in (ROM48, ROM128[1])]
    report = dict(passed=True, profiles=profiles, target=TARGET, read_pc=0x035A,
                  flag=FLAG, bank=0, refresh_and_frames_prepared=True, flag_value_from_original_rom=True,
                  action_initialization_trdos_substituted=True, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseLetterCaseVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
