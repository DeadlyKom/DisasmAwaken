"""Квалифицированные писатели LinkFlags, исходные байты и все значения флагового байта.

Документация: ../../../Docs/ActionLinkFlagWrites.md
Документация: ../../../Docs/ActionObjectRecords.md
"""
from collections import Counter
from hashlib import sha256
import json
import re

from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator, get_registers, PC
from SourcePresentation import instructions
from VerifySources import structure_symbols

INDIRECT = {'CreateLinkedMissileRecord': 0x613B, 'ApplyPendingRecordLink': 0x6365}
BITS = {'ActionLinkFlagsConst.BackLinkBit': 0, 'ActionArrivalConst.RocketAttackBit': 1,
        'ActionArrivalConst.RocketHitBit': 2, 'ActionLinkFlagsConst.AntimissileBit': 3}


class WriteMemory(bytearray):
    recording = False

    def __setitem__(self, address, value):
        if self.recording:
            assert isinstance(address, int)
            self.writes.append((address, value))
        super().__setitem__(address, value)


def zero_origin(rows, index):
    """Локальное доказательство A=0, между XOR и записью разрешены только сохраняющие A присваивания."""
    for previous in range(index - 1, -1, -1):
        operation = re.sub(r'\s', '', rows[previous]['operation'])
        if operation == 'XORA':
            return dict(xor_pc=rows[previous]['address'], sequential_fragment_required=True,
                        instructions_before_store=index - previous,
                        original_hex=''.join(row['hex'] for row in rows[previous:index + 1]))
        assert re.fullmatch(r'LD\(I[XY]\+#[0-9A-F]{2}\),(A|#[0-9A-F]+)', operation), operation
    raise AssertionError('Перед записью LinkFlags из A не доказан XOR A')


def collect(disk, entries):
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    functions = json.loads((ROOT / 'Tools/Disasm/Reports/Functions.json').read_bytes())
    views = {region['name']: region for region in flow}
    writers, readers = [], []
    # Проверка соответствия каждого символизованного операнда физическому представлению инструкции.
    for function in functions:
        text = (ROOT / function['path']).read_text(encoding='utf-8-sig')
        operations = instructions(text)
        selected = [i for i, operation in enumerate(operations)
                    if 'FActionRecord.LinkFlags' in operation and not operation.startswith('LD BC,')]
        if function['name'] in INDIRECT:
            selected += [i for i, operation in enumerate(operations)
                         if operation.startswith('SET ') and '(HL)' in operation]
        if not selected:
            continue
        rows = [row for row in views[function['region']]['instructions']
                if row['slot'] == function['slot'] and function['offset'] <= row['offset'] < function['end_offset']]
        assert len(rows) == len(operations)
        # Проверка всех байтов процедуры, включая фрагменты происхождения A и адреса через HL.
        for row in rows:
            origin = entries[row['slot']]['offset'] + row['offset']
            data = bytes.fromhex(row['hex'])
            assert disk[origin:origin + len(data)] == data
        for index in selected:
            row, source = rows[index], operations[index]
            operation = re.sub(r'\s', '', row['operation'])
            item = dict(path=function['path'], function=function['name'], region=function['region'],
                pc=row['address'], slot=row['slot'], offset=row['offset'], source_operation=source,
                original_operation=row['operation'], original_hex=row['hex'])
            if match := re.fullmatch(r'SET([0-7]),\((I[XY]\+#0C|HL)\)', operation):
                bit, operand = int(match[1]), match[2]
                assert bit in (0, 1, 2, 3)
                name = re.fullmatch(r'SET\s+@([A-Za-z0-9_.]+),\s*\(.+\)', source)[1]
                assert BITS[name] == bit
                if operand == 'HL':
                    assert row['address'] == INDIRECT[function['name']]
                    previous = [re.sub(r'\s', '', value['operation']) for value in rows[:index]]
                    if function['name'] == 'ApplyPendingRecordLink':
                        assert previous[-2:] == ['LDBC,#000C', 'ADDHL,BC']
                        item['address_precondition'] = 'HL_from_aligned_PendingRecord_plus_0C'
                    else:
                        assert previous[-4:] == ['CALL#E6A7', 'LDA,L', 'ADDA,#0C', 'LDL,A']
                        assert operations[index - 4] == 'CALL @Action.RecordIndexToAddress.Entry'
                        item['address_precondition'] = 'RecordIndexToAddress_then_low_byte_plus_0C_without_carry'
                item.update(kind='set_bit', bit=bit, operand=operand)
                writers.append(item)
            elif match := re.fullmatch(r'LD\((I[XY])\+#0C\),(A|#00)', operation):
                item.update(kind='clear_byte', operand=match[1] + '+#0C')
                if match[2] == 'A':
                    item['A_origin'] = zero_origin(rows, index)
                    # Проверка отказа доказательства при неизвестном A и при его перезаписи после XOR.
                    origin = index - item['A_origin']['instructions_before_store']
                    for changed, replacement in ((origin, 'OR A'), (index - 1, 'LD A,#FF')):
                        altered = list(rows)
                        altered[changed] = dict(rows[changed], operation=replacement)
                        try:
                            zero_origin(altered, index)
                        except AssertionError:
                            pass
                        else:
                            raise AssertionError('Принято недоказанное нулевое A')
                    item['A_origin']['negative_controls_rejected'] = 2
                else:
                    item['literal_zero'] = True
                writers.append(item)
            else:
                assert operation in ('LDA,(IX+#0C)', 'BIT3,(IX+#0C)'), operation
                readers.append(item)
    assert len(writers) == 17 and len(readers) == 2
    assert Counter(row['kind'] for row in writers) == {'clear_byte': 10, 'set_bit': 7}
    assert sum('A_origin' in row for row in writers) == 3
    return writers, readers


def main():
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entries = {entry['slot']: entry for entry in manifest['entries']}
    assert structure_symbols()['FACTIONRECORD.LINKFLAGS'] == 12
    # Проверка четырёх именованных разрядов в фактических константах проекта.
    constants = (ROOT / 'Includes/Const/Include.inc').read_text(encoding='utf-8-sig')
    for name, expected in BITS.items():
        module, field = name.split('.')
        block = re.search(r'\bmodule\s+' + module + r'\b(.*?)\bendmodule\b', constants, re.S)[1]
        match = re.search(r'^' + field + r'\s+equ\s+#([0-9A-F]+)\b', block, re.M)
        assert match and int(match[1], 16) == expected
    writers, readers = collect(disk, entries)
    original = bytearray(flat_action())
    # Проверка наблюдателя записи отдельной реальной инструкцией CPU.
    probe = WriteMemory(original)
    probe[0x4000:0x4003] = bytes.fromhex('320ca1')
    cpu = Simulator(probe)
    cpu.registers[PC], cpu.registers[0] = 0x4000, 0x6B
    probe.writes, probe.recording = [], True
    cpu.run()
    assert probe.writes == [(0xA10C, 0x6B)]
    counts = Counter()
    # Проверка каждого исходного писателя на всех байтах и трёх физических слотах.
    for writer in writers:
        pc = writer['pc']
        data = bytes.fromhex(writer['original_hex'])
        assert original[pc:pc + len(data)] == data
        for slot in (0, 12, 24):
            base = 0xA100 + 64 * slot
            address = base + 12
            for value in range(256):
                memory = WriteMemory(original)
                memory[address] = value
                cpu = Simulator(memory)
                initial = get_registers(dict(PC=pc, HL=address, DE=0x1357, BC=0x2468,
                    AF=0x0044, IX=base, IY=base, SP=0xBFFE), None, False)
                cpu.registers[:] = initial
                memory.writes, memory.recording = [], True
                cpu.run()
                memory.recording = False
                expected = 0 if writer['kind'] == 'clear_byte' else value | (1 << writer['bit'])
                assert memory.writes == [(address, expected)] and memory[address] == expected
                assert cpu.registers[PC] == pc + len(data)
                assert all(cpu.registers[i] == initial[i] for i in (*range(15), *range(16, 24), 26, 27))
                if writer['kind'] == 'set_bit':
                    assert (expected & 0xF0) == (value & 0xF0)
                counts[writer['kind']] += 1
    assert sum(counts.values()) == 13056
    result = dict(passed=True, original_disk_sha256=manifest['sha256'],
        source_map_sha256=sha256((ROOT / 'Tools/Disasm/Reports/SourceMap.json').read_bytes()).hexdigest(),
        qualified_writer_sites=17, named_indexed_reader_sites=2, writers=writers, readers=readers,
        bit_constants=BITS, cases=sum(counts.values()), case_counts=dict(counts),
        all_256_old_flag_bytes=True, record_slots=[0, 12, 24],
        CPU_write_probe_passed=True, single_writer_exact_write_and_preserved_registers_checked=True,
        R_T_and_bus_cycle_sequence_not_independently_checked=True,
        SET_writers_preserve_high_four_bits=True, zero_writers_clear_entire_byte=True,
        three_A_writers_have_local_XOR_zero_provenance=True,
        A_zero_provenance_negative_controls_rejected=6,
        A_proof_requires_sequential_fragment_without_middle_entry_or_interference=True,
        indirect_HL_proof_requires_documented_record_base_or_index=True,
        flat_single_instruction_execution_without_banking_or_parent_calls=True,
        other_indirect_block_stack_generated_or_ROM_writers_excluded=False,
        global_runtime_writer_graph_complete=False, high_bit_native_origin_or_game_meaning_proved=False,
        IRQ_executed=False, assembly_executed=False, native_execution=False)
    target = ROOT / 'Tools/Disasm/Reports/ActionLinkFlagWritesVerification.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, sites=17, cases=result['cases'], counts=dict(counts))))


if __name__ == '__main__':
    main()
