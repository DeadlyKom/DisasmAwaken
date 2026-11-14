"""Сверяет исходные объявления STARHSUN с размещением в двух CONTROL0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckMusicGateTicks import Memory


RESOURCES = (
    (0x195B, 0x195F, 'Source/Controls/Resources/ArchivedTxtrPair.bin', 'CONTROL0_AUTHORED_TXTR_PAIR',
     'Две авторские пары нулевых байтов, метка TXTR у второй пары'),
    (0x199C, 0x19B0, 'Source/Controls/Resources/SmallMaskBufferTail.bin', 'CONTROL0_AUTHORED_SMALL_MASK_TAIL',
     'Конец исходного 32-байтового буфера LA8FA после 12 используемых строк'),
)


def check_unfilled_entries(control):
    memory = Memory([0] * 0x10000)
    memory[0xC000:0xC000 + len(control)] = control
    simulator = Simulator(memory)
    cases = 0
    for start, m1 in ((0xD501, 2), (0xD502, 2), (0xD503, 1)):
        for value in range(256):
            stack = (0xBFFE, 0xFFFF)[value & 1]
            memory.recording = False
            memory[stack], memory[(stack + 1) & 0xFFFF] = 0xFE, 0x3F
            initial = get_registers(
                {'HL': 0x1357, 'DE': 0x2468, 'BC': (value << 8) | 0x43, 'AF': 0x5A00 | value,
                 '^HL': 0x369C, '^DE': 0x47AD, '^BC': 0x58BE, '^AF': 0x69CF, 'IX': 0x1234,
                 'IY': 0x5C3A, 'R': value, 'SP': stack, 'PC': start}, None, False)
            expected = list(initial)
            if start == 0xD501:
                expected[2] = 0x7F
            expected[15] = (value & 0x80) | ((value + m1) & 0x7F)
            expected[SP], expected[PC] = (stack + 2) & 0xFFFF, 0x3FFE
            simulator.registers[:] = initial
            memory.writes = []
            memory.recording = True
            for _ in range(m1):
                simulator.run()
            assert not memory.writes
            compared = (*range(13), 14, 15, *range(16, 24), PC, 26, 27)
            assert all(simulator.registers[i] == expected[i] for i in compared), (start, value)
            cases += 1
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        disk = archive.read('awk1.trd')
    _, old, _ = read_entry(disk, b'CONTROL0C')
    _, source, _ = read_entry(disk, b'STARHSUNa')
    origin, current, _ = read_entry((ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes(), b'CONTROL0C')
    assert origin == 0xC000
    shift = 0x535
    # Сохраняемые операнды относительных переходов и точные границы между соседними блоками.
    assert old[0x1940 + shift:0x1955 + shift] == current[0x1940:0x1955]
    assert old[0x1959 + shift:0x195F + shift] == current[0x1959:0x195F]
    assert old[0x1979 + shift:0x19B3 + shift] == current[0x1979:0x19B3]
    assert old[0x19B6 + shift:0x19BB + shift] == current[0x19B6:0x19BB]
    assert old[0x195B + shift:0x195F + shift] == current[0x195B:0x195F] == bytes(4)
    assert old[0x1990 + shift:0x19B0 + shift] == current[0x1990:0x19B0] == bytes(32)
    assert b'\x05g\x06\x83#00,#00\rTXTR\x06\x88\x05g\x06\x83#00,#00\r' in source
    assert b'\rLA8FA\r\x06\x8c\x05i\x06\x83#20\r' in source
    assert source.count(b'TXTR') == 1 and source.count(b'LA8FA') == 4
    assert b'\x03\x8c,LA8FA\r' in source and b'(LA8FA),\x05~\r' in source
    assert b'\x03\x8d,LA8FA\r' in source
    # Исторический вход UNFILLED имеет те же три машинных байта.
    assert b'\xfeUNFILLED\rL89C0\x06\x87\x05 \x06\x83\x03w,#7F\r\x06\x8c\x05$\r' in source
    assert old[0x14F4 + shift:0x14F9 + shift] == current[0x14F4:0x14F9]
    assert old[0x14FC + shift:0x1506 + shift] == current[0x14FC:0x1506]
    assert current[0x1501:0x1504] == bytes.fromhex('06 7F C9')
    report = dict(passed=True, archive_sha256=digest, source='awk1.trd:STARHSUN.a',
                  archived_control0_delta=shift, txtr_zeros=[0xD95B, 0xD95F],
                  txtr_label=0xD95D, txtr_consumer_proved=False,
                  small_mask_buffer=[0xD990, 0xD9B0], small_mask_tail=[0xD99C, 0xD9B0],
                  archived_unfilled_entry=0xD501, unfilled_forced_entry_cases=check_unfilled_entries(current),
                  unfilled_current_game_caller_proved=False,
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/ControlsArchivedStarWorkspaceVerification.json'
    path.write_text(json.dumps(report, indent=2) + '\n', 'utf-8')
    print(json.dumps(report, indent=2))
    if args.publish:
        from ClassifyStationWorkspaceResources import publish

        publish(slot=22, origin=origin, ranges=((0x195B, 0x195F), (0x199C, 0x19B0)),
                resources=RESOURCES, tag='ControlsArchivedStarWorkspace',
                resource_module='CheckControlsArchivedStarWorkspace',
                resource_name='CONTROLS_ARCHIVED_STAR_WORKSPACE', proof=dict(archive_proof=path.name))


if __name__ == '__main__':
    main()
