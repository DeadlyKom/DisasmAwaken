"""Перебор старших битов кода квадранта, трасса команд, адресов памяти и независимый растр.

Документация: ../../../Docs/ArcWorkspace.md#раздельное-влияние-старших-битов-на-af
"""
from collections import Counter
import json

from CheckArcDispatcher import ROOT, Simulator, get_registers, make_context, reference
from skoolkit.simutils import D, E, H, L, PC


FLAG_CHAIN = ((0xE05F, '3AADDF', 'LD A,(#DFAD)'),
              (0xE062, 'CB47', 'BIT 0,A'),
              (0xE064, 'CC8FE6', 'CALL Z,#E68F'),
              (0xE68F, 'F5', 'PUSH AF'),
              (0xE496, 'F1', 'POP AF'),
              (0xE497, 'C9', 'RET'),
              (0xE067, 'C481E6', 'CALL NZ,#E681'),
              (0xE06A, 'C9', 'RET'))


class TraceMemory(list):
    recording = False

    def __getitem__(self, index):
        if self.recording:
            if isinstance(index, int):
                self.reads.append(index)
            else:
                self.reads.extend(range(*index.indices(65536)))
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        if self.recording:
            if isinstance(index, int):
                self.writes.append(index)
            else:
                self.writes.extend(range(*index.indices(65536)))
        super().__setitem__(index, value)


def main(report_name='ArcQuadrantHighBitsVerification.json', record_bit_influence=False):
    _, source, banks = make_context()
    memory = TraceMemory([0] * 65536)
    memory[0x4000:0x8000], memory[0x8000:0xC000] = banks[5], banks[2]
    memory[0xC000:0xC000 + len(source)] = source
    memory[0x7FFE:0x8000] = [255, 63]
    cpu = Simulator(memory)
    initial = get_registers(dict(SP=0x7FFE, HL=0x1357, DE=0x247A, BC=0x36C9,
                                AF=0x5A5D, IX=0x2468, IY=0x5C3A,
                                **{'^AF': 0x69CF, '^HL': 0x369C,
                                   '^DE': 0x47AD, '^BC': 0x58BE}), None, False)
    cpu.registers[:] = initial
    cpu.registers[D] = cpu.registers[E] = 0
    cpu.run(start=0xC49B, stop=0x3FFF)
    counts = Counter()
    register_differences, memory_differences = set(), set()
    bit_influence = {bit: dict(cases=0, cases_with_returned_difference=0,
        returned_register_xor_masks={}, written_memory_xor_masks={}) for bit in range(2, 8)}
    for width, height in ((16, 24), (64, 64)):
        cpu.registers[:] = initial
        cpu.registers[H], cpu.registers[L] = height - 1, width - 1
        cpu.registers[D] = cpu.registers[E] = 0
        cpu.run(start=0xD0C3, stop=0x3FFF)
        prepared = memory.copy()
        for radius, x, y in ((8, 0, 0), (40, 0, 0), (80, 0, 48),
                             (80, 48, 0), (80, 48, 48), (255, 32, 32)):
            for mode in (0x30, 0x38):
                for quadrant in range(4):
                    baseline = None
                    baseline_registers, baseline_values = None, None
                    expected, fields, path = reference(bytes([0xA7]) * 0x1B00,
                                                       radius, x, y, quadrant, mode, width, height)
                    for high in range(64):
                        code = quadrant | (high << 2)
                        memory.recording = False
                        memory[:] = prepared
                        memory[0x4000:0x5B00] = [0xA7] * 0x1B00
                        memory[0xDFAB:0xDFAF] = [y, x, code, radius]
                        memory[0xDFAF:0xDFB4] = [0xA7] * 5
                        memory[0xDFB6:0xDFBA] = [0xA7] * 4
                        memory[0xDFC4] = 1 if mode == 0x38 else 0
                        cpu.registers[:] = initial
                        cpu.registers[PC] = 0xDFC3
                        memory.reads, memory.writes = [], []
                        memory.recording = True
                        commands = []
                        for _ in range(100000):
                            if cpu.registers[PC] == 0x3FFF:
                                break
                            commands.append(cpu.registers[PC])
                            cpu.run()
                        else:
                            raise AssertionError(('Не завершён диспетчер', width, height, radius, x, y, code))
                        memory.recording = False
                        assert bytes(memory[0x4000:0x5B00]) == expected
                        trace = (commands, memory.reads, memory.writes)
                        if baseline is None:
                            baseline = trace
                            baseline_registers = list(cpu.registers)
                            baseline_values = {address: memory[address] for address in set(memory.writes)}
                        assert trace == baseline, (width, height, radius, x, y, code, mode)
                        register_differences.update(i for i, value in enumerate(cpu.registers) if value != baseline_registers[i])
                        memory_differences.update(address for address, value in baseline_values.items() if memory[address] != value)
                        # Сравнение отдельных старших разрядов с тем же кодом без старших разрядов.
                        if record_bit_influence and high in (1, 2, 4, 8, 16, 32):
                            effect = bit_influence[high.bit_length() + 1]
                            effect['cases'] += 1
                            changed = False
                            for index, value in enumerate(cpu.registers):
                                delta = value ^ baseline_registers[index]
                                if delta:
                                    changed = True
                                    key = str(index)
                                    effect['returned_register_xor_masks'][key] = effect['returned_register_xor_masks'].get(key, 0) | delta
                            effect['cases_with_returned_difference'] += int(changed)
                            if changed and 'first_difference' not in effect:
                                effect['first_difference'] = dict(width=width,height=height,radius=radius,
                                    abs_x=x,abs_y=y,low_quadrant=quadrant,mode=mode,
                                    baseline_AF=baseline_registers[:2],actual_AF=list(cpu.registers[:2]),
                                    last_instruction_addresses=commands[-24:],
                                    flag_restore_chain=[pc for pc in commands if pc in {row[0] for row in FLAG_CHAIN}][-len(FLAG_CHAIN):])
                            for address, value in baseline_values.items():
                                delta = memory[address] ^ value
                                if delta:
                                    key = f'{address:04X}'
                                    effect['written_memory_xor_masks'][key] = effect['written_memory_xor_masks'].get(key, 0) | delta
                        assert memory[0xDFAD] == code
                        counts[path] += 1
    report = dict(passed=True, cases=counts.total(), paths=dict(counts),
                  window_profiles=[[16, 24], [64, 64]], all_256_quadrant_bytes=True,
                  command_read_address_write_address_traces_identical_with_same_low_bits=True,
                  independent_bitmap_and_attributes_checked=True, original_code_byte_preserved=True,
                  changed_register_indices=sorted(register_differences),
                  changed_written_memory_addresses=sorted(memory_differences),
                  full_register_and_stack_byte_equality_claimed=False,
                  all_geometries_proved=False, original_0f_initializer_purpose_proved=False,
                  irq_executed=False, native_execution=False, assembly_executed=False)
    if record_bit_influence:
        assert all(effect['cases'] == 96 for effect in bit_influence.values())
        # Проверка точного эффекта каждого разряда, включая недокументированные флаги BIT.
        for bit, effect in bit_influence.items():
            mask=1<<bit
            expected_registers={'0':mask}
            expected_memory={'7FFB':mask}
            if bit in (3,5):
                expected_registers['1']=mask
                expected_memory['7FFA']=mask
            assert effect['returned_register_xor_masks']==expected_registers
            assert effect['written_memory_xor_masks']==expected_memory
            assert effect['cases_with_returned_difference']==80
            witness=effect['first_difference']
            assert witness['flag_restore_chain']==[row[0] for row in FLAG_CHAIN], (bit,witness['flag_restore_chain'])
            assert witness['baseline_AF']==[0,0x54]
            assert witness['actual_AF']==[mask,0x54|(mask&0x28)]
        # Сверка причинной цепочки BIT и сохранения AF с оригинальным машинным KARTA.
        for address, raw, operation in FLAG_CHAIN:
            expected=bytes.fromhex(raw)
            assert bytes(source[address-0xC000:address-0xC000+len(expected)])==expected
        report['single_high_bit_influence'] = bit_influence
        report['first_witness_flag_chain']=[dict(address=pc,hex=raw,operation=op) for pc,raw,op in FLAG_CHAIN]
        report['register_index_names'] = {'0': 'A', '1': 'F'}
        report['compared_memory_values_scope'] = 'addresses_written_during_dispatcher_not_unchanged_input_QuadrantCode'
        report['global_high_bit_purpose_proved'] = False
    (ROOT / 'Tools/Disasm/Reports' / report_name).write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
