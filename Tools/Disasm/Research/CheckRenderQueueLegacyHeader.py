"""Различие архивной и текущей упаковки узла, без назначения неизвестных полей по догадке."""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckActionParameterActivation import flat_action
from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory


def main():
    archive_path = ROOT / 'Tools/Disasm/Research/References/AuthorArchives/ArchiveAwakenSources.zip'
    digest = sha256(archive_path.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(archive_path) as archive:
        origin, compiled, _ = read_entry(archive.read('awk6.trd'), b'D3D     C')
        _, source, _ = read_entry(archive.read('awk6.trd'), b'CLPXR1  a')
    assert origin == 0xC000
    old_base = [0] * 65536
    old_base[origin:origin + len(compiled)] = compiled
    current_base = flat_action()
    assert bytes(old_base[0xEECD:0xEEEE]) == bytes.fromhex(
        'C6 0E 32 03 CF 6F F9 D5 C5 2A 38 DA E5 2A F6 DA E5 '
        '3A 20 C2 F5 33 2A 1E C2 E5 2A FA CE E5 C3 AE EC')
    assert bytes(current_base[0xE486:0xE4A6]) == bytes.fromhex(
        'C6 0E 32 A2 9B 6F F9 C5 2A C4 D7 E5 2A B6 D9 E5 '
        '3A 14 9B F5 33 2A 12 9B E5 2A 8D 9B E5 C3 E2 E0')
    rows = source.split(b'\r')
    start = next(i for i, row in enumerate(rows) if row.startswith(b'La272\x06'))
    fragment = rows[start:start + 18]
    assert fragment[4:6] == [b'\x06\x8c\x05- \x05\x8b', b'\x06\x8c\x05- \x05\x8a']
    assert fragment[-3:] == [b'\x06\x8c\x05 \x06\x83\x03\x8c,(Sets)',
                              b'\x06\x8c\x05- \x05\x8c', b'\x06\x8c\x053\x06\x83L9efc']
    memories = [Memory(old_base), Memory(current_base)]
    cpus = [Simulator(memory) for memory in memories]
    cases = 0
    for offset in range(0, 252, 14):
        for seed in range(256):
            # Создаём различимые слова снимка и начальный шаблон всех четырнадцати байтов.
            header, phases = seed | ((255 - seed) << 8), ((seed * 73) ^ 0xA15C) & 65535
            x, y, depth, extra = ((seed * factor) ^ salt for factor, salt in
                                  ((257, 0x1234), (109, 0x5678), (71, 0x9ABC), (37, 0xDEF0)))
            x, y, depth, extra = (value & 65535 for value in (x, y, depth, extra))
            phase2 = seed ^ 0x96
            node = 0x8F00 + offset
            initial_node = bytes((seed + i * 17) & 255 for i in range(14))
            for version, (memory, cpu) in enumerate(zip(memories, cpus)):
                memory.recording = False
                memory[node:node + 14] = initial_node
                fields = ((0xCEFA, header), (0xC21E, phases), (0xDAF6, x), (0xDA38, y)) if version == 0 else (
                    (0x9B8D, header), (0x9B12, phases), (0xD9B6, x), (0xD7C4, y))
                for address, value in fields:
                    memory[address:address + 2] = value.to_bytes(2, 'little')
                memory[0xC220 if version == 0 else 0x9B14] = phase2
                cpu.registers[:] = get_registers(dict(AF=offset << 8 | seed, HL=node, DE=extra,
                    BC=depth, SP=0xBFFE, PC=0xEECD if version == 0 else 0xE486), None, False)
                memory.writes = []
                memory.recording = True
                stop = 0xECAE if version == 0 else 0xE0E2
                for _ in range(30):
                    if cpu.registers[PC] == stop:
                        break
                    cpu.run()
                else:
                    raise AssertionError(('Не достигнуто продолжение', version, offset, seed))
                memory.recording = False
                # Сравниваем физическую раскладку, дополнительное архивное слово сдвигает начало на два байта.
                packed = header.to_bytes(2, 'little') + phases.to_bytes(2, 'little') + bytes([phase2])
                packed += x.to_bytes(2, 'little') + y.to_bytes(2, 'little') + depth.to_bytes(2, 'little')
                begin = 1 if version == 0 else 3
                if version == 0:
                    packed += extra.to_bytes(2, 'little')
                expected = initial_node[:begin] + packed
                assert bytes(memory[node:node + 14]) == expected
                assert cpu.registers[SP] == node + begin
                written = {address for address, value in memory.writes if node <= address < node + 14}
                assert written == set(range(node + begin, node + 14))
                assert memory[0xCF03 if version == 0 else 0x9BA2] == offset + 14
            cases += 1
    report = dict(passed=True, cases=cases, machine_executions=cases * 2,
        archive_sha256=digest, archived_compiled='awk6.trd:D3D.C', archived_source='awk6.trd:CLPXR1.a',
        archived_fragment_hex=[row.hex() for row in fragment],
        archived_writer=0xEECD, current_writer=0xE486, node_bytes=14,
        archived_header_offset=1, current_header_offset=3,
        archived_extra_tail_word_offset=12, archived_extra_push='DE',
        archived_final_sp_offset=1, current_final_sp_offset=3,
        current_bytes_1_2_preserved=True, node_link_preserved=True,
        current_global_role_of_bytes_1_2_proved=False, interrupt_padding_intent_proved=False,
        full_queue_composition_executed=False, assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/RenderQueueLegacyHeaderVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Проверены {cases} пар раскладок на исходных инструкциях, архивный SETS находился по +1, текущий заголовок по +3.')


if __name__ == '__main__':
    main()
