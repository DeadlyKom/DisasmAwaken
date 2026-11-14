"""9F1C, отсутствие чтений прежнего буфера при копировании всех исходных моделей."""
from collections import Counter
import json
import re
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckActionObjectCopy import packet
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from SpawnPhysicalRows import TABLES as SPAWN_TABLES
from TraceFlight import main as trace_flight
from skoolkit.simutils import A, L


class TrackedStorage(RecordedBanks):
    targets=set()
    written=set()
    old_reads=[]
    def __getitem__(self,index):
        if self.recording and isinstance(index,int) and index in self.targets and index not in self.written:
            self.old_reads.append(index)
        return super().__getitem__(index)
    def __setitem__(self,index,value):
        if self.recording and isinstance(index,int) and index in self.targets:self.written.add(index)
        super().__setitem__(index,value)


class FlightModelMemory(RecordedBanks):
    registers = None
    model_fields = frozenset(range(0xA106, 0xA746, 64))

    def __init__(self):
        super().__init__(out7ffd=0x10)
        self.model_writes = Counter()
        self.table_writes = Counter()

    def __setitem__(self, address, value):
        if self.registers is not None:
            pc = self.registers[PC]
            if address in self.model_fields:
                self.model_writes[pc, address, value] += 1
            if 0x9E00 <= address < 0x9F00:
                self.table_writes[pc, address, value] += 1
        super().__setitem__(address, value)


def check_model_offsets_during_flight():
    memory = FlightModelMemory()
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    put(memory, 0x6000, source)
    boot = Simulator(memory, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A},
                     config={'fast_ldir': False, 'fast_djnz': False})
    memory.registers = boot.registers
    indices = {0xAACC: Counter(), 0xAAE2: Counter()}

    def observe(_, __, registers):
        pc = registers[PC]
        if pc in indices:
            indices[pc][registers[A if pc == 0xAACC else L]] += 1

    flight = trace_flight(['--frames', '65'], boot_simulator=boot, save_reports=False,
                          instruction_observer=observe)
    assert flight['reason'] == 'requested_frame_entries' and flight['frame_entries'] == 65
    assert not memory.table_writes
    assert memory.model_writes and {pc for pc, _, _ in memory.model_writes} == {0x78EC}
    assert all(not value & 1 for _, _, value in memory.model_writes)
    assert indices[0xAACC] and all(not value & 1 for counts in indices.values() for value in counts), indices
    return dict(frame_entries=65, trdos_stub=True, keys_pressed=False, model_table_writes=0,
                record_writes=[dict(pc=pc, address=address, value=value, count=count)
                               for (pc, address, value), count in sorted(memory.model_writes.items())],
                consumer_indices={f'{pc:04X}': dict(sorted(counts.items())) for pc, counts in indices.items()})


def check_indexed_model_writers(physical, copy_lengths):
    regions = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    relevant = {'Action', 'ActionBoot', 'Controls', 'ThreeD', 'Voxel'}
    indexed = r'\(I[XY]\s*\+\s*#06\)'
    writes = re.compile(rf'(?:LD {indexed},.*|(?:INC|DEC|RL|RR|RLC|RRC|SLA|SLL|SRA|SRL) {indexed}|(?:SET|RES) .*,{indexed})')
    actual = {(region['name'], row['address']): row['operation']
              for region in regions if region['name'] in relevant for row in region['instructions']
              if writes.fullmatch(row['operation'])}
    values = {
        0x6106: [0x90],
        0x61DA: [0xC0],
        0x6472: [0x98],
        0x78EC: physical['distinct_values']['template_rows'],
        0x79DF: sorted({((raw & 0x1C) | 0x40) + bias for raw in range(256) for bias in (0, 0x20)}),
        0x7BF6: physical['distinct_values']['class_choices'],
        0xE8D1: [0x88, 0x8C],
        0xF44B: [0x10 + 4 * region for region in range(4)],
    }
    other = {('Action', 0x6918): 'FActionWideVector.Component1.Byte2',
             ('Voxel', 0xEC57): 'FVisualEffect.Mode'}
    assert set(actual) == {('Action', address) for address in values} | set(other)
    action = {row['address']: row['operation'] for region in regions if region['name'] == 'Action'
              for row in region['instructions']}
    for address in (0x6106, 0x61DA, 0x6472):
        assert action[address].endswith(f',#{values[address][0]:02X}')
    assert [action[address] for address in (0x79BA, 0x79BE, 0x79C0, 0x79D9, 0x79DB, 0x79DD)] == [
        'LD A,#20', 'LD A,#00', 'LD (#79DE),A', 'AND #1C', 'OR #40', 'ADD A,#00']
    assert [action[address] for address in (0xF444, 0xF447, 0xF448, 0xF449)] == [
        'CALL #6E2B', 'RLCA', 'RLCA', 'ADD A,#10']
    assert [action[address] for address in (0xE8C8, 0xE8CF, 0xEAA3, 0xEAA5)] == [
        'LD C,#88', 'LD C,#8C', 'LD A,#B8', 'LD (DE),A']
    mutations = json.loads((ROOT / 'Tools/Disasm/Reports/ModifiedCode.json').read_bytes())
    assert {row['writer'] for row in mutations if row['region'] == 'Action' and row['target'] == 0x79DE} == {0x79C0}
    known_indices = set(physical['distinct_values']['initial_records']) | {0xB8}
    known_indices.update(value for group in values.values() for value in group)
    assert all(not value & 1 for value in known_indices)
    maximum = max(copy_lengths[value] for value in known_indices)
    return dict(indexed_record_writers=[dict(pc=address, operation=action[address], values=group)
                                        for address, group in sorted(values.items())],
                other_indexed_writers=[dict(region=region, pc=pc, field=field)
                                       for (region, pc), field in other.items()],
                known_indirect_record_writer=dict(pc=0xEAA5, operation=action[0xEAA5], value=0xB8),
                known_indices=sorted(known_indices), maximum_copy_bytes_from_initial_table=maximum,
                maximum_copy_indices=sorted(value for value in known_indices if copy_lengths[value] == maximum),
                arbitrary_indirect_writers_audited=False)


def check_extended_original_copies(flat, objects, baseline):
    origin = 0xC000
    buffer = 0x9F1C
    even_copy_end = 0xA00A
    next_resource = 0xA01C
    odd_cases, odd_outside_file, tail_cases = [], [], []

    def execute(index, pointer, original_pointer_address=None):
        data, fixed, lengths = packet(objects, pointer - origin)
        end = buffer + len(data)
        assert end <= next_resource
        memory = TrackedStorage(banks=[bank.copy() for bank in baseline], out7ffd=16)
        if original_pointer_address is not None:
            memory[0x9E00] = flat[original_pointer_address]
            memory[0x9E01] = flat[original_pointer_address + 1]
        memory[0xBFFE], memory[0xBFFF] = 0xFF, 0x3F
        memory.targets = set(range(buffer, next_resource))
        memory.written, memory.old_reads, memory.writes = set(), [], []
        sim = Simulator(memory)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        sim.registers[:] = get_registers({'PC': 0xAAE2, 'SP': 0xBFFE, 'HL': index}, None, False)
        memory.recording = True
        sim.run(0xAAE2, 0x3FFF)
        memory.recording = False
        assert (sim.registers[PC], sim.registers[SP], memory.o7ffd) == (0x3FFF, 0xC000, 0x10)
        assert trace.writes == [(0x7FFD, 0x14), (0x7FFD, 0x10)]
        assert not memory.old_reads and memory.written == set(range(buffer, end))
        actual = [(offset + 0x8000, value) for bank, offset, value in memory.writes
                  if bank == 2 and offset + 0x8000 in memory.targets]
        assert actual == list(enumerate(data, buffer))
        assert bytes(memory[end:next_resource]) == bytes(flat[end:next_resource])
        assert bytes(memory.banks[4][:len(objects)]) == objects
        return dict(index=index, pointer=pointer, size=len(data), destination_end=end,
                    fixed_records=fixed, variable_records=len(lengths),
                    extra_destination_bytes=max(0, end - even_copy_end))

    for index in range(1, 256, 2):
        pointer = flat[0x9E00 + index] | flat[0x9E00 + ((index + 1) & 255)] << 8
        if origin <= pointer < origin + len(objects):
            odd_cases.append(execute(index, pointer))
        else:
            odd_outside_file.append(dict(index=index, pointer=pointer))
    for address in range(0x9F00, 0x9F1C, 2):
        pointer = flat[address] | flat[address + 1] << 8
        tail_cases.append(dict(execute(0, pointer, address), physical_pointer_address=address))
    assert len(odd_cases) == 20 and len(odd_outside_file) == 108 and len(tail_cases) == 14
    assert max(row['destination_end'] for row in odd_cases) == 0xA016
    assert max(row['destination_end'] for row in tail_cases) == 0xA017
    return dict(original_odd_entries_in_file=odd_cases, odd_entries_outside_logical_file=odd_outside_file,
                physical_tail_pointer_fixtures=tail_cases, game_reachability_proved=False,
                bytes_compared_in_original_order=True)


def check_odd_entries_after_flight_boot():
    buffer, candidate_list, first_record = 0x9F1C, 0xA01C, 0xA100
    stack = 0x5FFE
    source = (ROOT / 'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    original = TrackedStorage(out7ffd=0x10)
    put(original, 0x6000, source)
    boot = Simulator(original, {'PC': 0x6000, 'SP': 0x5FFF, 'IY': 0x5C3A})
    flight = trace_flight(['--frames', '2'], boot_simulator=boot, save_reports=False)
    assert flight['reason'] == 'requested_frame_entries'
    assert original.o7ffd == 0x10 and boot.registers[PC] == 0xA85E
    original.out7ffd(0x14)
    snapshot = bytes(original[0:0x10000])
    cases = []
    for index in range(1, 256, 2):
        pointer = snapshot[0x9E00 + index] | snapshot[0x9E00 + ((index + 1) & 255)] << 8
        raw, _, _ = packet(snapshot, pointer)
        end = buffer + len(raw)
        assert end <= pointer or pointer + len(raw) <= buffer
        assert pointer >= stack + 2 or pointer + len(raw) <= stack - 4
        memory = TrackedStorage(banks=[bytearray(bank) for bank in original.banks], out7ffd=0x10)
        put(memory, stack, (0xFF, 0x3F))
        memory.targets = set(range(buffer, first_record + 1))
        memory.written, memory.old_reads, memory.writes = set(), [], []
        cpu = Simulator(memory, {'PC': 0xAAE2, 'SP': stack, 'HL': index})
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.recording = True
        for _ in range(10000):
            if cpu.registers[PC] == 0x3FFF or first_record in memory.written:
                break
            cpu.run()
        else:
            raise AssertionError((index, pointer, cpu.registers[PC]))
        memory.recording = False
        stopped = end > first_record
        written = raw[:first_record + 1 - buffer]
        written_addresses = set(range(buffer, buffer + len(written)))
        assert memory.written == written_addresses and written_addresses.isdisjoint(memory.old_reads), (
            hex(index), hex(pointer), len(written), len(memory.written), memory.old_reads[:8])
        actual = [(offset + 0x8000, value) for bank, offset, value in memory.writes
                  if bank == 2 and offset + 0x8000 in memory.targets]
        assert actual == list(enumerate(written, buffer))
        if stopped:
            assert memory.o7ffd == 0x14 and ports.writes == [(0x7FFD, 0x14)]
        else:
            assert (cpu.registers[PC], cpu.registers[SP]) == (0x3FFF, stack + 2)
            assert ports.writes == [(0x7FFD, 0x14), (0x7FFD, 0x10)]
        cases.append(dict(index=index, source=pointer, predicted_bytes=len(raw), checked_bytes=len(written),
                          reached_candidate_list=end > candidate_list,
                          source_reads_in_gap_after_candidate_list=sorted({
                              address for address in memory.old_reads if 0xA027 <= address < first_record}),
                          stopped_at_first_record_byte=stopped))
    return dict(cases=cases, snapshot_frame_entry=2, original_table_unchanged=True,
                forced_odd_input_indices=True, game_use_proved=False, trdos_stub=True)


def check_physical_model_offsets(flat):
    def word(address):
        return flat[address] | flat[address + 1] << 8

    template_start, template_end = SPAWN_TABLES[0][:2]
    choice_start, choice_end = SPAWN_TABLES[1][:2]
    templates = [word(template_start + 2 * seed) for seed in range(16)]
    choices = [word(choice_start + 2 * code) for code in range(9)]
    assert all(template_start + 32 <= row < template_end - 7 for row in templates)
    assert all(choice_start + 18 <= row <= choice_end - 16 for row in choices)
    values = dict(initial_records=[flat[record + 6] for record in range(0xA100, 0xA740, 64)],
                  template_rows=[flat[row + 6] for row in templates],
                  class_choices=[flat[row + 2 * variant] for row in choices for variant in range(8)])
    assert all(value & 1 == 0 for group in values.values() for value in group)
    return dict(source_counts={name: len(group) for name, group in values.items()},
                distinct_values={name: sorted(set(group)) for name, group in values.items()},
                all_source_bytes_even=True, other_runtime_writers_proved=False)


def main():
    previous=json.loads((ROOT/'Tools/Disasm/Reports/ActionObjectCopyVerification.json').read_text('utf-8'))
    assert previous['passed']
    flat=flat_action();objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks=[bytearray([160+i]*16384) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[4][:len(objects)]=objects
    memory=TrackedStorage(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks]
    simulator=Simulator(memory);counts=Counter();union=set();lengths={}
    for index in range(0,256,2):
        pointer=flat[0x9E00+index]+256*flat[0x9E01+index]
        data,_,_=packet(objects,pointer-0xC000);lengths[index]=len(data)
        for pattern in (None,0,255,165):
            memory.recording=False
            for bank in range(8):memory.banks[bank][:]=baseline[bank]
            memory.out7ffd(16)
            if pattern is not None:
                for address in range(0x9F1C,0xA00A):memory[address]=pattern
            memory[0xBFFE],memory[0xBFFF]=255,63
            initial=get_registers({'PC':0xAAE2,'SP':0xBFFE,'AF':0xA55A,'HL':0x1300|index,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
            memory.targets=set(range(0x9F1C,0x9F1C+len(data)));memory.written=set();memory.old_reads=[]
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.writes=[];memory.recording=True
            simulator.run(start=0xAAE2,stop=0x3FFF);memory.recording=False
            assert not memory.old_reads,(index,pattern,memory.old_reads)
            assert memory.written==memory.targets,(index,pattern)
            assert bytes(memory[0x9F1C:0x9F1C+len(data)])==data
            assert trace.writes==[(0x7FFD,20),(0x7FFD,16)] and memory.o7ffd==16
            union.update(memory.written);counts[str(pattern)]+=1
    assert union==set(range(0x9F1C,0xA00A)) and max(lengths.values())==238
    extended = check_extended_original_copies(flat, objects, baseline)
    physical = check_physical_model_offsets(flat)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),all_128_original_even_pointer_entries=True,
        actual_original_copy_and_bank_switching_executed=True,buffer_start=0x9F1C,maximum_original_copy_bytes=238,
        maximum_original_end_exclusive=0xA00A,read_of_initial_byte_before_first_write=False,
        generated_or_copied_values_not_serialized=True,original_buffer_bytes_preserved=True,
        extended_original_copies=extended,
        odd_snapshot=check_odd_entries_after_flight_boot(),
        physical_model_offsets=physical,
        indexed_model_writers=check_indexed_model_writers(physical, lengths),
        flight_model_offsets=check_model_offsets_during_flight(),
        storage_capacity_for_arbitrary_streams_proved=False,first_reads_in_arbitrary_other_phases_proved=False,
        subsequent_render_consumers_executed_in_this_test=False,assembly_executed=False,irq_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionObjectStreamStorageVerification.json'
    temporary=target.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(target)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
