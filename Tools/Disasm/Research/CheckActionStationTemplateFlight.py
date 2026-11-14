"""Штатный вход планировщика после гиперперехода к ключу шаблона ST16k."""
import argparse
from collections import Counter
from functools import partial
from hashlib import sha256
import json
from pathlib import Path

from CheckBootBankFileReads import ACTION_TAIL, check_intro_transition, watch_addresses
from CheckPurchasedHyperJump import check_flight
from CheckStationFlightCycle import DISK, ROOT, payload, put
from TraceFlight import Ports
from skoolkit.simutils import A, F, H, IXh, IXl, IYh, IYl, L, PC, SP


FRAME = 0xA85E
VECTOR = (0x9B79, 0x9B7C, 0x9B7F)
WORK_VECTOR = (0x9B78, 0x9B7B, 0x9B7E)
SCALED_VECTOR = (0xE5B3, 0xE5D2, 0xE5ED)
SUBTRACT_VECTOR = 0x66D2
REQUEST_BOOST = 0x74A3
ALTERNATE_GATE = 0x794B
TEMPLATE_ENTRY = 0x7859
TEMPLATE_ROW = 0x78A1
MODEL_WRITER = 0x78EC
DESTINATION = '384bfa4400'


class FlightKeys(Ports):
    boost_pressed = False

    def __init__(self, memory):
        super().__init__(memory)
        self.rows = {}

    def read_port(self, registers, port):
        if registers[PC] == 0x6F34:
            value = self.rows.get(port, 255)
            if self.boost_pressed and port == 0xBFFE:
                value &= 0xF7
            return value
        return super().read_port(registers, port)


def signed_components(memory, addresses, width):
    return tuple(int.from_bytes(memory[address:address + width], 'little', signed=True)
                 for address in addresses)


def observe_sites(cpu, sites, observer):
    grouped = {}
    for address in sites:
        opcode = cpu.memory[address]
        grouped.setdefault(opcode, set()).add(address)
    for opcode, addresses in grouped.items():
        original = cpu.opcodes[opcode]

        def execute(original=original, addresses=addresses):
            pc = cpu.registers[PC]
            if pc in addresses:
                observer(pc)
            original()

        cpu.opcodes[opcode] = execute


def observe_flight(cpu):
    memory, registers = cpu.memory, cpu.registers
    keys = FlightKeys(memory)
    cpu.set_tracer(keys)
    assert memory.o7ffd == 16 and registers[PC] == FRAME and registers[SP] == 0xBFFC
    assert bytes(memory[0x9BC1:0x9BC6]).hex() == DESTINATION
    model_table = bytes(memory[0x9E00:0x9F1C])
    gate_rows, entries, templates, created = [], [], [], []
    checkpoint = None
    other_selection = 0
    checkpoint_frame_end = None
    motion_steps, boost_requests = [], []

    def snapshot():
        return tuple(bytes(bank) for bank in memory.banks), registers.copy()

    def restore(state):
        for destination, saved in zip(memory.banks, state[0], strict=True):
            destination[:] = saved
        registers[:] = state[1]
        memory.out7ffd(16)

    def observe(pc):
        nonlocal checkpoint, other_selection
        if pc == ALTERNATE_GATE:
            values = [int.from_bytes(memory[address:address + 2], 'little', signed=True) for address in VECTOR]
            gate_rows.append(dict(frame=frame, vector=values))
            if checkpoint is None:
                checkpoint = snapshot()
        elif pc == TEMPLATE_ENTRY:
            entries.append(frame)
        elif pc == TEMPLATE_ROW:
            templates.append(registers[IXh] * 256 + registers[IXl])
        elif pc == MODEL_WRITER:
            created.append((registers[IYh] * 256 + registers[IYl], registers[A]))
        elif pc == SUBTRACT_VECTOR:
            motion_steps.append((signed_components(memory, WORK_VECTOR, 3),
                                 signed_components(memory, SCALED_VECTOR, 2)))
        elif pc == REQUEST_BOOST:
            boost_requests.append(frame)
        else:
            other_selection += 1

    start = snapshot()
    observe_sites(cpu, (ALTERNATE_GATE, TEMPLATE_ENTRY, TEMPLATE_ROW, MODEL_WRITER, 0x7B78,
                        SUBTRACT_VECTOR, REQUEST_BOOST), observe)
    for frame in range(1, 257):
        cpu.run(FRAME, FRAME, interrupts=True)
        assert memory.o7ffd == 16 and registers[SP] == 0xBFFC
        if checkpoint is not None and checkpoint_frame_end is None:
            checkpoint_frame_end = snapshot()
    idle = list(gate_rows)
    assert len(idle) == 29 and other_selection == 3
    assert idle[0] == dict(frame=24, vector=[1535, 255, -257])
    assert checkpoint is not None and checkpoint_frame_end is not None
    assert all(max(map(abs, row['vector'])) >= 112 for row in idle)
    assert not entries and not templates and not created
    assert bytes(memory[0x9E00:0x9F1C]) == model_table
    idle_other_selection = other_selection
    assert len(motion_steps) == 256 and not boost_requests

    restore(start)
    gate_rows.clear()
    motion_steps.clear()
    for frame in range(1, 65):
        keys.boost_pressed = frame >= 33
        cpu.run(FRAME, FRAME, interrupts=True)
        assert memory.o7ffd == 16 and registers[SP] == 0xBFFC
    keys.boost_pressed = False

    final_vector = signed_components(memory, WORK_VECTOR, 3)
    vectors = [before for before, _ in motion_steps] + [final_vector]
    assert len(motion_steps) == 64 and boost_requests == list(range(33, 65))
    assert vectors[0] == (392960, 65280, -65281) and final_vector == (392960, 65280, -105848)
    assert all(tuple(value - step for value, step in zip(before, steps, strict=True)) == after
               for (before, steps), after in zip(motion_steps, vectors[1:], strict=True))
    assert all(steps[:2] == (0, 0) and steps[2] >= 0 for _, steps in motion_steps)
    assert len(gate_rows) == 6 and not entries and not templates and not created
    assert all(max(map(abs, row['vector'])) >= 112 for row in gate_rows)
    assert bytes(memory[0x9E00:0x9F1C]) == model_table
    boost = dict(keyboard_port=0xBFFE, active_low_mask=8, requests=boost_requests,
                 complete_frames=64, initial_vector=vectors[0], final_vector=final_vector,
                 vector_steps_match=64, gate_visits=list(gate_rows), template_entries=0)

    restore(start)
    gate_rows.clear()
    entries.clear()
    templates.clear()
    created.clear()
    boost_requests.clear()
    for frame in range(1, 169):
        keys.rows.clear()
        if frame <= 26:
            keys.rows[0xBFFE] = 0xFD
        if 20 < frame <= 26:
            keys.rows[0xFDFE] = 0xFD
        keys.boost_pressed = frame >= 59
        cpu.run(FRAME, FRAME, interrupts=True)
        assert memory.o7ffd == 16 and registers[SP] == 0xBFFC
    keys.rows.clear()
    keys.boost_pressed = False
    assert entries == [168] and templates == [0x784F] and created == [(0xA100, 0)]
    assert gate_rows[-1] == dict(frame=168, vector=[108, -23, -60])
    assert memory[0xA112] == 0x12 and memory[0xA106] == 0
    assert boost_requests == list(range(59, 169))
    assert bytes(memory[0x9E00:0x9F1C]) == model_table
    navigation = dict(complete_frames=168, inputs=[
        dict(first_frame=1, last_frame=26, port=0xBFFE, active_low_mask=2),
        dict(first_frame=21, last_frame=26, port=0xFDFE, active_low_mask=2),
        dict(first_frame=59, last_frame=168, port=0xBFFE, active_low_mask=8)],
        gate_visits=list(gate_rows), template_entries=list(entries), template_pointer=templates[0],
        created_record=created[0][0], created_class=memory[0xA112], created_selector=created[0][1],
        vector_substituted=False, code_substituted=False, irq_executed=True,
        model_table_preserved=True)

    render_events, render_insertions, render_nodes, raster_changes = [], [], [], []
    render_decisions = []
    current_record = None
    raster_before = None
    render_active = True

    def observe_render(pc):
        nonlocal current_record, raster_before
        if not render_active or frame != 177:
            return
        if pc == 0xE1B2:
            current_record = registers[SP] - 0x1A
        elif pc == 0xE40F:
            render_insertions.append(current_record)
        elif pc == 0xE4B1:
            node = registers[H] * 256 + registers[L]
            render_nodes.append(dict(address=node, data=bytes(memory[node:node + 14]).hex()))
        elif pc == 0xE4DB:
            raster_before = bytes(memory.banks[2][:0xC00])
        elif pc == 0xE4FD:
            assert raster_before is not None
            raster_changes.append(sum(before != after for before, after in
                                      zip(raster_before, memory.banks[2][:0xC00], strict=True)))
            assert bytes(memory[0x9F1C:0x9F5C]) == bytes(memory.banks[4][:64])
        elif 0xE4E7 <= pc <= 0xE4FA:
            render_decisions.append(dict(pc=pc, a=registers[A], f=registers[F]))
        elif not raster_changes:
            render_events.append(dict(pc=pc, address=registers[H] * 256 + registers[L],
                                      page=memory.o7ffd))

    observe_sites(cpu, (0xE1B2, 0xE40F, 0xE4B1, 0xE4DB, 0xE4E7, 0xE4ED, 0xE4F4, 0xE4FA, 0xE4FD,
                        0xAACF, 0xAAD1, 0xAAD8, 0xAAE4, 0xAAE6, 0xAAF0), observe_render)
    for frame in range(169, 178):
        keys.rows.clear()
        if frame <= 176:
            keys.rows.update({0xBFFE: 0xFD, 0xFEFE: 0xFB})
        cpu.run(FRAME, FRAME, interrupts=True)
        assert memory.o7ffd == 16 and registers[SP] == 0xBFFC
    keys.rows.clear()
    render_active = False
    assert render_insertions == [0xA100]
    assert render_nodes == [dict(address=0x8F00, data='0100000100000000fc157bee405c')]
    assert render_decisions == [dict(pc=0xE4E7, a=0xF8, f=0xA8),
                                dict(pc=0xE4ED, a=0, f=0x54),
                                dict(pc=0xE4FA, a=8, f=0x18)]
    assert raster_changes == [0]
    assert render_events == [
        dict(pc=0xAACF, address=0x9E00, page=16), dict(pc=0xAAD1, address=0x9E01, page=16),
        dict(pc=0xAAD8, address=0xC000, page=20), dict(pc=0xAAE4, address=0x9E00, page=16),
        dict(pc=0xAAE6, address=0x9E01, page=16), dict(pc=0xAAF0, address=0xC000, page=20)], render_events
    assert bytes(memory[0x9E00:0x9F1C]) == model_table
    navigation['render'] = dict(frame=177, additional_inputs=[
        dict(first_frame=169, last_frame=176, port=0xBFFE, active_low_mask=2),
        dict(first_frame=169, last_frame=176, port=0xFEFE, active_low_mask=4)],
        inserted_records=render_insertions, queue_nodes=render_nodes, reads=render_events, decisions=render_decisions,
        copied_packet_bytes=64, packet_matches_original_bank4=True, model_address=0xC000,
        raster_changed_bytes=raster_changes, model_table_preserved=True)

    frame = idle[0]['frame']
    for values in (None, (112, 0, 34), (0, 0, 34)):
        restore(checkpoint)
        gate_rows.clear()
        entries.clear()
        templates.clear()
        created.clear()
        if values is not None:
            for address, value in zip(VECTOR, values, strict=True):
                put(memory, address, value.to_bytes(2, 'little'))
        cpu.run(ALTERNATE_GATE, FRAME, interrupts=True)
        assert memory.o7ffd == 16 and registers[SP] == 0xBFFC
        assert bytes(memory[0x9E00:0x9F1C]) == model_table
        assert len(gate_rows) == 1
        if values is None:
            assert snapshot() == checkpoint_frame_end
        if values != (0, 0, 34):
            assert not entries and not templates and not created
        else:
            assert entries == [frame] and templates == [0x784F] and len(created) == 1
            address, selector = created[0]
            assert selector == memory[address + 6] == 0 and memory[address + 0x12] == 0x12

    return dict(idle_complete_frames=256, idle_gate_visits=idle,
                idle_other_class_selection_visits=idle_other_selection, idle_template_entries=0,
                straight_boost=boost,
                natural_navigation=navigation,
                replayed_frame=frame, unmodified_replay_matches_all_ram_and_registers=True,
                rejected_vector=[112, 0, 34], accepted_vector=[0, 0, 34], created_record=address,
                created_class=0x12, created_selector=selector, template_pointer=0x784F,
                written_vector_words=list(VECTOR), model_table_preserved=True)


def check_route(cpu, ports, basic, dos, set_rom, *, mark_context, symbols):
    result = check_flight(cpu, ports, basic, dos, set_rom, mark_context=mark_context,
                          stock=(7, 0), symbols=symbols, coordinates=(250, 68), finish_first_frame=False)
    assert result['selected_context'] == DESTINATION and result['measured_cost'] == 3
    assert result['accepted'] and result['final_stock'] == [1, 0]
    font, template = range(0xC600, 0xC870), range(0xDADE, 0xDB5D)
    watched_banks = dict.fromkeys(range(ACTION_TAIL, 0x10000), 0)
    watched_banks.update(dict.fromkeys((*font, *template), 1))
    assert bytes(cpu.memory.banks[1][0x600:0x870]) == payload(22)[0x600:0x870]
    assert bytes(cpu.memory.banks[1][0x1ADE:0x1B5D]) == payload(23)[:127]
    with watch_addresses(cpu, watched_banks, watched_banks) as accesses:
        scheduler = observe_flight(cpu)
    bank1_accesses = [(kind, address, pc) for kind, address, pc in accesses if watched_banks[address] == 1]
    accesses = [(kind, address, pc) for kind, address, pc in accesses if watched_banks[address] == 0]
    assert {address for _, address, _ in accesses} == {0xFFDE, 0xFFDF}
    assert {pc for kind, _, pc in accesses if kind == 'write'} == {0xD273, 0xD3AE}
    assert {pc for kind, _, pc in accesses if kind == 'read'} == {
        0xD2F6, 0xD313, 0xD324, 0xD383, 0xD3A2, 0xD435, 0xD451, 0xD461, 0xD4BF, 0xD4FE}
    assert set(accesses[:2]) == {('write', 0xFFDE, accesses[0][2]), ('write', 0xFFDF, accesses[0][2])}
    word_operations = Counter(kind for kind, address, _ in accesses if address == 0xFFDE)
    assert word_operations == {'read': 2420, 'write': 2420}
    counts = Counter((kind, pc) for kind, _, pc in accesses)
    tail = dict(bank=0, start=ACTION_TAIL, end_exclusive=0x10000,
                accessed_addresses=[0xFFDE, 0xFFDF],
                word_operations=dict(word_operations),
                sites=[dict(operation=kind, pc=pc, count=count)
                       for (kind, pc), count in sorted(counts.items())],
                first_access_writes_both_bytes=True)
    assert all(kind == 'read' and address in font for kind, address, _ in bank1_accesses)
    assert all(address != pc for _, address, pc in bank1_accesses)
    assert bytes(cpu.memory.banks[1][0x600:0x870]) == payload(22)[0x600:0x870]
    assert bytes(cpu.memory.banks[1][0x1ADE:0x1B5D]) == payload(23)[:127]
    legacy_counts = Counter(pc for _, _, pc in bank1_accesses)
    assert legacy_counts == {
        **dict.fromkeys((0xF00A, 0xF018, 0xF026, 0xF034, 0xF042, 0xF050), 114),
        **dict.fromkeys((0xF05D, 0xF067, 0xF071, 0xF07B, 0xF085, 0xF08F), 73)}
    legacy = dict(bank=1, font_start=font.start, font_end_exclusive=font.stop,
                  template_start=template.start, template_end_exclusive=template.stop,
                  writes=0, instruction_fetches=0, font_bytes_match_disk=True, template_bytes_match_disk=True,
                  font_read_sites=[dict(pc=pc, count=count) for pc, count in sorted(legacy_counts.items())])
    return dict(hyperjump=result, scheduler=scheduler, bank0_tail_after_hyperjump=tail,
                bank1_legacy_inputs_after_hyperjump=legacy)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom', type=Path)
    args = parser.parse_args()
    basic = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    dos = args.dos_rom.read_bytes()
    symbols = json.loads((ROOT / 'Tools/Disasm/Reports/Symbols.json').read_bytes())
    result = check_intro_transition(basic, dos, 0, mark_context=False,
                                    flight_check=partial(check_route, symbols=symbols))
    report = dict(passed=True, disk_sha256=sha256(DISK).hexdigest(), dos_rom_sha256=sha256(dos).hexdigest(),
                  **result['flight_transition'], actual_purchase_and_map_selection=True,
                  trdos_substituted=False, irq_executed_during_idle_frames=True,
                  natural_navigation_to_spawn_gate_proved=True, native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ActionStationTemplateFlightVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Проверены гиперпереход, генерация ST16k на кадре 168 и чтение KN01pol1 на кадре 177.')


if __name__ == '__main__':
    main()
