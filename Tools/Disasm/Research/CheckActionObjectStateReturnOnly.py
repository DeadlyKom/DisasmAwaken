"""Сверяет авторский NTH и проверяет исходный RET отдельно от диспетчера."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import put


def compare_archive(archive_path, current):
    archive_digest = sha256(archive_path.read_bytes()).hexdigest()
    assert archive_digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        _, source, _ = read_entry(archive.read('awk1.trd'), b'BRAINPROa')
        origin, old, _ = read_entry(archive.read('awk5.trd'), b'SP      C')
    assert origin == 0x6000
    lines = source.split(b'\r')
    table = lines.index(b'ITAB')
    words = [re.fullmatch(rb'\x06\x8c\x05h\x06\x83([A-Z0-9_]+)', line)
             for line in lines[table + 1:table + 23]]
    assert all(words)
    assert [match[1] for match in words[-2:]] == [b'OBLET', b'WOZWRAT']
    assert lines[table + 23:table + 25] == [b'NTH', b'\x06\x8c\x05$']
    assert b'\rOBLET\r' in source
    assert old[0x8F8D] == current[0xEF7C] == 0xC9
    # Сверка хвоста ITAB и тела OBLET с учётом переноса целей.
    assert old[0x8F89:0x8F8D] == bytes.fromhex('8E EF AB EF')
    assert bytes(current[0xEF78:0xEF7C]) == bytes.fromhex('7D EF 9A EF')
    assert old[0x8F8D:0x8F9E] == bytes(current[0xEF7C:0xEF8D])
    assert old[0x8F9E:0x8FA0] == b'\x01\xF1' and bytes(current[0xEF8D:0xEF8F]) == b'\xF8\xF0'
    assert old[0x8FA0:0x8FA9] == bytes(current[0xEF8F:0xEF98])
    assert b'\x7C\xEF' not in bytes(current[0x6000:])
    return archive_digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    flat = flat_action()
    archive_digest = compare_archive(args.archive, flat)
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = flat[start:start + 0x4000]
    memory = RecordedBanks(banks=banks, out7ffd=0x10)
    sim = Simulator(memory)
    for value in range(256):
        stack = (0x5F00, 0xBFFE)[value & 1]
        continuation = value * 257 ^ 0x3865
        memory.recording = False
        put(memory, stack, continuation.to_bytes(2, 'little'))
        initial = get_registers({'PC': 0xEF7C, 'SP': stack, 'R': value, 'AF': 0x5A00 | value,
                                 'HL': 0x1357, 'DE': 0x2468, 'BC': 0x369C,
                                 '^AF': 0x48D7, '^HL': 0x59AD, '^DE': 0x6ABE, '^BC': 0x7BCF,
                                 'IX': 0xA100, 'IY': 0x5C3A}, None, False)
        sim.registers[:] = initial
        memory.recording = True
        memory.writes = []
        sim.run()
        expected = initial.copy()
        expected[PC], expected[SP] = continuation, stack + 2
        expected[15] = (value & 128) | ((value + 1) & 127)
        assert all(sim.registers[i] == expected[i] for i in range(len(expected)) if i != 25)
        assert not memory.writes
    for state in (0x16, 0x96):
        memory.recording = False
        memory[0xA10A] = state
        sim.registers[:] = get_registers({'PC': 0xF843, 'SP': 0x5FFE, 'IX': 0xA100}, None, False)
        for _ in range(16):
            sim.run()
            if sim.registers[PC] == 0xDDC9:
                break
        else:
            raise AssertionError(('чтение за ITAB', state, hex(sim.registers[PC])))
    report = dict(passed=True, total_cases=258, direct_ret_profiles=256, out_of_table_profiles=2,
                  archive_sha256=archive_digest, authored_label='BRAINPRO.a:NTH',
                  archived_sp_address=0xEF8D, awaken_action_address=0xEF7C,
                  out_of_table_target=0xDDC9, original_game_path_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ActionObjectStateReturnOnlyVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
