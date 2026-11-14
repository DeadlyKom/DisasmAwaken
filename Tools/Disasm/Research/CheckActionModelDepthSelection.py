"""Выбор пакета OBJECT3D по глубине с исполнением чтения заголовка и копирования."""
from collections import Counter
from itertools import product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import ROOT, payload, run_to
from CheckMusic import PC, SP, Simulator, get_registers
from skoolkit.simutils import A, H, L


def packet_metrics(objects, address):
    start = address - 0xC000
    cursor = start + 2
    vertices = faces = lines = 0
    while objects[cursor]:
        vertices += objects[cursor].bit_count()
        cursor += 4
    cursor += 1
    while objects[cursor] & 15:
        header = objects[cursor]
        is_line = bool(header & 128)
        lines += is_line
        faces += not is_line
        cursor += 1 + (header & 15)
    assert objects[cursor] == 0
    return dict(vertices=vertices, faces=faces, lines=lines, bytes=cursor + 1 - start)


def check_selection(rows, objects):
    flat = flat_action()
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[4][:len(objects)] = objects
    memory = RecordedBanks(banks=banks, out7ffd=0x10)
    cpu = Simulator(memory)
    ports = PortTrace(cpu)
    cpu.set_tracer(ports)
    registers = cpu.registers
    put(memory, 0xE4A7, b'\xFE\xBF')
    counts = Counter()
    pairs = []
    for row in rows:
        selector = row['byte_selector']
        far, near = (target['address'] for target in row['targets'])
        assert selector % 4 == 0
        variants = {address: packet_metrics(objects, address) for address in (far, near)}
        for high, low in product(range(256), (0, 255)):
            memory[0x9B8E] = selector
            ports.writes.clear()
            registers[:] = get_registers({'PC': 0xE1A0, 'SP': 0xA11A, 'DE': high << 8 | low}, None, False)
            if high & 128:
                run_to(cpu, 0xE0E2)
                assert registers[SP] == 0xA11A and memory[0x9B8E] == selector and not ports.writes
                counts['negative'] += 1
                continue

            close = high < 0x1F
            address = near if close else far
            index = selector + 2 * close
            run_to(cpu, 0xAACC)
            assert registers[A] == memory[0x9B8E] == index and registers[SP] == 0xBFFC
            run_to(cpu, 0xAAD8)
            assert registers[H] * 256 + registers[L] == address and memory.o7ffd == 0x14
            run_to(cpu, 0xE1B9)
            offset = address - 0xC000
            assert bytes((registers[L], registers[H])) == objects[offset:offset + 2]
            assert registers[SP] == 0xBFFE and memory.o7ffd == 0x10
            assert ports.writes == [(0x7FFD, 0x14), (0x7FFD, 0x10)]
            counts['near' if close else 'far'] += 1

            if (high, low) in ((0x1E, 0xFF), (0x1F, 0)):
                size = variants[address]['bytes']
                put(memory, 0x9F1C, bytes((0xA5,)) * size)
                registers[PC] = 0xD5C9
                ports.writes.clear()
                run_to(cpu, 0xAAE2)
                assert registers[L] == index
                run_to(cpu, 0xD5D0)
                assert bytes(memory[0x9F1C:0x9F1C + size]) == objects[offset:offset + size]
                assert registers[SP] == 0xBFFE and memory.o7ffd == 0x10
                assert ports.writes == [(0x7FFD, 0x14), (0x7FFD, 0x10)]
                counts['packet_copy'] += 1
        pairs.append(dict(index=row['index'], selector=selector,
                          far={**row['targets'][0], **variants[far]}, near={**row['targets'][1], **variants[near]}))
    assert counts == {'negative': 16384, 'far': 12416, 'near': 3968, 'packet_copy': 128}
    different = [row for row in pairs if row['far']['address'] != row['near']['address']]
    assert len(different) == 32
    fewer_faces = [row['index'] for row in different if row['near']['faces'] < row['far']['faces']]
    assert fewer_faces == ['IUFO7']
    assert sum(row['near']['faces'] > row['far']['faces'] for row in different) == 31
    return dict(passed=True, selection_cases=32768, outcomes=dict(counts), pairs=pairs,
                shared_packet_pairs=len(pairs) - len(different), near_variant_with_fewer_faces=fewer_faces,
                entry_after_coordinate_transform=0xE1A0, header_caller_return=0xE1B9,
                negative_depth_target=0xE0E2, packet_copy_caller_return=0xD5D0,
                prepared_transformed_depth=True, full_frame_not_executed=True,
                assembly_executed=False, native_execution=False)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    archive = json.loads((reports / 'ActionArchivedObjectTableVerification.json').read_bytes())
    storage = json.loads((reports / 'ActionObjectStreamStorageVerification.json').read_bytes())
    rows = archive['original_table_rows']
    assert archive['passed'] and len(rows) == 71
    assert storage['passed']
    known_selectors = set(storage['indexed_model_writers']['known_indices'])
    archive_selectors = {row['byte_selector'] for row in rows[:64]}
    assert len(known_selectors) == 55 and known_selectors <= archive_selectors
    result = check_selection(rows[:64], payload(24))
    result['record_sources'] = dict(
        confirmed_pair_starts=sorted(known_selectors),
        other_tested_pair_starts=sorted(archive_selectors - known_selectors),
        arbitrary_indirect_writers_audited=False,
    )
    (reports / 'ActionModelDepthSelectionVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', 'utf-8')
    print('Сверены 32768 выборов модели по глубине и 128 копий полного пакета.')


if __name__ == '__main__':
    main()
