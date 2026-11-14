"""E020: формирование очереди, загрузка узлов, вывод и конечный возврат."""
from collections import Counter
from itertools import chain, product
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckActionPatchedVector import OUTPUTS
from CheckEffects import memory_image
from CheckFlightKeyPaths import ClipDispatchProbe
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace
from ReferenceActionLogRatio import EXP, LOG
from ReferenceActionPatchedVector import evaluate


RETURN_FLAGS = {0xC0: (0x40, False), 0xC8: (0x40, True),
                0xD0: (0x01, False), 0xD8: (0x01, True),
                0xE0: (0x04, False), 0xE8: (0x04, True),
                0xF0: (0x80, False), 0xF8: (0x80, True)}


class RenderStackMemory(RecordedBanks):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stack_writers = {}
        self.instruction = None
        self.tail_accesses = None
        self.executing = False
        self.bank0_tail_accesses = Counter()
        self.bank0_tail_written = set()
        self.bank0_tail_original_reads = Counter()

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.executing and isinstance(address, int) and address >= 0xF866 and self.o7ffd & 7 == 0:
            self.bank0_tail_accesses['read', self.instruction[1], address] += 1
            if address not in self.bank0_tail_written:
                self.bank0_tail_original_reads[self.instruction[1], address] += 1
        if (self.tail_accesses is not None and self.instruction is not None
                and isinstance(address, int) and 0xA00A <= address < 0xA01C):
            self.tail_accesses.append(('read', self.instruction[1], address, value))
        return value

    def __setitem__(self, address, value):
        if self.executing and address >= 0xF866 and self.o7ffd & 7 == 0:
            self.bank0_tail_accesses['write', self.instruction[1], address] += 1
            self.bank0_tail_written.add(address)
        if self.instruction is not None and 0xBF00 <= address < 0xC000:
            self.stack_writers[address] = self.instruction
        if self.tail_accesses is not None and self.instruction is not None and 0xA00A <= address < 0xA01C:
            self.tail_accesses.append(('write', self.instruction[1], address, value))
        super().__setitem__(address, value)


def taken_return(memory, pc, flags, sp):
    opcode = memory[pc]
    condition = RETURN_FLAGS.get(opcode)
    if opcode != 0xC9 and (condition is None or bool(flags & condition[0]) != condition[1]):
        return None
    # Проверка адреса из физического CPU-стека и происхождения обоих байтов.
    assert 0xBF00 <= sp <= 0xBFFE, (pc, sp)
    target = memory[sp] | memory[sp + 1] << 8
    writer = memory.stack_writers.get(sp)
    assert writer == memory.stack_writers.get(sp + 1), (pc, sp)
    assert target >> 8 != 0xCF, (pc, sp, writer, target)
    if writer is None:
        assert target == 0x3FFF
    elif writer == (0, 0xC06F, 0xD5):
        assert target == 0xC071
    else:
        _, address, opcode = writer
        assert opcode == 0xCD or opcode & 0xC7 == 0xC4, writer
        assert target == address + 3
    return target, writer


def code_bank(memory, address):
    if address >= 0xC000:
        return memory.o7ffd & 7
    return 2 if address >= 0x8000 else 5


def main(report_name='ActionNonemptyRenderFrameVerification.json'):
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[3][:] = bytes(memory_image()[0xC000:])
    objects = (ROOT / 'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    baseline[4][:len(objects)] = objects
    baseline[2][0x1100:0x1200] = bytes(value & 255 for value in LOG)
    baseline[2][0x1200:0x1300] = bytes(value >> 8 for value in LOG)
    baseline[2][0x1300:0x1400] = bytes(EXP)
    matrix = ((127, 0, 0), (0, 127, 0), (0, 0, 127))
    paths = Counter()
    returns = Counter()
    high_page = bytes(flat[0xD000:0xD100])
    regular_clip = ClipDispatchProbe(high_page)
    tail_profiles = []
    bank0_tail_accesses = Counter()
    profiles_with_tail_accesses = 0
    cases = 0
    catalogue = set()
    mixed = product((0, 12, 32, 64), ((0x1000,), (0x2000, 0x3000, 0x1000), (0x2200, 0x2200, 0x2200)),
                    (0, 0x180, 0x600, -1), ((0, 0, 0), (1, 7, 11)))
    originals = ((offset, (0x2200,), 0, (0, 0, 0)) for offset in range(0, 256, 2))
    tail_pointers = [flat[address] | flat[address + 1] << 8 for address in range(0x9F00, 0x9F1C, 4)]
    assert len(set(tail_pointers)) == 7
    assert all(0xC000 <= pointer < 0xC000 + len(objects) for pointer in tail_pointers)
    regular = ((None, args) for args in chain(mixed, originals))
    extra = ((pointer, (0, (0x2200,), 0, (0, 0, 0))) for pointer in tail_pointers)
    for tail_pointer, (model, depths, lateral, phases) in chain(regular, extra):
        memory = RenderStackMemory(banks=[bank.copy() for bank in baseline], out7ffd=16)
        clip = regular_clip if tail_pointer is None else ClipDispatchProbe(high_page)

        def put(address, value):
            memory[address], memory[address + 1] = value & 255, value >> 8

        def word(address):
            return memory[address] | memory[address + 1] << 8

        if tail_pointer is not None:
            # Дополнительный физический поток выбирается через один подставленный указатель страницы 9E.
            put(0x9E00, tail_pointer)
            memory.tail_accesses = []
        memory[0x9B81], memory[0x688B] = 1, 0
        for index in range(9):
            put(0x9B00 + 2 * index, 0x7F00 if index % 4 == 0 else 0)
        for address in range(0x9B95, 0x9B98):
            memory[address] = 0
        put(0xBFFE, 0x3FFF)
        order, payloads = [], []
        old_outputs = [word(address) for address in OUTPUTS]
        for index, depth in enumerate(depths):
            pointer = 0xA100 + 64 * index
            vector = (depth // 2 - 64 if lateral == -1 else lateral, 0, depth)
            for offset, value in enumerate(vector):
                put(pointer + 2 * offset, value)
            for offset, value in enumerate((model, *phases)):
                memory[pointer + 6 + offset] = value
            outputs = evaluate(vector, matrix, old_outputs)['outputs']
            old_outputs = outputs
            selected = model + 2 * (outputs[2] >> 8 < 31)
            if tail_pointer is None and cases >= 96:
                assert selected == model
                catalogue.add(selected)
            if tail_pointer is not None:
                assert selected == 0
            payload = bytes((int(not (phases[0] | phases[2])), selected, *phases))
            payload += b''.join(value.to_bytes(2, 'little') for value in outputs)
            payloads.append(payload)
            position = next((pos for pos, prev in enumerate(order)
                             if (word_from_payload(payloads[prev]) - outputs[2] - int(prev == 0)) & 32768),
                            len(order))
            order.insert(position, index)
        put(0xA100 + 64 * len(depths), 0x80FF)

        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xE020, 'SP': 0xBFFE, 'IY': 0x5C3A}, None, False)
        loaded, rendered = [], []
        context = (model, depths, lateral, phases, tail_pointer)
        case_paths = Counter()
        for _ in range(500000):
            r = sim.registers
            pc = r[PC]
            if pc == 0x3FFF:
                break
            clip.observe(memory, r)
            if pc == 0xE4A6:
                assert memory[0x9BA1] == 14 * order[0] and memory[0x9BA2] == 14 * len(order), context
                for position, index in enumerate(order):
                    pointer = 0x8F00 + 14 * index
                    link = 14 * order[position + 1] if position + 1 < len(order) else 1
                    assert memory[pointer] == link, context
                    assert bytes(memory[pointer + 3:pointer + 14]) == payloads[index], context
            if pc == 0xE4B1:
                assert r[SP] == 0xBFFE and r[6] == 0x8F
                loaded.append(r[7] // 14)
            if pc == 0xE4DB:
                index = loaded[-1]
                assert r[SP] == 0xBFFC and word(0xBFFC) == 0x8F00 + 14 * index
                assert bytes(memory[0x9B8D:0x9B8F]) + bytes(memory[0x9B12:0x9B15]) == payloads[index][:5]
                assert b''.join(word(address).to_bytes(2, 'little') for address in OUTPUTS) == payloads[index][5:]
                rendered.append(index)
            if pc in (0xE4F4, 0xE4FA):
                case_paths['inside' if pc == 0xE4F4 else 'clipped'] += 1
            sp = r[SP]
            returned = taken_return(memory, pc, r[1], sp)
            bank = code_bank(memory, pc)
            memory.instruction = (bank, pc, memory[pc])
            memory.executing = True
            sim.run()
            memory.executing = False
            if returned is not None:
                target, writer = returned
                assert (r[PC], r[SP]) == (target, sp + 2), (pc, writer, target, context)
                if tail_pointer is None:
                    returns[bank, pc, writer, target] += 1
        assert sim.registers[PC] == 0x3FFF and sim.registers[SP] == 0xC000, context
        assert loaded == rendered == order, (context, order, loaded, rendered)
        paging = [(port, value) for port, value in trace.writes if port == 0x7FFD]
        assert paging == [(0x7FFD, 19), (0x7FFD, 16)] + [(0x7FFD, 20), (0x7FFD, 16)] * (2 * len(order)), context
        assert memory.o7ffd == 16
        bank0_tail_accesses.update(memory.bank0_tail_accesses)
        assert not memory.bank0_tail_original_reads, (context, memory.bank0_tail_original_reads)
        profiles_with_tail_accesses += bool(memory.bank0_tail_accesses)
        if tail_pointer is not None:
            assert not clip.alias_entries
            assert bytes(memory[0xA01C:0xA027]) == bytes(flat[0xA01C:0xA027])
            assert bytes(memory.banks[4][:len(objects)]) == objects
            raster_changes = sum(current != initial for current, initial
                                 in zip(memory.banks[2][:0xC00], baseline[2][:0xC00]))
            assert raster_changes
            tail_profiles.append(dict(pointer=tail_pointer, paths=dict(case_paths),
                                      raster_bytes_changed=raster_changes,
                                      clip_dispatches=dict(clip.dispatches),
                                      destination_tail_accesses=memory.tail_accesses))
            continue
        paths.update(case_paths)
        paths['nodes'] += len(order)
        cases += 1
    assert paths['inside'] or paths['clipped'], paths
    assert regular_clip.dispatches and not regular_clip.alias_entries
    assert catalogue == set(range(0, 256, 2))
    assert len(tail_profiles) == 7
    assert [row for row in tail_profiles[-1]['destination_tail_accesses'] if row[2] == 0xA016] == [
        ('write', 0xAB13, 0xA016, 0), ('read', 0xDD23, 0xA016, 0)]
    assert sum(count for (_, _, writer, target), count in returns.items()
               if writer is None and target == 0x3FFF) == cases
    assert all(target == 0x3FFF for (_, _, writer, target) in returns if writer is None)
    assert profiles_with_tail_accesses == 229
    assert {address for _, _, address in bank0_tail_accesses} == {0xFFDE, 0xFFDF}
    assert {pc for op, pc, _ in bank0_tail_accesses if op == 'write'} == {0xD273, 0xD3AE}
    for op, pc, address in bank0_tail_accesses:
        assert bank0_tail_accesses[op, pc, address] == bank0_tail_accesses[op, pc, address ^ 1]
    word_operations = Counter()
    for (op, _, address), count in bank0_tail_accesses.items():
        if address == 0xFFDE:
            word_operations[op] += count
    assert word_operations == {'read': 6332, 'write': 6332}
    return_paths = [dict(pc=pc, bank=bank, stack_writer=writer[1] if writer else None,
                         stack_writer_bank=writer[0] if writer else None,
                         stack_writer_opcode=writer[2] if writer else None, target=target, count=count)
                    for (bank, pc, writer, target), count in sorted(returns.items(),
                        key=lambda row: (row[0][0], row[0][1], row[0][3], row[0][2] or (-1, 0)))]
    report = dict(passed=True, total_cases=cases, outcomes=dict(paths),
                  bank0_tail=dict(start=0xF866, end_exclusive=0x10000,
                                  profiles=cases + len(tail_profiles), reads_before_first_write=0,
                                  profiles_with_accesses=profiles_with_tail_accesses,
                                  word_operations=dict(word_operations),
                                  accesses=[dict(operation=op, pc=pc, address=address, count=count)
                                            for (op, pc, address), count in sorted(bank0_tail_accesses.items())]),
                  actual_frame_entry_executed=True, original_object_bank_used=True,
                  mixed_profiles=96, catalogue_profiles=len(catalogue),
                  clip_dispatches=dict(regular_clip.dispatches), clip_targets=sorted(regular_clip.targets),
                  physical_tail_model_profiles=tail_profiles,
                  physical_tail_pointer_substituted_in_9E00=True,
                  original_high_page_at_each_clip_dispatch=True, clip_alias_execution_seen=False,
                  taken_ret_count=returns.total(), ret_paths=return_paths,
                  clip_returns_from_explicit_push=sum(count for (_, _, writer, _), count in returns.items()
                                                     if writer == (0, 0xC06F, 0xD5)),
                  ret_targets_and_last_writers_of_both_stack_bytes_observed=True,
                  ret_targets_on_page_cf=0, all_game_ret_paths_proved=False,
                  checked_order_payload_stack_and_paging=True, assembly_executed=False, native_execution=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports' / report_name).write_text(payload, encoding='utf-8')
    print(payload)


def word_from_payload(payload):
    return int.from_bytes(payload[-2:], 'little')


if __name__ == '__main__':
    main()
