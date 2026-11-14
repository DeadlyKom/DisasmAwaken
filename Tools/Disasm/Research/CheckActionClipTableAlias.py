"""Доказанная табличная роль CF08 не доказывает невозможность исполнения этих байтов."""
import json
import re
from collections import Counter
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionOverlappingKeyClipReturns import run_to
from CheckMusic import PC, SP, Simulator


FIXED_TEMPORARY_WINDOW = range(0x5DA0, 0x5F5D)
BANKED_TEMPORARY_WINDOW = range(0xDADE, 0xDC9B)


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
    selected = set()
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
                selected.add(target)
                cases += 1
    return cases, sorted(set(original_page)), selected


def check_object_dispatch_targets(flat):
    cases = []
    targets = {}
    entries = (
        ('DispatchRecordClass', 0x64DF, 0x64EF, 0x64F0, 0x12, 0),
        ('DispatchObjectState.CallHandler', 0xF843, 0xF85D, 0xEF50, 0x0A, 4),
        ('HandleLinkedTargetState.SelectSaved', 0xF168, 0xF175, 0xEF50, None, 0),
        ('HandleLinkedPhaseState.SelectSaved', 0xF2B9, 0xF2C6, 0xEF50, None, 0),
    )
    for name, entry, jump, table, field, stack_bytes in entries:
        selected = set()
        # Проверка полного байтового домена, включая чтения за физическим концом обеих таблиц.
        for code in range(256):
            memory = flat.copy()
            if field is not None:
                memory[0xA100 + field] = code
            cpu = Simulator(memory, {'PC': entry, 'SP': 0xBFFE, 'IX': 0xA100, 'AF': code << 8})
            run_to(cpu, jump, 20)
            assert memory[jump] == 0xE9
            cpu.run()
            index = table + ((code << 1) & 255)
            target = flat[index] | flat[index + 1] << 8
            assert cpu.registers[PC] == target and cpu.registers[SP] == 0xBFFE - stack_bytes
            assert target >> 8 != 0xCF, (name, code, target)
            selected.add(target)
        cases.append(dict(dispatcher=name, jump=jump, table=table, profiles=256,
                          distinct_targets=len(selected), page_cf_targets=0))
        targets[name] = selected
    return cases, targets


def check_indirect_sources(flow, flat):
    regions = {region['name']: region['instructions'] for region in flow
               if region['name'] in ('Action', 'ThreeD')}
    perspective = {0xDB9E, 0xDBA7, 0xDBB2, 0xDBBC}
    clip = {0xC070, 0xC992}
    state = {0x64EF, 0xF175, 0xF2C6, 0xF85D}
    expected = {'Action': perspective | clip | state | {0x6CFF, 0x6F4D, 0xAFF3, 0xD192},
                'ThreeD': perspective | clip | {0xD192}}
    for region, instructions in regions.items():
        assert {item['address'] for item in instructions
                if item['operation'] in ('JP (HL)', 'JP (IX)', 'JP (IY)')} == expected[region]

    def immediate_producers(region, entry, register):
        instructions = regions[region]
        opcode = 'CALL' if entry == 0x6CEF else 'JP'
        pattern = re.compile(rf'{opcode} (?:[A-Z]+,)?#{entry:04X}')
        sites = []
        for index, item in enumerate(instructions):
            if not pattern.fullmatch(item['operation']):
                continue
            prior = instructions[index - 1]
            if entry == 0x6CEF and prior['operation'] == 'PUSH IX':
                assert prior['offset'] + 2 == item['offset']
                prior = instructions[index - 2]
                assert prior['offset'] + 5 == item['offset']
            else:
                assert prior['offset'] + len(bytes.fromhex(prior['hex'])) == item['offset']
            assert prior['slot'] == item['slot']
            match = re.fullmatch(rf'LD {register},#([0-9A-F]{{4}})', prior['operation'])
            assert match, (region, item, prior)
            target = int(match[1], 16)
            assert target >> 8 != 0xCF
            sites.append(dict(branch=item['address'], load=prior['address'], target=target))
        return sites

    callback = immediate_producers('Action', 0x6CEF, 'HL')
    vector = immediate_producers('Action', 0xAF43, 'IY')
    multiply = immediate_producers('Action', 0xD12C, 'IX')
    vertex = immediate_producers('Action', 0xD7A0, 'HL')
    assert [len(sites) for sites in (callback, vector, multiply, vertex)] == [4, 6, 15, 10]
    assert {site['target'] for site in callback} == {0xEC00, 0xEC1B}
    assert len({site['target'] for site in vector}) == 6
    assert len({site['target'] for site in multiply}) == 15
    assert vertex == immediate_producers('ThreeD', 0xD7A0, 'HL')
    assert immediate_producers('ThreeD', 0xD12C, 'IX') == []
    # Проверка прямых входов в найденные переходы в обход загрузки регистра.
    direct = re.compile(r'(?:CALL|JP|JR|DJNZ) (?:[A-Z]+,)?#([0-9A-F]{4})')
    for region, producers in (('Action', callback + vector + multiply + vertex), ('ThreeD', vertex)):
        bypasses = {site['branch'] for site in producers}
        assert not any(int(match[1], 16) in bypasses for item in regions[region]
                       if (match := direct.fullmatch(item['operation'])))
    # Проверка 26 записей и перекрывающегося 27-го шага исходного сканера.
    keyboard = [flat[a] | flat[a + 1] << 8 for a in range(0x7017, 0x704D, 2)]
    assert len(keyboard) == 27 and keyboard[-1] == 0xC0C9
    assert all(target >> 8 != 0xCF for target in keyboard)
    return dict(indirect_jump_sites={region: sorted(sites) for region, sites in expected.items()},
                known_bank3_callback_sources=callback, known_vector_sources=vector,
                known_multiply_sources=multiply, known_vertex_sources_in_both_copies=vertex,
                original_keyboard_targets=keyboard, computed_rets_covered=False,
                direct_entries_bypassing_known_register_loads=[],
                outside_regions_or_modified_producers_covered=False)


def check_temporary_module_targets(flow, functions, clip_targets, object_targets, indirect_sources, render):
    indirect = dict(clip=clip_targets, **object_targets,
                    keyboard=set(indirect_sources['original_keyboard_targets']))
    for name, sites in indirect_sources.items():
        if name.startswith('known_'):
            indirect[name] = {site['target'] for site in sites}
    for name, targets in indirect.items():
        assert not targets.intersection(FIXED_TEMPORARY_WINDOW), name
        assert not targets.intersection(BANKED_TEMPORARY_WINDOW), name

    # Эти прямые совпадения относятся к коду ACTION и 3DPART в банке 0.
    direct = re.compile(r'(?:CALL|JP|JR|DJNZ) (?:[A-Z]+,)?#([0-9A-F]{4})')
    regions = ('ActionBoot', 'Action', 'ThreeD')
    fixed_branches = []
    banked_branches = []
    for region in flow:
        name = region['name']
        if name not in regions:
            continue
        for item in region['instructions']:
            match = direct.fullmatch(item['operation'])
            if match is None:
                continue
            target = int(match[1], 16)
            if target in FIXED_TEMPORARY_WINDOW:
                fixed_branches.append((name, item['address'], target))
            if target not in BANKED_TEMPORARY_WINDOW:
                continue
            assert name in ('Action', 'ThreeD') and item['address'] >= 0xC000
            path, = [row['path'] for row in functions if row['region'] == name and row['slot'] == item['slot']
                     and row['offset'] <= item['offset'] < row['end_offset']]
            banked_branches.append(dict(region=name, address=item['address'], target=target, source=path))
    counts = Counter(row['source'] for row in banked_branches)
    assert not fixed_branches and counts == {
        'Source/Action/ProjectRenderVertex.asm': 45, 'Source/ThreeD/ProjectRenderVertex.asm': 45,
        'Source/Action/RenderClippedRecords.asm': 17, 'Source/ThreeD/RenderClippedRecords.asm': 17,
        'Source/Action/RenderQueuedObject.asm': 1, 'Source/Action/ToggleTargetOverlay.asm': 1,
    }
    # Отдельная трасса проверяет адрес после RET и писателя обоих байтов стека.
    assert render['passed'] and render['ret_targets_and_last_writers_of_both_stack_bytes_observed']
    returns = render['ret_paths']
    assert sum(row['count'] for row in returns) == render['taken_ret_count']
    assert not any(row['target'] in FIXED_TEMPORARY_WINDOW for row in returns)
    banked_returns = [row for row in returns if row['target'] in BANKED_TEMPORARY_WINDOW]
    for row in banked_returns:
        assert row['bank'] == row['stack_writer_bank'] == 0
        assert row['stack_writer_opcode'] in (0xCD, 0xD4) and row['target'] == row['stack_writer'] + 3
    return dict(regions=regions, fixed_window=[0x5DA0, 0x5F5C], banked_window=[0xDADE, 0xDC9A],
                original_indirect_targets={name: sorted(targets) for name, targets in indirect.items()},
                fixed_window_direct_branches=fixed_branches, banked_window_bank0_branches=banked_branches,
                physical_control_bank=1, separately_traced_render_returns=render['taken_ret_count'],
                render_returns_to_same_cpu_addresses_in_bank0=banked_returns, all_returns_covered=False,
                unregistered_code_covered=False)


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
    dispatch_cases, high_bytes, clip_targets = check_dispatch_targets(memory)
    object_dispatch_cases, object_targets = check_object_dispatch_targets(memory)
    indirect_sources = check_indirect_sources(flow, memory)
    reports = ROOT / 'Tools/Disasm/Reports'
    functions = json.loads((reports/'Functions.json').read_bytes())
    render = json.loads((reports/'ActionNonemptyRenderFrameVerification.json').read_bytes())
    temporary_module_targets = check_temporary_module_targets(flow, functions, clip_targets, object_targets,
                                                             indirect_sources, render)
    complete_paths = check_complete_paths(memory)
    report = dict(passed=True, region='Action', bank=0, address=0xCF08, bytes=[0xF3, 0xAF, 0xC9],
                  valid_lookup_entries=selected, table_role_proved=True,
                  decoded_regions=len(flow), decoded_instructions=sum(len(r['instructions']) for r in flow),
                  explicit_references_to_cf08_cf0a=references,
                  raw_words_disk_offsets=raw_words, all_raw_words_in_deleted_sector_tail=True,
                  original_high_table_bytes=high_bytes, target_exclusion_cases=dispatch_cases,
                  object_dispatch_target_exclusion=object_dispatch_cases,
                  registered_indirect_sources=indirect_sources,
                  temporary_module_target_exclusion=temporary_module_targets,
                  complete_paths=complete_paths,
                  page_cf_unreachable_via_both_clip_dispatchers_with_original_high_table=True,
                  possible_instructions=['DI', 'XOR A', 'RET'], execution_entry_proved=False,
                  nonexecution_proved=False, physical_emission='named_pointer_low_bytes',
                  source_bytes_changed=False, assembly_executed=False, native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClipTableAliasVerification.json').write_bytes(
        (json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
