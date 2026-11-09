"""Доказанная табличная роль CF08 не доказывает невозможность исполнения этих байтов."""
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionOverlappingKeyClipReturns import run_to
from CheckMusic import PC, SP, Simulator


class ClipMemory(bytearray):
    def __init__(self, data):
        super().__init__(data)
        self.table_reads = []
        self.alias_writes = []
        self.registers = None

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if self.registers is not None and isinstance(address, int):
            pc = self.registers[PC]
            if pc in (0xC068, 0xC06A, 0xC988, 0xC98A) and address != pc:
                self.table_reads.append((pc, address, value))
        return value

    def __setitem__(self, address, value):
        if self.registers is not None and isinstance(address, int) and 0xCF08 <= address < 0xCF0B:
            self.alias_writes.append((self.registers[PC], address, value))
        super().__setitem__(address, value)


def check_complete_paths(flat):
    from CheckActionOverlappingKeyClipReturns import packed_point

    overlay = (ROOT / 'Tools/Disasm/Extracted/Active/19_3DPART.C.bin').read_bytes()
    cases = []
    for use_overlay in (False, True):
        for index, x in ((8, 127), (9, 319), (10, -64)):
            for polygon in (False, True):
                memory = ClipMemory(flat)
                if use_overlay:
                    memory[0xC000:0xC000 + len(overlay)] = overlay
                inside = packed_point(127, 47, 0xF0)
                outside = packed_point(x, -64, ((index ^ 15) << 4) | index)
                if polygon:
                    memory[0x8E00:0x8E0A] = inside + outside
                    memory[0xA000:0xA002] = bytes((0, 5))
                else:
                    memory[0xCF0B:0xCF10] = inside
                    memory[0xCF1B:0xCF20] = outside
                memory[0xBFFE:0xC000] = bytes.fromhex('FF 3F')
                entry = 0xC000 if polygon else 0xC941
                cpu = Simulator(memory, {'PC': entry, 'SP': 0xBFFE, 'HL': 0xA000, 'BC': 0x0200})
                memory.registers = cpu.registers
                executed = run_to(cpu, 0x3FFF, 10000)
                assert not {0xCF08, 0xCF09, 0xCF0A} & executed
                assert not memory.alias_writes and cpu.registers[SP] == 0xC000
                indices = (index << 4, index) if polygon else (index << 4,)
                expected = []
                for selected in indices:
                    for pc, base in zip((0xC068, 0xC06A) if polygon else (0xC988, 0xC98A), (0xCF00, 0xD000)):
                        expected.append((pc, base + selected, flat[base + selected]))
                assert memory.table_reads == expected, (index, polygon, memory.table_reads)
                cases.append(dict(overlay='ThreeD' if use_overlay else 'Action', entry=entry,
                                  outside_code=index, indices=indices, table_reads=memory.table_reads,
                                  complete_return=True))
    return cases


def check_dispatch_targets(flat):
    # Для каждого исходного оверлея проверяем оба вычислителя вплоть до настоящего JP.
    overlay = (ROOT / 'Tools/Disasm/Extracted/Active/19_3DPART.C.bin').read_bytes()
    original_page = bytes(flat[0xD000:0xD100])
    assert 0xCF not in original_page
    cases = 0
    for use_overlay in (False, True):
        original = bytearray(flat)
        if use_overlay:
            original[0xC000:0xC000 + len(overlay)] = overlay
        assert original[0xD000:0xD100] == original_page
        for start, jump, depth in ((0xC058, 0xC070, 2), (0xC941, 0xC992, 6)):
            for index in range(256):
                memory = original.copy()
                memory[0xCF0F] = ((~index) & 0xF0) | 0x0F
                memory[0xCF1F] = index & 0x0F
                simulator = Simulator(memory, {'PC': start, 'SP': 0xBFFE})
                run_to(simulator, jump, 60)
                assert memory[0xD000:0xD100] == original_page
                target = memory[0xCF00 + index] | memory[0xD000 + index] << 8
                simulator.run()
                assert simulator.registers[PC] == target
                assert simulator.registers[SP] == 0xBFFE - depth
                assert target >> 8 != 0xCF
                cases += 1
    return cases, sorted(set(original_page))


def main():
    memory = flat_action()
    rows = json.loads((ROOT/'Tools/Disasm/Reports/ActionClipDispatchTable.json').read_text('utf-8'))['rows']
    # Проверка исходных байтов и действительных обращений диспетчера к младшей странице таблицы.
    assert bytes(memory[0xCF08:0xCF0B]) == bytes((0xF3, 0xAF, 0xC9))
    selected = []
    for index in (8, 9, 10):
        row = next(row for row in rows if row['index'] == index)
        assert row['target'] == memory[0xCF00+index]+256*memory[0xD000+index]
        selected.append(dict(index=index, low_address=0xCF00+index, low_byte=memory[0xCF00+index],
                             target=row['target'], target_path=row['path']))
    # Ищем все явно заданные адреса внутри трёх байтов во всех разобранных областях.
    flow = json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    targets = ('#CF08', '#CF09', '#CF0A')
    references = [dict(region=region['name'], address=item['address'], operation=item['operation'])
                  for region in flow for item in region['instructions']
                  if any(target in item['operation'] for target in targets)]
    assert not references, references
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    raw_words = {f'{address:04X}': [offset for offset in range(len(disk) - 1)
                                 if disk[offset] == address & 255 and disk[offset + 1] == address >> 8]
                 for address in range(0xCF08, 0xCF0B)}
    manifest = json.loads((ROOT / 'Tools/Disasm/Disk/Manifest.json').read_bytes())['entries']
    deleted = next(entry for entry in manifest if entry['slot'] == 0)
    assert deleted['deleted'] and raw_words == {'CF08': [0x4167, 0x9A62], 'CF09': [0x259B], 'CF0A': [0xE35B]}
    assert all(deleted['offset'] + deleted['length'] <= offset < deleted['offset'] + deleted['allocated_length']
               for offsets in raw_words.values() for offset in offsets)
    dispatch_cases, high_bytes = check_dispatch_targets(memory)
    complete_paths = check_complete_paths(memory)
    report = dict(passed=True, region='Action', bank=0, address=0xCF08, bytes=[0xF3, 0xAF, 0xC9],
                  valid_lookup_entries=selected, table_role_proved=True,
                  decoded_regions=len(flow), decoded_instructions=sum(len(r['instructions']) for r in flow),
                  explicit_references_to_cf08_cf0a=references,
                  raw_words_disk_offsets=raw_words, all_raw_words_in_deleted_sector_tail=True,
                  original_high_table_bytes=high_bytes, target_exclusion_cases=dispatch_cases,
                  complete_paths=complete_paths,
                  page_cf_unreachable_via_both_clip_dispatchers_with_original_high_table=True,
                  possible_instructions=['DI', 'XOR A', 'RET'], execution_entry_proved=False,
                  nonexecution_proved=False, unknown_status_preserved=True,
                  source_bytes_changed=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipTableAliasVerification.json').write_bytes(
        (json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
