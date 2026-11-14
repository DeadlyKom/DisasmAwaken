"""Портовый и RAM-эффект второй клавиатурной ветви ROM 128K в шумовых кадрах."""
from itertools import product
import json
from pathlib import Path

from CheckActionNoiseExit import COPY_SEED, PC, ROM48, ROM128, put, run_to
from CheckActionNoiseLetterCase import FLAG, LetterA, boot_noise, run_seeded_frame
from CheckIntro import ROOT


WORKSPACE = 0x5B88
ROM_ENTRIES = (0x3A42, 0x39A0, 0x3938, 0x02BF, 0x035A)


class AuxKeyboard(LetterA):
    def __init__(self, cpu, keyboard_frame, ay_input, exit_frame=100):
        super().__init__(cpu, keyboard_frame)
        self.exit_frame = exit_frame
        self.keys = iter([255] * (exit_frame - 1) + [254])
        self.ay_input = ay_input
        self.rom_ports = []

    def write_port(self, registers, port, value, offset):
        if registers[PC] < 0x4000:
            self.rom_ports.append(('write', registers[PC], port, value))
        super().write_port(registers, port, value, offset)

    def read_port(self, registers, port):
        if port == 0xFFFD and registers[PC] < 0x4000:
            value = self.ay_input if self.outfffd == 14 else self.ay[self.outfffd]
            self.rom_ports.append(('read', registers[PC], port, value))
            return value
        return super().read_port(registers, port)


def advance_flag(cpu, words, wraps):
    iy, _ = run_seeded_frame(cpu, words, 0x06, 0x5C3A)
    for index in range(wraps):
        seed = 0x5A if index == wraps - 1 else 0x06
        iy, increment = run_seeded_frame(cpu, words, seed, iy, wrap=True)
        assert increment == dict(address=FLAG, old=index, new=index + 1, bank0=True)
    assert iy == 0xFD7B and cpu.memory[FLAG] == wraps
    return iy


def check_timeout(cpu, words):
    memory = cpu.memory
    ports = AuxKeyboard(cpu, 0, 0xFF, exit_frame=201)
    cpu.set_tracer(ports)
    iy = advance_flag(cpu, words, 16)
    countdown = []
    for frame in range(1, 155):
        run_to(cpu, COPY_SEED)
        ports.rom_ports.clear()
        iy, increment = run_seeded_frame(cpu, words, 0x5A, iy)
        assert increment is None and memory[FLAG] == 0x10
        if frame % 2:
            assert not ports.rom_ports
        else:
            countdown.append(tuple(memory[WORKSPACE:WORKSPACE + 3]))
        if frame < 154:
            assert not any(kind == 'write' and port == 0xBFFD for kind, _, port, _ in ports.rom_ports)
    assert countdown == [(1, delay, 0) for delay in range(0x4C, 0, -1)] + [(0, 0, 0)]
    latch_writes = [value for kind, _, port, value in ports.rom_ports if kind == 'write' and port == 0xBFFD]
    input_reads = [value for kind, pc, port, value in ports.rom_ports
                   if (kind, pc, port) == ('read', 0x38A4, 0xFFFD)]
    assert latch_writes == [0xFE, 0xFF]
    assert input_reads == [0xFF] * 34
    return dict(frames_after_wrap=154, even_polls=len(countdown), countdown_from=0x4C,
                workspace_cleared=True, latch_writes=latch_writes,
                initial_and_timeout_reads=len(input_reads), timeout_port_trace=ports.rom_ports)


def check_rom(rom_path, extended):
    rom = Path(rom_path).read_bytes()
    cpu = boot_noise(rom)
    memory, registers = cpu.memory, cpu.registers
    initial = registers.copy()
    banks = [bank.copy() for bank in memory.banks]
    words = [int.from_bytes(rom[0x10FE + seed:0x1100 + seed], 'little') for seed in range(256)]
    profiles = []
    def reset():
        memory.watch_tail = False
        for bank, saved in zip(memory.banks, banks):
            bank[:] = saved
        memory.out7ffd(16)
        registers[:] = initial
        put(memory, 0x5C78, bytes(3))
        assert memory[FLAG] == 0

    for wraps, even, ay_input in product((15, 16), (False, True), (0xDF, 0xFF)):
        reset()
        ports = AuxKeyboard(cpu, wraps + 2 + int(even), ay_input)
        cpu.set_tracer(ports)
        iy = advance_flag(cpu, words, wraps)
        if even:
            iy, _ = run_seeded_frame(cpu, words, 0x5A, iy)
        run_to(cpu, COPY_SEED)
        ports.rom_ports.clear()
        before = bytes(memory[WORKSPACE:WORKSPACE + 3])
        visits = []

        def observe(pc):
            if pc in ROM_ENTRIES:
                visits.append(pc)

        run_seeded_frame(cpu, words, 0, iy, observe_irq=observe)
        after = bytes(memory[WORKSPACE:WORKSPACE + 3])
        assert memory[0x5C78] == (2 if even else 1)
        assert memory[FLAG] == wraps | 0x20
        assert (0x3A42 in visits) == (extended and wraps == 16)
        assert (0x39A0 in visits) == (extended and wraps == 16 and even)
        assert visits.count(0x02BF) == 1
        assert memory[0x5C08] == (0x61 if wraps == 15 else 0xE6)
        assert before == bytes(3)
        expected_ports = []
        expected_workspace = bytes(3)
        if extended and wraps == 16 and even:
            expected_ports = [
                ('write', 0x3888, 0xFFFD, 7), ('read', 0x388A, 0xFFFD, 0),
                ('write', 0x388E, 0xFFFD, 14), ('read', 0x3890, 0xFFFD, ay_input),
                ('write', 0x38A2, 0xFFFD, 14), ('read', 0x38A4, 0xFFFD, ay_input),
            ]
            if ay_input == 0xFF:
                expected_workspace = b'\x01\x4C\0'
            else:
                expected_ports.extend((('write', 0x3899, 0xFFFD, 14), ('write', 0x389C, 0xBFFD, 0xFF)))
        assert ports.rom_ports == expected_ports and after == expected_workspace
        profiles.append(dict(wraps=wraps, even=even, ay_input=ay_input, visits=visits,
                             rom_ports=ports.rom_ports[:], workspace_before=before.hex(),
                             workspace_after=after.hex(), key=memory[0x5C08]))
    result = dict(rom=Path(rom_path).name, profiles=profiles)
    if extended:
        reset()
        result['continuous_high_input'] = check_timeout(cpu, words)
    return result


def main():
    profiles = [check_rom(ROM48, False), check_rom(ROM128[1], True)]
    report = dict(passed=True, profiles=profiles, flag_address=FLAG, bank=0,
                  original_rom_irq_executed=True, refresh_and_frames_prepared=True,
                  ay_input_modeled=True, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ActionNoiseAuxKeyboardVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
