"""Чтение полей PLAYER при исходном подходе ракеты и подготовке большого эффекта.

Документация: ../../../Docs/ActionPanelPhysicalData.md#поля-игрока-при-ракетном-попадании
"""
from collections import Counter
from hashlib import sha256
import json

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckEffects import memory_image
from CheckIntro import ROOT
from CheckMusic import Simulator, get_registers, PC, SP
from CheckScreenUpdate import PortTrace
from ReferenceActionArrivalState import ArrivalMachine
from ReferenceControlsTextQueue import QUEUE, PRODUCER


class PlayerFieldMemory(RecordedBanks):
    watched_fields = (0xA786, 0xA792)

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if (self.recording and isinstance(address, int) and address in self.watched_fields):
            self.field_reads.append(dict(pc=self.registers[PC], address=address, value=value))
        return value


def main(report_name='ActionPlayerEffectFieldsVerification.json', inspect_adjacent=False):
    previous_report = ROOT/'Tools/Disasm/Reports/ActionArrivalStateVerification.json'
    preserved = sha256(previous_report.read_bytes()).hexdigest()
    flat = flat_action()
    assert flat[0xA786] == 0 and flat[0xA792] == 255 and flat[0xA78A] == 255
    assert bytes(flat[0xEA29:0xEA2C]) == bytes.fromhex('DD7E12')
    assert bytes(flat[0xEA6F:0xEA72]) == bytes.fromhex('DD7E12')
    assert bytes(flat[0xEA37:0xEA3A]) == bytes.fromhex('DD7E06')
    banks = [bytearray([0xA0 + page] * 0x4000) for page in range(8)]
    for page, address in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        banks[page][:] = flat[address:address + 0x4000]
    banks[1][:] = base_memory()[0xC000:]
    banks[3][:] = memory_image()[0xC000:]
    objects = (ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    assert flat[0x9E00:0x9E02] == [0, 0xC0]
    expected_header = int.from_bytes(objects[:2], 'little')
    banks[4][:len(objects)] = objects
    rom = bytes((i * 71 + 39 + (i >> 8) * 13) & 255 for i in range(0x4000))
    memory = PlayerFieldMemory(banks=banks, out7ffd=16)
    adjacent_fields = (0xA78D, 0xA78E, 0xA791, 0xA793) if inspect_adjacent else ()
    memory.watched_fields += adjacent_fields
    memory.roms = (memory.roms[0], rom)
    cpu = Simulator(memory)
    memory.registers = cpu.registers
    baseline = [bytearray(bank) for bank in banks]
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    score_read = next(row['address'] for region in flow if region['name'] == 'Action'
        for row in region['instructions'] if 0xF62C <= row['address'] < 0xF66A
        and row['operation'] == 'LD A,(IY+#12)')
    cases, examples = 0, []
    reader_counts = Counter()
    adjacent_reads, adjacent_writes = Counter(), Counter()
    for type_code in range(256):
        for notify in (0, 1):
            memory.recording = False
            for page, bank in enumerate(baseline):
                memory.banks[page][:] = bank
            memory.out7ffd(16)
            for slot in range(25):
                record = 0xA100 + slot * 64
                memory[record], memory[record + 1], memory[record + 18], memory[record + 24] = 0, 128, 16, 0
            projectile = 0xA700
            for offset in range(6):
                memory[projectile + offset] = 0
            memory[projectile + 1] = 0
            memory[projectile + 6], memory[projectile + 18] = 0, 17
            memory[projectile + 13], memory[projectile + 15], memory[projectile + 17] = 0, 0x1A, notify
            memory[projectile + 7], memory[projectile + 8], memory[projectile + 9] = 0, 0, 0
            memory[0xA740], memory[0xA741] = 128, 128
            memory[0xA792] = type_code
            memory[0x9BCE], memory[0x9BCF] = 0xFF, 0x7F
            memory.banks[1][PRODUCER & 0x3FFF] = QUEUE & 255
            memory.banks[1][(PRODUCER + 1) & 0x3FFF] = QUEUE >> 8
            for row in range(16):
                memory.banks[1][(QUEUE + row * 2) & 0x3FFF] = 128
            for row in range(8):
                memory[0xA79C + 18 * row] = 0 if row == 0 else 1
            memory[0xA82C] = 128
            memory[0x6D3D] = 0
            memory[0xBFFE], memory[0xBFFF] = 255, 63
            initial = get_registers(dict(PC=0xF57F, SP=0xBFFE, IX=projectile,
                IY=0x5C3A, HL=0x1357, DE=0x2468, BC=0x369C, AF=0xA55A,
                **{'^AF': 0x69CF, '^HL': 0x1234, '^DE': 0x5678, '^BC': 0x9ABC}), None, False)
            model = ArrivalMachine(memory.banks, initial)
            model.arrival(rom)
            cpu.registers[:] = initial
            ports = PortTrace(cpu)
            cpu.set_tracer(ports)
            memory.field_reads, memory.writes = [], []
            memory.recording = True
            returned_headers = []
            for _ in range(8000):
                if cpu.registers[PC] == 0x3FFF:
                    break
                if cpu.registers[PC] == 0xEA3D:
                    returned_headers.append(cpu.registers[6] * 256 + cpu.registers[7])
                cpu.run()
            else:
                raise AssertionError(('Нет возврата', type_code, notify))
            memory.recording = False
            assert all(model.r[i] == cpu.registers[i] for i in (*range(25), 26, 27))
            assert memory.banks == model.banks and Counter(memory.writes) == Counter(model.writes)
            assert ports.writes == model.ports and memory.o7ffd == 16 and cpu.registers[SP] == 0xC000
            type_reads = [row for row in memory.field_reads if row['address'] == 0xA792]
            model_reads = [row for row in memory.field_reads if row['address'] == 0xA786]
            assert type_reads == [dict(pc=pc, address=0xA792, value=type_code)
                                  for pc in ([score_read] if notify else []) + [0xEA29, 0xEA6F]], type_reads
            assert model_reads == [dict(pc=0xEA37, address=0xA786, value=0)], model_reads
            assert returned_headers == [expected_header]
            expected_mask = 0x40 if type_code == 8 else 0xA0
            assert memory[0xEAC4] == expected_mask
            assert [(page, offset, value) for page, offset, value in memory.writes
                    if page == 0 and offset == 0x2AC4] == [(0, 0x2AC4, expected_mask)]
            assert memory[0xA792] == type_code and memory[0xA786] == 0 and memory[0xA78A] == 255
            assert memory[0x9BCE] + memory[0x9BCF] * 256 == 0x7FFF + int(notify and type_code in (0, 5, 6, 7))
            reader_counts.update(row['pc'] for row in memory.field_reads if row['address'] in (0xA786, 0xA792))
            adjacent_reads.update((row['pc'], row['address'], row['value']) for row in memory.field_reads
                                  if row['address'] in adjacent_fields)
            adjacent_writes.update((offset + 0x8000, value) for page, offset, value in memory.writes
                                   if page == 2 and offset + 0x8000 in adjacent_fields)
            if type_code in (0, 5, 6, 7, 8, 255):
                examples.append(dict(type_code=type_code, notify=notify, field_reads=memory.field_reads,
                    path=model.path, final_rank=memory[0x9BCE] + memory[0x9BCF] * 256,
                    child_mask=expected_mask, returned_OBJECT3D_header=returned_headers[0]))
            cases += 1
    assert sha256(previous_report.read_bytes()).hexdigest() == preserved
    report = dict(passed=True, cases=cases, player_index=0x1A, player_address=0xA780,
        type_address=0xA792, model_offset_address=0xA786, original_type_code=255, original_model_offset=0,
        original_model_pointer=0xC000, original_model_header=expected_header,
        exact_ChildMask_write_and_returned_OBJECT3D_header_verified=True,
        actual_reader_counts={f'{pc:04X}': count for pc, count in sorted(reader_counts.items())},
        examples=examples, original_action_entry_and_all_called_helpers=True,
        exact_registers_flags_r_sp=True, full_eight_bank_memory_and_write_counts_compared=True,
        real_banked_queue_and_effect_executed=True, original_player_marker_preserved=True,
        target_and_near_projectile_coordinates_prepared=True, projectile_ownership_prepared=True,
        synthetic_ROM_used=True, original_type_model_and_notify_zero_profile_included=True,
        natural_reachability_of_all_mutated_type_notify_pairs_proved=False,
        original_arrival_report_sha256=preserved, original_arrival_report_unchanged=True,
        irq_executed=False, native_execution=False, assembly_executed=False)
    if inspect_adjacent:
        report['adjacent_fields'] = dict(addresses=list(adjacent_fields),
            original_bytes={f'{address:04X}': flat[address] for address in adjacent_fields},
            reads=[dict(pc=pc, address=address, value=value, count=count)
                   for (pc, address, value), count in sorted(adjacent_reads.items())],
            writes=[dict(address=address, value=value, count=count)
                    for (address, value), count in sorted(adjacent_writes.items())],
            global_unusedness_or_field_purpose_proved=False)
    (ROOT/'Tools/Disasm/Reports'/report_name).write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('512 player-target profiles: TypeCode and model offset read by original full missile/effect chain')


if __name__ == '__main__':
    main()
