"""Проверка условной копии CONTROL с реальным банком после запуска ACTION."""
import json

from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import payload, run_to
from PackedResourceCodec import decode
from TraceFlight import B, D, H, PC, SP, ROOT, Simulator, main as trace
from skoolkit.pagingtracer import SliceableMemory


COPY_BASE = 0x5DA0
LENGTH_WORD = COPY_BASE + 0x23
COPY_LOOP = COPY_BASE + 0x2A


def word(registers, index):
    return registers[index] * 256 + registers[index + 1]


def restore_cpu(memory, bank_snapshot, register_snapshot, length):
    for destination, saved in zip(memory.banks, bank_snapshot):
        destination[:] = saved
    memory.out7ffd(0x11)
    template = payload(23)[:127]
    assert bytes(memory[0xDADE:0xDB5D]) == template
    put(memory, COPY_BASE, template)
    assert memory[LENGTH_WORD:LENGTH_WORD + 2] == [0, 0]
    if length:
        put(memory, LENGTH_WORD, length.to_bytes(2, 'little'))
    cpu = Simulator(memory)
    cpu.registers[:] = register_snapshot
    cpu.registers[PC], cpu.registers[SP] = COPY_BASE, 0x5FF0
    tracer = PortTrace(cpu)
    cpu.set_tracer(tracer)
    return cpu, tracer


def inspect_zero_length(cpu):
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, COPY_LOOP)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0xC600, 0x8000, 0)
    assert bytes(memory[COPY_LOOP:COPY_LOOP + 2]) == bytes.fromhex('ED B0')
    first_overwrite = (COPY_LOOP - 0x8000) & 65535
    assert first_overwrite == 0xDDCA
    for iteration in range(first_overwrite + 1):
        assert registers[PC] == COPY_LOOP and memory[COPY_LOOP] == 0xED
        if iteration == 0x2B23:
            assert (word(registers, H), word(registers, D)) == (0xF123, 0xAB23)
            unpack_opcode = memory[0xF123]
            assert memory[0xAB23] == 0xD5 and unpack_opcode == 0xC0
        cpu.run()
    assert memory[0xAB23] == unpack_opcode
    assert registers[PC] == COPY_LOOP and memory[COPY_LOOP:COPY_LOOP + 2] == [0x3E, 0xB0]
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0xA3CB, 0x5DCB, 0x2235)
    return dict(copied_before_self_overwrite=first_overwrite + 1, next_pc=registers[PC],
                next_instruction='LD A,#B0', unpacker_entry_opcode_after_copy=unpack_opcode,
                ldir_count_remaining=word(registers, B))


def inspect_zero_continuation(cpu):
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, 0x5DD5)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0x6000, 0xE000, 0x2000)
    backup = bytes(memory[0x6000:0x8000])
    run_to(cpu, 0x5DD7)
    assert bytes(memory[0xE000:0x10000]) == backup
    run_to(cpu, 0x5DDD)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0x8000, 0x6400, 0)
    third_copy_count = ((0x5DDD - 0x6400) & 65535) + 1
    for _ in range(third_copy_count):
        assert registers[PC] == 0x5DDD and memory[0x5DDD] == 0xED
        cpu.run()
    assert third_copy_count == 63966
    assert registers[PC] == 0x5DDD and bytes(memory[0x5DDD:0x5DDF]) == b'\xDD\xB0'
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0x79DE, 0x5DDE, 0x0622)
    for pc in (0x5DDD, 0x5DDE, 0x5DDF, 0x5DE0, 0x5DE1, 0x5DE2):
        assert registers[PC] == pc
        cpu.run()
    assert registers[PC] == 0xAB23 and registers[SP] == 0x5FEC
    assert bytes(memory[0xAB23:0xAB30]) == bytes.fromhex('77 21 89 5c be 38 03 34 06 18 cd 00 0e')
    for pc in (0xAB23, 0xAB24, 0xAB27, 0xAB28, 0xAB2A, 0xAB2B, 0xAB2D):
        assert registers[PC] == pc
        cpu.run()
    assert registers[PC] == 0x0E00 and registers[SP] == 0x5FEA
    assert bytes(memory[0x5FEA:0x5FEE]) == bytes.fromhex('30 AB E5 5D')
    return dict(backup_copy_bytes=8192, third_copy_before_self_overwrite=third_copy_count,
                third_copy_new_instruction='DD-prefixed OR B', third_copy_count_remaining=0x0622,
                original_unpacker_entry_reached_with_replaced_code=True,
                reached_rom=0x0E00, reached_temporary_entry=False, stopped_before_rom_execution=True)


def inspect_font_match(cpu, font):
    memory, registers = cpu.memory, cpu.registers
    run_to(cpu, 0xAB23)
    assert (word(registers, H), word(registers, D)) == (0x6400, 0x6400)
    assert bytes(memory[0x6400:0x6800]) == font
    run_to(cpu, 0xABC0)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0x6400, 0x6404, 1)
    cpu.run()
    run_to(cpu, 0xABC0)
    assert (word(registers, H), word(registers, D), word(registers, B)) == (0x624F, 0x6406, 2)
    assert bytes(memory[0x6400:0x6406]) == bytes.fromhex('86 EC 28 EA 86 84')
    actual = bytes(memory[0x624F:0x6251])
    cpu.run()
    cpu.run()
    assert registers[PC] == 0xABC2 and bytes(memory[0x6406:0x6408]) == actual
    return dict(invalid_reference=0x624F, destination=0x6406, length=2,
                copied_bytes=actual.hex(), source_outside_output_history=True)


def main():
    control = payload(22)
    raw = control[0x600:0xA00]
    assert raw[:6] == bytes.fromhex('04 04 04 04 00 04')
    # Сигнатура нормализуется только для независимого декодера, Z80 её не читает.
    try:
        decode(b'HR' + raw[2:], control[0xA00:0xA02])
    except AssertionError as error:
        assert error.args == (('bad_reference', -433, 2, 6, 1028),)
    else:
        raise AssertionError('Декодер принял ссылку до начала результата')
    cases = []
    for frames in (2, 9, 65):
        memory = SliceableMemory(out7ffd=0x10)
        put(memory, 0x6000, payload(17))
        cpu = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A})
        flight = trace(['--frames', str(frames)], boot_simulator=cpu, save_reports=False)
        assert flight['reason'] == 'requested_frame_entries'
        assert bytes(memory.banks[1][0x600:0xA00]) == raw
        bank_snapshot = [bank.copy() for bank in memory.banks]
        register_snapshot = cpu.registers[:]
        original, ports = restore_cpu(memory, bank_snapshot, register_snapshot, 0)
        zero = inspect_zero_length(original)
        zero.update(inspect_zero_continuation(original))
        assert ports.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
        conditional, ports = restore_cpu(memory, bank_snapshot, register_snapshot, len(raw))
        nonzero = inspect_font_match(conditional, raw)
        assert ports.writes == [(0x7FFD, 0x16), (0x7FFD, 0x11)]
        cases.append(dict(frame_entries=frames, zero_length=zero, length_from_font_header=nonzero))
    result = dict(passed=True, cases=cases, template_copy_base=COPY_BASE, relocation_is_fixture=True,
                  trdos_substituted_during_flight_start=True, native_execution=False,
                  actual_game_caller_proved=False, assembly_executed=False)
    path = ROOT / 'Tools/Disasm/Reports/TemporaryModuleLiveSourceVerification.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('3 профиля ACTION, два самоперезаписанных LDIR и вход ROM при нуле, недопустимая ссылка при длине 0400')


if __name__ == '__main__':
    main()
