"""Исполняет архивную цепочку перехода от копировщика до первого повреждённого вызова."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckControlsTemporaryModule import RecordedBanks
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from PackedResourceCodec import decode


def shifted_unpack(sp, target):
    start, end = 0xAC07, 0xAD28
    raw = bytearray(sp[start - 0x6000:end - 0x6000])
    operands = (0x34, 0x43, 0x4F, 0x71, 0x88, 0xC2, 0xCA, 0xFA)
    current_start = 0xAB23
    current = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    normalized = bytearray(raw)
    for offset in operands:
        address = int.from_bytes(raw[offset:offset + 2], 'little')
        assert address in (0xAD1C, 0xAC43) and raw[offset - 1] in (0xC3, 0xCD)
        raw[offset:offset + 2] = (address + target - start).to_bytes(2, 'little')
        normalized[offset:offset + 2] = (address + current_start - start).to_bytes(2, 'little')
    assert normalized == current[current_start - 0x6000:current_start - 0x6000 + len(raw)]
    return raw, operands


def initial_state(sp, control, control0, three_d):
    banks = [bytearray(0x4000) for _ in range(8)]
    memory = RecordedBanks(banks=banks, out7ffd=0x10)
    put(memory, 0x6000, sp[:0x6000])
    put(memory, 0xC000, three_d)
    memory.out7ffd(0x11)
    put(memory, 0xC000, control0)
    put(memory, 0xE193, control[:0x138])
    unpack, offsets = shifted_unpack(sp, 0xAC0A)
    put(memory, 0xAC0A, unpack)
    return memory, offsets


def check_writers(simulator, memory, disk):
    matches = [disk[index:index + 16] for index in range(0, 2048, 16)
               if disk[index:index + 9] == b'CONTROL0C']
    assert len(matches) == 1
    entry = matches[0]
    sector, track, count = entry[14] + 1, entry[15], entry[13]
    assert bytes(memory[0x60AA:0x60B0]) == bytes.fromhex('22 1D 5E 32 20 5E')
    simulator.registers[:] = get_registers(
        {'PC': 0x60AA, 'HL': sector | (track << 8), 'AF': count << 8, 'SP': 0x5FF0}, None, False)
    simulator.run()
    simulator.run()
    assert simulator.registers[PC] == 0x60B0
    assert bytes(memory[0x5E1D:0x5E1F]) == bytes((sector, track))
    assert memory[0x5E20] == count
    assert bytes(memory.banks[1][0x2193 + 0x7C:0x2193 + 0x81]) == bytes.fromhex('11 00 00 06 00')
    return dict(sector=sector, track=track, sector_count=count)


def execute(sp, control, control0, three_d, effect, effect_tail, disk):
    memory, operands = initial_state(sp, control, control0, three_d)
    cpu = Simulator(memory, config={'fast_ldir': True, 'fast_djnz': True})
    trace = PortTrace(cpu)
    cpu.set_tracer(trace)
    written = check_writers(cpu, memory, disk)
    put(memory, 0x5FF0, b'\xFD\x3F')
    cpu.registers[:] = get_registers({'PC': 0x72C2, 'SP': 0x5FF0, 'IX': 0x1234}, None, False)
    core = bytes(memory[0x6000:0x8000])
    expected_effect = decode(effect, effect_tail)['data']
    original_clear = bytes(memory.banks[0][0x110A:0x1112])
    assert original_clear == bytes.fromhex('ED 73 29 D1 31 00 8C 21')
    frames = 0
    checkpoints = []
    for steps in range(8_000_000):
        pc = cpu.registers[PC]
        if pc == 0x5DA0:
            assert cpu.registers[SP] == 0x5FF0
            assert bytes(memory[0x5DA0:0x5ED8]) == control[:0x138]
            assert bytes(memory[0x5E1C:0x5E21]) == bytes.fromhex('11 00 00 06 00')
            checkpoints.append(pc)
        if pc == 0x6500:
            assert bytes(memory[0x6400:0x6400 + len(expected_effect)]) == expected_effect
            assert bytes(memory.banks[1][0x2000:]) == core
            assert cpu.registers[SP] == 0x5FFE and bytes(memory[0x5FFE:0x6000]) == b'\xEB\x5D'
            checkpoints.append(pc)
        if pc == 0x652A:
            assert memory.o7ffd == 0x10 and bytes(memory[0xD10A:0xD112]) == original_clear
        if pc == 0x652D:
            assert memory.o7ffd == 0x10 and bytes(memory[0xC000:0x10000]) == bytes(0x4000)
            checkpoints.append(pc)
        if pc == 0x6568:
            assert memory.o7ffd == 0x11 and bytes(memory[0xC000:0x10000]) == bytes(0x4000)
            checkpoints.append(pc)
        if pc == 0x6586:
            frames += 1
        if pc == 0x5DEB:
            assert frames == 300 and cpu.registers[SP] == 0x6000
            assert bytes(memory.banks[1][0x2000:]) != core
            assert bytes(memory.banks[0][0x110A:0x1112]) != original_clear
            checkpoints.append(pc)
        if pc == 0xD10A:
            assert cpu.registers[SP] == 0x5FFE and memory.o7ffd == 0x10
            assert bytes(memory[0x5FFE:0x6000]) == b'\x08\x5E'
            checkpoints.append(pc)
            break
        cpu.run()
    else:
        raise AssertionError((frames, hex(cpu.registers[PC]), cpu.registers[SP]))
    assert checkpoints == [0x5DA0, 0x6500, 0x652D, 0x6568, 0x5DEB, 0xD10A]
    changed_clear = bytes(memory[0xD10A:0xD112])
    assert changed_clear == bytes.fromhex('8B 8B 8A 8A 89 89 8D 28'), changed_clear.hex()
    cpu.run()
    assert cpu.registers[PC] == 0xD10B
    return dict(archive_writer_values=written, copy_entry=0x72C2, copy_destination=0x5DA0,
                old_disk_operands_overwritten_by_copy=True, unpack_absolute_operands_shifted=len(operands),
                unpacked_bytes=len(expected_effect), effect_frames=frames, effect_return=0x5DEB,
                bank0_clear_ldir=0x652B, bank1_clear_ldir=0x6566,
                changed_clear_entry=0xD10A, original_clear_bytes=original_clear.hex(),
                changed_clear_bytes=changed_clear.hex(), first_changed_opcode_executed=changed_clear[0],
                calls_after_effect_reaching_original_clear=False, disk_reload_executed=False,
                checkpoints=checkpoints, simulator_steps=steps,
                paging_at_effect_return=0x11, paging_at_changed_clear_entry=0x10,
                port_writes_through_changed_entry=len(trace.writes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
        sp_disk = archive.read('awk5.trd')
    base, sp, _ = read_entry(sp_disk, b'SP      C')
    _, control, _ = read_entry(disk, b'CONTROL C')
    _, control0, _ = read_entry(disk, b'CONTROL0C')
    _, three_d, _ = read_entry(disk, b'3DPART  C')
    _, effect, effect_tail = read_entry(disk, b'EFF     c')
    _, startup, _ = read_entry(disk, b'LOADI2  a')
    assert b'(TS_CON+1),\x05\x8c\r' in startup and b'(SL_CON+1),\x05~\r' in startup
    assert b'\x054 RRFILE\r' in startup and b'\x05g\x06\x83"CONTROL0C"\r' in startup
    assert base == 0x6000 and sp[0x12C2:0x12CF] == bytes.fromhex('21 93 E1 11 A0 5D D5 01 38 01 ED B0 C9')
    assert effect == control0[0x600:0xB35]
    report = dict(passed=True, archive_sha256=digest, archive_copy_machine='awk5.trd:SP.C',
                  archive_wrapper='awk1.trd:CONTROL.C', archive_disk_writer='awk1.trd:LOADI2.a',
                  archive_hybrid_bank_placement=True, full_historical_chain_proved=False,
                  current_game_caller_proved=False, assembly_executed=False, native_execution=False,
                  **execute(sp, control, control0, three_d, effect, effect_tail, disk))
    path = ROOT / 'Tools/Disasm/Reports/ControlsArchivedHyperChainVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
