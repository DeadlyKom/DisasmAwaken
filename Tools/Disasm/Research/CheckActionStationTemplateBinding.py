"""Создание записи ST16k и чтение фактически выбранной модели полётным рисователем."""
import json

from CheckActionModelDepthSelection import packet_metrics
from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionSpawnTemplateLoop import word
from CheckControlsTextQueue import base_memory
from CheckControlsWordRandom import reference as random_step
from CheckEffects import memory_image
from CheckMapSectorTables import reference as sector_table
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from CheckStationFlightCycle import ROOT, payload, run_to
from ReferenceActionLogRatio import EXP, LOG
from skoolkit.simutils import H, IXh, IXl, L


def check_render(baseline, key, template, depth, objects, *, close):
    memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=16)
    cpu = Simulator(memory)
    ports = PortTrace(cpu)
    cpu.set_tracer(ports)
    registers = cpu.registers
    put(memory, 0x9BC1, key)
    put(memory, 0x9B78, b'\0\0\0\0\0\0' + depth.to_bytes(2, 'little'))
    put(memory, 0x9B82, bytes(2))
    put(memory, 0xA100, b'\0\x80' + bytes(62) + b'\x80\x80')
    put(memory, 0xBFFE, b'\xFF\x3F')
    registers[:] = get_registers({'PC': 0x7859, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
    run_to(cpu, 0x78A1)
    assert registers[IXh] * 256 + registers[IXl] == template['pointer'] == 0x784F
    run_to(cpu, 0x3FFF)
    assert registers[SP] == 0xC000 and memory.o7ffd == 16
    assert ports.writes == [(0x7FFD, 17), (0x7FFD, 16)]
    assert bytes(memory[0xA100:0xA108]) == bytes(4) + depth.to_bytes(2, 'little') + bytes(2)
    assert memory[0xA112] == 0x12 and word(memory, 0xA140) == 0x8080
    table_before = bytes(memory[0x9E00:0x9F1C])
    assert word(memory, 0x9F00) == word(memory, 0x9F02) == 0xE469

    memory[0x9B81], memory[0x688B] = 1, 0
    for index in range(9):
        value = 0x7F00 if index % 4 == 0 else 0
        put(memory, 0x9B00 + 2 * index, value.to_bytes(2, 'little'))
    put(memory, 0x9B95, bytes(3))
    put(memory, 0xBFFE, b'\xFF\x3F')
    registers[:] = get_registers({'PC': 0xE020, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
    selector = 2 if close else 0
    chosen = template['selected_targets'][close]
    expected_pointer = chosen['address']
    reads = []
    fetches = []

    def observe(pc):
        if pc in (0xAACF, 0xAAD1, 0xAAE4, 0xAAE6):
            reads.append((pc, registers[H] * 256 + registers[L]))
        if pc in (0xAAD8, 0xAAF0):
            assert memory.o7ffd == 20
            fetches.append((pc, registers[H] * 256 + registers[L]))

    run_to(cpu, 0x3FFF, observe)
    start = 0x9E00 + selector
    assert reads == [(0xAACF, start), (0xAAD1, start + 1), (0xAAE4, start), (0xAAE6, start + 1)]
    assert fetches == [(0xAAD8, expected_pointer), (0xAAF0, expected_pointer)]
    size = packet_metrics(objects, expected_pointer)['bytes']
    offset = expected_pointer - 0xC000
    assert bytes(memory[0x9F1C:0x9F1C + size]) == objects[offset:offset + size]
    assert bytes(memory[0x9E00:0x9F1C]) == table_before
    assert registers[SP] == 0xC000 and memory.o7ffd == 16
    raster_changes = sum(a != b for a, b in zip(memory.banks[2][:0xC00], baseline[2][:0xC00]))
    assert raster_changes
    return dict(depth_input=depth, variant='near' if close else 'far',
                selector=selector, model=chosen, table_reads=reads, model_fetches=fetches,
                packet_bytes=size, raster_changed_bytes=raster_changes)


def main():
    reports = ROOT / 'Tools/Disasm/Reports'
    archive = json.loads((reports / 'ActionArchivedObjectTableVerification.json').read_bytes())
    template = archive['station_templates']['rows'][11]
    assert archive['passed'] and template['name'] == 'ST16k'
    assert template['authored_pair'] == 'IST16' and template['selected_pair'] == 'IPOL1'
    key = bytes.fromhex('38 4B FA 44 00')
    coords = sector_table(*key[:2])[0]
    map_memory = bytearray(65536)
    map_code = payload(7)
    map_memory[0xC000:0xC000 + len(map_code)] = map_code
    put(map_memory, 0xBFFE, b'\xFF\x3F')
    cpu = Simulator(map_memory, {'PC': 0xC474, 'SP': 0xBFFE, 'HL': 0xF200,
                                '^DE': int.from_bytes(key[:2], 'little')})
    run_to(cpu, 0x3FFF)
    assert map_memory[0xF200:0xF300] == coords
    assert (key[2], key[3]) in zip(coords[::2], coords[1::2])
    _, _, seed, _ = random_step(int.from_bytes(key[:2], 'little'), int.from_bytes(key[2:4], 'little'))
    assert ((seed ^ 255) >> 2) & 15 == template['index'] == 11

    flat = flat_action()
    objects = payload(24)
    banks = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[bank][:] = bytes(flat[start:start + 0x4000])
    banks[1][:] = bytes(base_memory()[0xC000:])
    banks[3][:] = bytes(memory_image()[0xC000:])
    banks[4][:len(objects)] = objects
    banks[2][0x1100:0x1200] = bytes(value & 255 for value in LOG)
    banks[2][0x1200:0x1300] = bytes(value >> 8 for value in LOG)
    banks[2][0x1300:0x1400] = bytes(EXP)
    cases = [check_render(banks, key, template, depth, objects, close=close)
             for depth, close in ((0x1800, True), (0x2200, False))]
    report = dict(passed=True, source_template=template, sector_key=key.hex(),
                  original_map_sector_generation_verified=True, cases=cases,
                  real_spawn_entry=0x7859, real_render_entry=0xE020, original_model_tables_preserved=True,
                  spawn_entry_and_render_geometry_prepared=True, gameplay_reachability_proved=False,
                  assembly_executed=False, native_execution=False)
    (reports / 'ActionStationTemplateBindingVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены создание записи ST16k и чтение обоих вариантов IPOL1.')


if __name__ == '__main__':
    main()
