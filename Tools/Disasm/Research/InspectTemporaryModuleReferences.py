"""Разделение числовых совпадений CONTROL, HELP, ACTION и интро без сборки."""
import argparse,hashlib,json,re
from CheckIntro import ROOT
from InspectUnresolvedAuthorSymbols import inspect as inspect_storm_symbols


def absolute_length_stores(flow, disk, entries):
    """Прямые записи с учётом ширины и перекрытия обоих байтов длины, контекст банка не выводится по числу."""
    watched = {0xDB01, 0xDB02}
    stores, matches = 0, []
    for region in flow:
        for instruction in region['instructions']:
            operation = re.sub(r'\s', '', instruction['operation'])
            match = re.fullmatch(r'LD\(#([0-9A-F]{4})\),(HL|DE|BC|SP|IX|IY|A)', operation)
            if not match:
                continue
            data = bytes.fromhex(instruction['hex'])
            offset = instruction['offset']
            entry = entries[instruction['slot']]
            # Проверка физического выделения включает код вступления после объявленной длины BASIC.
            assert 0 <= offset and offset + len(data) <= entry['allocated_length']
            absolute = entry['offset'] + offset
            assert disk[absolute:absolute + len(data)] == data
            target = int(match[1], 16)
            assert int.from_bytes(data[-2:], 'little') == target
            width = 1 if match[2] == 'A' else 2
            # Расчёт каждого адреса слова сохраняет реальное оборачивание после FFFF.
            touched = watched & {(target + index) & 0xFFFF for index in range(width)}
            stores += 1
            if touched:
                matches.append(dict(region=region['name'], slot=instruction['slot'], pc=instruction['address'],
                    offset=offset, operation=instruction['operation'], original_hex=data.hex(),
                    destination=target, width=width, touched_addresses=sorted(touched)))
    assert [(row['region'], row['pc'], row['operation']) for row in matches] == [
        ('Help', 0xDB57, 'LD (#DB01),A')]
    return dict(watched_addresses=sorted(watched), regions_scanned=len(flow),
        registered_instruction_views=sum(len(region['instructions']) for region in flow),
        absolute_store_instruction_views=stores, original_store_bytes_matched=True,
        declared_logical_lengths_not_used_to_truncate_code=True,
        word_store_overlap_and_address_wrap_checked=True, matches=matches,
        same_numeric_HELP_store_is_not_bank1_operand_write_proof=True,
        indexed_indirect_block_stack_generated_or_IRQ_writes_excluded=False,
        nonzero_length_writer_proved=False)


def point_update_high_byte_flow(code, random_entry, preserving_entries):
    """Конечное распространение признака H=C5, неизвестные значения не объявляются безопасными."""
    by_pc = {row['address']: row for row in code}
    assert len(by_pc) == len(code)
    allowed = {'ADD', 'AND', 'CALL', 'CP', 'CPL', 'DEC', 'EX', 'EXX', 'INC', 'JP', 'JR',
               'LD', 'NEG', 'RET', 'RLA', 'RR', 'RRA', 'SUB', 'XOR'}
    assert {row['operation'].split()[0] for row in code} <= allowed
    call_words = {row['address'] + 1 for row in code
        if (call := re.fullmatch(r'CALL #([0-9A-F]{4})', row['operation']))
        and int(call[1], 16) in preserving_entries}
    assert len(call_words) == 2
    for row in code:
        store = re.fullmatch(r'LD\(#([0-9A-F]{4})\),(HL|DE|BC|SP|IX|IY|A)', re.sub(r'\s', '', row['operation']))
        if store:
            start = int(store[1], 16)
            width = 1 if store[2] == 'A' else 2
            touched = set(range(start, start + width)) & {byte for word in call_words for byte in (word, word + 1)}
            if touched:
                assert start in call_words and store[2] == 'HL' and width == 2
    pending = [(code[0]['address'], False, False, None, None)]
    visited, stores, bindings = set(), set(), {}
    while pending:
        pc, main, alternate, main_word, alternate_word = pending.pop()
        state = pc, main, alternate, main_word, alternate_word
        if state in visited:
            continue
        visited.add(state)
        assert pc in by_pc, ('Переход за пределы UpdateBufferPoints', pc)
        row = by_pc[pc]
        operation = re.sub(r'\s', '', row['operation'])
        following = pc + len(bytes.fromhex(row['hex']))
        if operation.startswith('LD(HL),'):
            assert main, ('Не доказан H=C5 при записи', hex(pc), state)
            stores.add(pc)
        word_store = re.fullmatch(r'LD\(#([0-9A-F]{4})\),HL', operation)
        if word_store and int(word_store[1], 16) in call_words:
            assert main_word in preserving_entries, ('Не доказана цель изменяемого CALL', hex(pc), state)
            bindings.setdefault(int(word_store[1], 16), set()).add(main_word)
        # EXX меняет принадлежность обеих пар, значение L не влияет на доказанный старший байт.
        if operation == 'EXX':
            main, alternate = alternate, main
            main_word, alternate_word = alternate_word, main_word
        elif operation.startswith('LDHL,'):
            literal = re.fullmatch(r'LDHL,#([0-9A-F]{4})', operation)
            main = bool(literal and int(literal[1], 16) >> 8 == 0xC5)
            main_word = int(literal[1], 16) if literal and int(literal[1], 16) in preserving_entries else None
        elif operation.startswith('LDH,'):
            main = operation == 'LDH,#C5'
            main_word = None
        elif operation.startswith(('ADDHL,', 'ADCHL,', 'SBCHL,')) or operation in ('INCHL', 'DECHL', 'INCH', 'DECH', 'RRH'):
            main = False
            main_word = None
        elif operation.startswith('LDL,') or operation in ('INCL', 'DECL', 'RRL'):
            main_word = None
        elif operation.startswith('EX') and operation != "EXAF,AF'":
            assert operation == 'EXDE,HL', row
            main = False
            main_word = None
        call = re.fullmatch(r'CALL(?:(NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})', operation)
        if call:
            target = int(call[2], 16)
            assert target == random_entry or target in preserving_entries, row
            if call[1]:
                pending.append((following, main, alternate, main_word, alternate_word))
            # Генератор использует альтернативный HL, оба входа возврата точки сохраняют обе пары.
            pending.append((following, main, False if target == random_entry else alternate,
                            main_word, None if target == random_entry else alternate_word))
            continue
        branch = re.fullmatch(r'(JP|JR)(?:(NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})', operation)
        if branch:
            pending.append((int(branch[3], 16), main, alternate, main_word, alternate_word))
            if branch[2]:
                pending.append((following, main, alternate, main_word, alternate_word))
            continue
        if operation.startswith('RET'):
            assert operation in ('RET', 'RETZ', 'RETNZ', 'RETC', 'RETNC', 'RETPO', 'RETPE', 'RETP', 'RETM')
            if operation != 'RET':
                pending.append((following, main, alternate, main_word, alternate_word))
            continue
        assert not operation.startswith(('JP', 'JR', 'CALL')), row
        pending.append((following, main, alternate, main_word, alternate_word))
    assert set(bindings) == call_words
    return dict(states_checked=len(visited), own_indirect_store_pcs=sorted(stores),
        call_operand_binding_values={f'{word:04X}': sorted(values) for word, values in sorted(bindings.items())},
        all_condition_outcomes_explored=True, initial_main_and_alternate_HL_unknown=True,
        H_at_every_reachable_indirect_store=0xC5, arithmetic_affecting_H_widened_to_unknown=True,
        entry_only=True, CPU_execution_or_flag_model=False,
        arbitrary_changed_opcodes_or_call_targets_supported=False)


def buffer_point_store_domains(flow, disk, entries, functions, sites, symbols):
    """Доказанные области записи трёх процедур при их собственных предусловиях, не общий граф вызовов."""
    control = next(region for region in flow if region['name'] == 'Controls')

    def original_code(path):
        function = next(function for function in functions if function['path'] == path)
        code = sorted((row for row in control['instructions'] if row['slot'] == function['slot']
            and function['offset'] <= row['offset'] < function['end_offset']
            and function['address'] + row['offset'] - function['offset'] == row['address']), key=lambda row: row['offset'])
        data = b''.join(bytes.fromhex(row['hex']) for row in code)
        assert len(data) == function['end_offset'] - function['offset']
        entry = entries[function['slot']]
        start = entry['offset'] + function['offset']
        assert disk[start:start + len(data)] == data
        return code, dict(path=path, start=function['address'], bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

    initialization = 'Source/Controls/InitializeBufferPoints.asm'
    drawing = 'Source/Controls/XorBufferPoints.asm'
    initialize_code, initialize_proof = original_code(initialization)
    random_code, random_proof = original_code('Source/Controls/NextBufferRandom.asm')
    draw_code, draw_proof = original_code(drawing)
    update_path = 'Source/Controls/UpdateBufferPoints.asm'
    update_code, update_proof = original_code(update_path)
    respawn = []
    for path in ('Source/Controls/RespawnPointIndexPos.asm', 'Source/Controls/RespawnPointIndexNeg.asm'):
        helper_code, helper_proof = original_code(path)
        # Эти помощники вообще не обращаются к HL и не меняют принадлежность основных пар.
        assert not any(re.search(r'\bHL\b|\bH\b|\bL\b|\bEXX\b', row['operation']) for row in helper_code)
        assert {row['operation'].split()[0] for row in helper_code} <= {
            'ADD', 'AND', 'CP', 'CPL', 'DEC', 'INC', 'JP', 'JR', 'LD', 'NEG', 'OR',
            'RET', 'RLA', 'RLCA', 'RRCA', 'RRA', 'SUB', 'XOR'}
        helper_addresses = {row['address'] for row in helper_code}
        phase_stores = []
        for row in helper_code:
            operation = re.sub(r'\s', '', row['operation'])
            assert not operation.startswith(('CALL', 'RST', 'PUSH', 'POP', 'LDSP,', 'INCSP', 'DECSP'))
            if operation.startswith(('INC', 'DEC')):
                assert '(' not in operation
            if operation.startswith('LD('):
                phase_stores.append(operation)
            branch = re.fullmatch(r'(?:JP|JR)(?:(?:NZ|Z|NC|C|PO|PE|P|M),)?#([0-9A-F]{4})', operation)
            if branch:
                assert int(branch[1], 16) in helper_addresses
            else:
                assert not operation.startswith(('JP', 'JR')), row
        assert phase_stores == [f'LD(#{helper_proof["start"] + 1:04X}),A']
        helper_proof['only_memory_store'] = dict(address=helper_proof['start'] + 1, bytes=1, role='phase operand')
        respawn.append(helper_proof)
    update_flow = point_update_high_byte_flow(update_code, random_proof['start'], {row['start'] for row in respawn})
    # Отрицательный контроль, смена каждой из трёх затравок указателя на страницу DB должна разрушить доказательство.
    negative_controls = 0
    for changed in update_code:
        if changed['operation'] not in ('LD HL,#C500', 'LD HL,#C501'):
            continue
        mutant = [dict(row) for row in update_code]
        next(row for row in mutant if row['address'] == changed['address'])['operation'] = 'LD HL,#DB00'
        try:
            point_update_high_byte_flow(mutant, random_proof['start'], {row['start'] for row in respawn})
        except AssertionError as error:
            assert error.args[0][0] == 'Не доказан H=C5 при записи'
            negative_controls += 1
        else:
            raise AssertionError(('Принята небезопасная страница', changed))
    assert negative_controls == 3
    update_flow['unsafe_pointer_page_negative_controls_rejected'] = negative_controls
    update_sites = {row['pc'] for row in sites if row['path'] == update_path and row['kind'] == 'indirect_store'}
    assert len(update_sites) == 18 and update_sites == set(update_flow['own_indirect_store_pcs'])
    point_base = symbols['ControlsBufferPoints.Point00']
    point_end = symbols['ControlsBufferPoints.Point22'] + 2
    assert (point_base, point_end) == (0xC500, 0xC546)
    init_ops = [row['operation'] for row in initialize_code]
    random_ops = [row['operation'] for row in random_code]
    draw_ops = [row['operation'] for row in draw_code]
    assert init_ops[0] == 'LD HL,#C500' and init_ops.count('INC L') == 2 and 'CP #46' in init_ops
    assert random_ops[0] == random_ops[-2] == 'EXX' and random_ops[-1] == 'RET'
    assert random_ops.count('EXX') == 2 and not any(op.startswith(('CALL ', 'OUT ')) for op in random_ops)
    assert not any(re.match(r'^(?:JR|JP|RET|RST)\b', op) for op in random_ops[1:-2])
    assert init_ops.count(f'CALL #{random_proof["start"]:04X}') == 2
    assert draw_ops[0] == 'LD BC,#C500' and 'LD H,#94' in draw_ops and draw_ops.count('INC H') == 3
    assert not any(op.startswith(('CALL ', 'OUT ')) for op in draw_ops)
    initialization_sites = [row['pc'] for row in sites if row['path'] == initialization and row['kind'] == 'indirect_store']
    draw_sites = [row['pc'] for row in sites if row['path'] == drawing and row['kind'] == 'indirect_store']
    assert len(initialization_sites) == 2 and len(draw_sites) == 1
    # Расчёт всех адресов при допустимых координатах, перенос из младшей суммы отсутствует.
    addresses = set()
    for y in range(96):
        for x in range(256):
            high = (0x8000 + 32 * y) >> 8
            low = (32 * y & 255) + x // 8
            assert low <= 255
            address = high * 256 + low
            assert address == 0x8000 + 32 * y + x // 8
            addresses.add(address)
    assert addresses == set(range(0x8000, 0x8C00))
    proof = json.loads((ROOT/'Tools/Disasm/Reports/ControlsBufferPointsVerification.json').read_bytes())
    assert proof['passed'] and proof['all_viewport_coordinates'] and proof['original_bitmap_builder']
    return dict(scope='own_indirect_stores_under_documented_procedure_preconditions',
        initialization=dict(code=initialize_proof, helper=random_proof, indirect_store_pcs=initialization_sites,
            destination_start=point_base, destination_end_exclusive=point_end,
            HL_preserved_by_generator_EXX_pair=True, low_byte_increments_only=True,
            explicit_generator_seed_store_and_stack_are_separate=True),
        drawing=dict(code=draw_proof, indirect_store_pcs=draw_sites, y_range=[0, 95], x_range=[0, 255],
            destination_start=min(addresses), destination_end_exclusive=max(addresses) + 1,
            coordinate_pairs_calculated=96 * 256, bitmap_table_pages=[0x94, 0x95, 0x96, 0x97],
            low_byte_sum_does_not_carry=True, destination_disjoint_from_tables_and_points=True),
        update=dict(code=update_proof, helper_code=respawn, high_byte_provenance=update_flow,
            destination_start=0xC500, destination_end_exclusive=0xC600,
            supported_dynamic_respawn_targets=[row['start'] for row in respawn],
            exact_70_byte_bound_not_claimed_by_high_byte_proof=True),
        required_bitmap_tables='ActionBoot.BuildBitmapTables original results',
        required_stack='temporary CALL words in common RAM',
        required_code='original opcodes and documented mutable operands, bank1 selected, no interfering IRQ',
        related_model_report='Tools/Disasm/Reports/ControlsBufferPointsVerification.json',
        bitmap_model_report_sha256=hashlib.sha256((ROOT/'Tools/Disasm/Reports/ControlsBufferPointsVerification.json').read_bytes()).hexdigest(),
        own_indirect_stores_do_not_reach_DB01_DB02=True,
        all_callers_satisfy_preconditions_proved=False, hardware_interrupt_writes_proved=False)


def three_row_glyph_store_domains(flow,disk,entries,functions,sites):
    """Полный байтовый диапазон координат исходного знака, не общий граф вызывающих путей."""
    from CheckControlsThreeRowGlyph import next_scanline
    path='Source/Controls/OrThreeRowGlyph.asm'
    function=next(row for row in functions if row['path']==path)
    control=next(region for region in flow if region['name']=='Controls')
    code=sorted((row for row in control['instructions'] if row['slot']==function['slot']
        and function['offset']<=row['offset']<function['end_offset']),key=lambda row:row['offset'])
    raw=b''.join(bytes.fromhex(row['hex']) for row in code)
    entry=entries[function['slot']];start=entry['offset']+function['offset']
    assert len(raw)==function['end_offset']-function['offset']
    assert disk[start:start+len(raw)]==raw
    assert not any(row['operation'].startswith(('CALL ', 'OUT ', 'PUSH ', 'RST ')) for row in code)
    operations=[row['operation'] for row in code]
    assert operations[:21]==['LD A,B','AND A','RRA','SCF','RRA','AND A','RRA','XOR B',
        'AND #F8','XOR B','LD H,A','LD A,C','RLCA','RLCA','RLCA','XOR B','AND #C7',
        'XOR B','RLCA','RLCA','LD L,A']
    assert {operation.split()[0] for operation in operations}<={'LD','AND','RRA','SCF','XOR',
        'RLCA','ADD','ADC','OR','INC','DEC','JP','JR','SUB','RET'}
    # Проверка независимости последующих изменений HL от прочитанных масочных байтов.
    for index,operation in enumerate(operations):
        if re.match(r'(?:LD|INC|DEC|ADD|ADC|SBC|POP) (?:HL|H|L)(?:,|$)',operation):
            assert operation in ('LD H,A','LD L,A','INC H','INC L','DEC L')
        if index>20 and operation=='LD H,A':
            assert operations[index-2:index]==['LD A,H','SUB #08']
        if index>20 and operation=='LD L,A':
            assert operations[index-2:index]==['LD A,L','ADD A,#20']
    own_sites=[row['pc'] for row in sites if row['path']==path and row['kind']=='indirect_store']
    assert own_sites==[0xE174,0xE179,0xE18F,0xE194,0xE1AA,0xE1AF]
    # Расчёт всех шести адресов для каждой байтовой пары координат, включая выход за 192 строки.
    addresses=set()
    for y in range(256):
        for x in range(256):
            address=0x4000|((y&0xC0)<<5)|((y&7)<<8)|((y&0x38)<<2)|(x>>3)
            for _ in range(3):
                addresses.update((address,(address&0xFF00)|((address+1)&255)))
                address=next_scanline(address)[0]
    assert len(addresses)==8258 and min(addresses)==0x4000 and max(addresses)==0x6120
    assert not addresses&{0xDB01,0xDB02}
    # Проверка чувствительности границы к ошибочному переносу базовой области в верхнее окно.
    assert {address+0x8000 for address in addresses}&{0xDB01,0xDB02}
    proof_path=ROOT/'Tools/Disasm/Reports/ControlsThreeRowGlyphVerification.json'
    proof=json.loads(proof_path.read_bytes())
    assert proof['passed'] and proof['all_four_original_shapes_all_coordinates']
    assert proof['every_ram_byte_and_write_checked'] and proof['total_cases']==274864
    return dict(path=path,entry=0xE14E,entry_only=True,original_code_sha256=hashlib.sha256(raw).hexdigest(),
        original_code_bytes=len(raw),own_indirect_store_pcs=own_sites,
        coordinate_pairs=65536,x_range=[0,255],y_range=[0,255],
        distinct_destination_bytes=len(addresses),destination_start=min(addresses),
        destination_end_exclusive=max(addresses)+1,destination_bank=5,
        arbitrary_Y_does_not_extend_to_bank1=True,mutated_upper_window_base_probe_detected=True,
        source_mask_bytes_do_not_feed_HL_address_updates=True,
        related_model_report=proof_path.relative_to(ROOT).as_posix(),
        model_report_sha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        own_stores_do_not_reach_DB01_DB02=True,
        original_opcodes_bank1_selection_and_no_interfering_IRQ_required=True,
        all_callers_stack_placements_and_interrupt_writes_proved=False)


def station_reload_transfer_domains(flow, disk, entries, sites):
    """Четыре фиксированных назначения LDIR при исполнении исходных префиксов."""
    specs = (
        (0xDCA4, 0xDC9B, 0xDCA9, 0x4000, 0x0100,
         ('LD HL,#DCA9', 'LD DE,#4000', 'LD BC,#0100', 'LDIR')),
        (0xDCED, 0xDCE3, 0x5800, 0x5801, 0x02FF,
         ('LD HL,#5800', 'LD DE,#5801', 'LD BC,#02FF', 'LD (HL),L', 'LDIR')),
        (0xDD09, 0xDD00, 0x9BBD, 0x4000, 0x0200,
         ('LD HL,#9BBD', 'LD DE,#4000', 'LD BC,#0200', 'LDIR')),
        (0xDD15, 0xDD0B, 0xDD23, 0x4200, 0x0100,
         ('LD HL,#DD23', 'LD DE,#4200', 'PUSH DE', 'LD BC,#0100', 'LDIR')),
    )
    watched = {0xDB01, 0xDB02}
    domains = []
    for pc, start, source, destination, length, operations in specs:
        code = [x for r in flow if r['name'] == 'Controls' for x in r['instructions']
                if start <= x['address'] <= pc]
        assert tuple(x['operation'] for x in code) == operations
        cursor = start
        for row in code:
            data = bytes.fromhex(row['hex'])
            assert row['address'] == cursor
            entry = entries[row['slot']]
            absolute = entry['offset'] + row['offset']
            assert row['offset'] + len(data) <= entry['allocated_length']
            assert disk[absolute:absolute + len(data)] == data
            cursor += len(data)
        assert code[-1]['hex'] == 'edb0'
        # Проверка непосредственных HL, DE, BC исключает вывод только из текста отчёта.
        immediates = {x['operation'].split(',')[0][3:]:
                      int.from_bytes(bytes.fromhex(x['hex'])[1:], 'little')
                      for x in code if re.fullmatch(r'LD (HL|DE|BC),#[0-9A-F]{4}', x['operation'])}
        assert immediates == dict(HL=source, DE=destination, BC=length)
        # Расчёт каждой записи LDIR учитывает 16-битное оборачивание адреса.
        addresses = {(destination + i) & 0xFFFF for i in range(length or 65536)}
        assert not addresses & watched
        own_sites = [x for x in sites if x['pc'] == pc and x['kind'] == 'implicit_pointer_store']
        assert len(own_sites) == 1
        domains.append(dict(pc=pc, prefix_start=start, source=source,
            destination=destination, length=length, destination_min=min(addresses),
            destination_max=max(addresses), unique_destination_bytes=len(addresses),
            storage_bank=5, source_path=own_sites[0]['path'],
            prefix_sha256=hashlib.sha256(b''.join(bytes.fromhex(x['hex']) for x in code)).hexdigest(),
            DB01_DB02_reached=False))
    # Проверка чувствительности адресного вывода, перенос назначения на DB00 достигает оба байта.
    assert watched <= {(0xDB00 + i) & 0xFFFF for i in range(0x100)}
    proofs = []
    for name, cases in (('ControlsStationRelocationVerification', 65792),
                        ('ControlsStationPrepareVerification', 8960)):
        path = ROOT/'Tools/Disasm/Reports'/f'{name}.json'
        data = path.read_bytes()
        report = json.loads(data)
        assert report['passed'] and report['total_cases'] == cases
        assert report['all_physical_ram_bytes_proved'] and report['exact_registers_including_R']
        proofs.append(dict(path=path.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(data).hexdigest(), cases=cases))
    return dict(scope='own_four_LDIR_after_original_prefixes_without_IRQ', transfers=domains,
        original_prefix_bytes_checked=True, immediate_register_values_checked=True,
        shifted_destination_negative_control_passed=True, linked_existing_execution_models=proofs,
        execution_models_rerun=False, arbitrary_middle_entries_or_modified_opcodes_proved=False,
        caller_stack_and_other_writes_excluded=False, all_runtime_length_writers_excluded=False)


def queue_pointer_domains(code, cursors):
    """Конечное распространение HL/B, оба исхода условий допускаются независимо от A."""
    by_pc = {x['address']: x for x in code}
    pending = [(0xEC5F, cursor, None) for cursor in cursors]
    visited, stores = set(), {0xEC77: set(), 0xEC79: set()}
    while pending:
        pc, hl, b = pending.pop()
        if (pc, hl, b) in visited:
            continue
        visited.add((pc, hl, b))
        assert len(visited) < 20000
        # Проверка границы, после восстановления регистров новых записей очереди нет.
        if pc == 0xEC6C:
            continue
        row = by_pc[pc]
        op = row['operation']
        following = pc + len(bytes.fromhex(row['hex']))
        if op == 'LD B,#10':
            b = 16
        elif op == 'INC HL':
            hl = (hl + 1) & 0xFFFF
        elif op == 'LD HL,#EC80':
            hl = 0xEC80
        elif op in ('LD (HL),D', 'LD (HL),E'):
            stores[pc].add(hl)
        elif op in ('LD A,(HL)', 'DEC A', 'INC A', 'LD (#EC5D),HL'):
            pass
        elif op.startswith('DJNZ #'):
            assert b is not None and 1 <= b <= 16
            b -= 1
            following = int(op[-4:], 16) if b else following
        elif re.fullmatch(r'JR (?:Z,)?#[0-9A-F]{4}', op):
            target = int(op[-4:], 16)
            if op.startswith('JR Z,'):
                pending.append((following, hl, b))
            following = target
        else:
            raise AssertionError(('Неописанное изменение состояния очереди', pc, op))
        pending.append((following, hl, b))
    return stores, len(visited)


def text_queue_store_domains(flow, disk, entries, functions, sites):
    """Собственные две записи производителя, не стек и не дочерние процедуры."""
    owner = [x for x in functions if x['region'] == 'Controls' and x['name'] == 'QueueTextItem']
    assert len(owner) == 1
    owner = owner[0]
    code = [x for r in flow if r['name'] == 'Controls' for x in r['instructions']
            if x['slot'] == owner['slot'] and owner['offset'] <= x['offset'] < owner['end_offset']]
    # Проверка полной исходной последовательности, курсор допускается менять только в операнде EC5D.
    expected = bytes.fromhex('e5c5f52180ec06107e3d28123c2808232310f5f1c1e1c92180ec10ec18f572237323225dec18ec')
    data = b''.join(bytes.fromhex(x['hex']) for x in code)
    assert data == expected and code[0]['address'] == 0xEC59
    cursor = code[0]['address']
    for row in code:
        raw = bytes.fromhex(row['hex'])
        assert row['address'] == cursor
        entry = entries[row['slot']]
        absolute = entry['offset'] + row['offset']
        assert disk[absolute:absolute + len(raw)] == raw
        cursor += len(raw)
    stores, states = queue_pointer_domains(code, range(0xEC80, 0xECA1, 2))
    assert set(stores[0xEC77]) == set(range(0xEC80, 0xECBF, 2))
    assert set(stores[0xEC79]) == set(range(0xEC81, 0xECC0, 2))
    assert not (stores[0xEC77] | stores[0xEC79]) & {0xDB01, 0xDB02}
    # Проверка чувствительности, испорченный начальный курсор допускает запись длины.
    control, _ = queue_pointer_domains(code, [0xDB00])
    assert 0xDB01 in control[0xEC79] and 0xDB02 in control[0xEC77]
    assert [x['pc'] for x in sites if x['path'] == owner['path'] and x['kind'] == 'indirect_store'] == [0xEC77, 0xEC79]
    return dict(scope='two_own_queue_stores_with_aligned_initial_WriteCursor_in_EC80_ECA0_without_IRQ',
        original_bytes_checked=True, code_sha256=hashlib.sha256(data).hexdigest(),
        abstract_states=states, cursor_values=17, conditions_independently_overapproximated=True,
        correct_End_marker_not_required_for_bound=True, maximum_probes=16,
        own_stores=[dict(pc=pc, addresses=sorted(values)) for pc, values in stores.items()],
        DB01_DB02_not_reached=True, corrupted_cursor_negative_control_passed=True,
        arbitrary_initial_cursor_or_stack_or_IRQ_excluded=False)


def text_window_patch_domains(flow, disk, entries, functions, sites):
    """Полный домен четырёх IX-записей фиксированного тридцатистрочного цикла."""
    owner = next(x for x in functions if x['region'] == 'Controls' and x['name'] == 'InitializeTextWindow')
    code = [x for r in flow if r['name'] == 'Controls' for x in r['instructions']
            if x['slot'] == owner['slot'] and owner['offset'] <= x['offset'] < owner['end_offset']]
    expected = bytes.fromhex('21000022a3ec217eec22aaec2323225decdd2119ed0114002174501160503e1e'
        'dd09dd7500dd7401dd730add720b0824147ce607fe06200b7dc6206f7bc6205f265054083d20d9c9')
    data = b''.join(bytes.fromhex(x['hex']) for x in code)
    assert data == expected
    cursor = 0xEC0E
    for row in code:
        raw = bytes.fromhex(row['hex'])
        assert row['address'] == cursor
        entry = entries[row['slot']]
        absolute = entry['offset'] + row['offset']
        assert disk[absolute:absolute + len(raw)] == raw
        cursor += len(raw)
    by_pc = {x['address']: x['operation'] for x in code}
    assert [by_pc[pc] for pc in (0xEC1F, 0xEC23, 0xEC2C)] == [
        'LD IX,#ED19', 'LD BC,#0014', 'LD A,#1E']
    assert [by_pc[pc] for pc in (0xEC2E, 0xEC3C, 0xEC51, 0xEC52, 0xEC53)] == [
        'ADD IX,BC', "EX AF,AF'", "EX AF,AF'", 'DEC A', 'JR NZ,#EC2E']
    # Расчёт счётчика, исходный A перезаписан до первого обмена AF, BC в теле не меняется.
    domains = []
    for pc, displacement in ((0xEC30, 0), (0xEC33, 1), (0xEC36, 10), (0xEC39, 11)):
        addresses = [(0xED19 + 0x14 * iteration + displacement) & 0xFFFF for iteration in range(1, 31)]
        assert not set(addresses) & {0xDB01, 0xDB02}
        assert len([x for x in sites if x['path'] == owner['path'] and x['pc'] == pc
                    and x['kind'] == 'indirect_store']) == 1
        domains.append(dict(pc=pc, displacement=displacement, addresses=addresses))
    all_targets = {address for row in domains for address in row['addresses']}
    assert len(all_targets) == 120 and min(all_targets) == 0xED2D and max(all_targets) == 0xEF7C
    # Проверка чувствительности границы, иной IX может направить ту же форму записи в DB01/DB02.
    assert {0xDB01, 0xDB02} <= {0xDAED + 0x14 + d for d in (0, 1, 10, 11)}
    return dict(scope='four_own_IX_stores_after_original_EC0E_entry_without_IRQ',
        original_bytes_checked=True, code_sha256=hashlib.sha256(data).hexdigest(),
        input_A_overwritten=True, BC_constant_in_loop=True, IX_changes_only_by_ADD_IX_BC=True,
        counter_preserved_between_two_EX_AF=True, iterations=30, own_stores=domains,
        unique_destination_bytes=120, destination_min=min(all_targets), destination_max=max(all_targets),
        DB01_DB02_not_reached=True, shifted_IX_negative_control_passed=True,
        arbitrary_middle_entry_or_modified_code_or_stack_or_IRQ_excluded=False)


def implicit_pointer_store(operation):
    """Мнемоника RLD отличается от регистра D инструкции RL D, пробел операндов не удаляется."""
    return operation.strip() in ('LDI', 'LDIR', 'LDD', 'LDDR', 'INI', 'INIR', 'IND', 'INDR', 'RLD', 'RRD')


def indirect_control_stores(flow, disk, entries, functions, symbols):
    """Места возможной записи и смены SP в банковом тексте CONTROL, без вывода о фактическом банке исполнения."""
    from collections import Counter
    # Проверка различения неявного адреса HL и обычного регистра D.
    assert implicit_pointer_store('RLD') and implicit_pointer_store('RRD')
    assert not implicit_pointer_store('RL D') and not implicit_pointer_store('RR D')
    rows = []
    for region in flow:
        if region['name'] != 'Controls':
            continue
        for instruction in region['instructions']:
            if instruction['address'] < 0xC000:
                continue
            operation = re.sub(r'\s', '', instruction['operation'])
            kind = None
            if re.match(r'LD\((?:HL|DE|BC|I[XY][+-]#[0-9A-F]+)\),', operation):
                kind = 'indirect_store'
            elif (re.match(r'(?:INC|DEC|RLC|RRC|RL|RR|SLA|SRA|SLI|SLL|SRL|SET|RES)\b', instruction['operation'])
                  and re.search(r'\((?:HL|I[XY][+-]#[0-9A-F]+)\)', operation)):
                kind = 'memory_modify'
            elif implicit_pointer_store(instruction['operation']):
                kind = 'implicit_pointer_store'
            elif operation.startswith('LDSP,') or operation in ('INCSP', 'DECSP'):
                kind = 'stack_pointer_change'
            elif operation.startswith(('CALL', 'PUSH', 'RST')) or operation.startswith('EX(SP),'):
                kind = 'stack_store'
            if kind is None:
                continue
            entry = entries[instruction['slot']]
            data = bytes.fromhex(instruction['hex'])
            offset = instruction['offset']
            assert offset + len(data) <= entry['allocated_length']
            absolute = entry['offset'] + offset
            assert disk[absolute:absolute + len(data)] == data
            owners = [function for function in functions if function['region'] == 'Controls'
                and function['slot'] == instruction['slot']
                and function['offset'] <= offset < function['end_offset']
                and function['address'] + offset - function['offset'] == instruction['address']]
            assert len(owners) == 1, instruction
            rows.append(dict(kind=kind, slot=instruction['slot'], pc=instruction['address'], offset=offset,
                original_disk_offset=absolute, original_hex=data.hex(), operation=instruction['operation'],
                path=owners[0]['path']))
    counts = Counter(row['kind'] for row in rows)
    assert {kind: counts[kind] for kind in ('stack_pointer_change', 'indirect_store',
        'implicit_pointer_store', 'memory_modify')} == dict(stack_pointer_change=183, indirect_store=201,
            implicit_pointer_store=11, memory_modify=9)
    # Проверка отдельного наблюдения всех трёх собственных косвенных записей построителя.
    parameter_report_path = ROOT/'Tools/Disasm/Reports/ControlsParameterStoreDomainsVerification.json'
    parameter_proof = json.loads(parameter_report_path.read_bytes())
    assert parameter_proof['passed'] and parameter_proof['all_table_h_c_pairs'] == 80
    assert parameter_proof['every_ram_byte_and_write_checked']
    parameter_sites = [row['pc'] for row in rows if row['path'] == 'Source/Controls/BuildParameterTables.asm'
                       and row['kind'] == 'indirect_store']
    assert parameter_sites == [0xDE69, 0xDE88, 0xDE93]
    assert [row['pc'] for row in parameter_proof['own_indirect_store_domains']] == parameter_sites
    assert [row['addresses'] for row in parameter_proof['own_indirect_store_domains']] == [
        list(range(0x9BA4, 0x9BB3)), [0x7B97], [0x7B97 + 6 * index for index in range(1, 9)]]
    # Проверка статических границ тех же записей, независимо от зерна и значений параметров.
    from CheckControlsParameterStoreBounds import derive_domains
    bounds_path = ROOT/'Tools/Disasm/Reports/ControlsParameterStoreBoundsVerification.json'
    bounds = json.loads(bounds_path.read_bytes())
    parameter_code = [row for region in flow if region['name'] == 'Controls'
                      for row in region['instructions'] if 0xDE10 <= row['address'] < 0xDE9A]
    parameter_raw = b''.join(bytes.fromhex(row['hex']) for row in parameter_code)
    assert bounds['passed'] and bounds['three_own_stores_disjoint_from_DB01_DB02']
    assert hashlib.sha256(parameter_raw).hexdigest() == bounds['original_code_sha256']
    assert bounds['domains'] == derive_domains(parameter_code)
    assert bounds['own_indirect_store_pcs'] == parameter_sites
    # Проверка полной цепочки без исполнения, повторно вычисляются области детей и стека.
    from CheckControlsParameterCallWrites import derive_report
    call_writes = derive_report()
    call_path = ROOT/'Tools/Disasm/Reports/ControlsParameterCallWritesVerification.json'
    assert json.loads(call_path.read_bytes()) == json.loads(json.dumps(call_writes))
    # Проверка хвостов и банков, числовой адрес верхнего окна не заменяет физический банк.
    from CheckControlsActivationWriteBanks import derive_report as derive_activation_banks
    activation_banks = derive_activation_banks()
    activation_path = ROOT/'Tools/Disasm/Reports/ControlsActivationWriteBanksVerification.json'
    assert json.loads(activation_path.read_bytes()) == json.loads(json.dumps(activation_banks))
    # Проверка тридцати косвенных писателей растра, самомодификация и стек выделены отдельно.
    from CheckControlsInteriorWriteBounds import derive_report as derive_interior_bounds
    interior = derive_interior_bounds()
    interior_path = ROOT/'Tools/Disasm/Reports/ControlsInteriorWriteBoundsVerification.json'
    assert json.loads(interior_path.read_bytes()) == json.loads(json.dumps(interior))
    interior_sites = [row['pc'] for row in rows
                      if row['path'] == 'Source/Controls/PrepareInteriorSpan.asm' and row['kind'] == 'indirect_store']
    assert interior_sites == interior['domains']['own_raster_store_pcs']
    # Проверка всех PUSH прокрутки, область записей выводится без значений пикселей и исполнения прокрутки.
    from CheckControlsScrollStoreBounds import analyze as analyze_scroll, START as SCROLL_START, END as SCROLL_END
    from ReferenceControlsTextDisplay import initialize as initialize_scroll_reference
    scroll_path=ROOT/'Tools/Disasm/Reports/ControlsScrollStoreBoundsVerification.json'
    scroll=json.loads(scroll_path.read_bytes())
    assert scroll['passed'] and scroll['own_writes_disjoint_from_bank1_DB01_DB02']
    scroll_memory=[0]*65536
    for slot,origin in ((22,0xC000),(23,0xDADE)):
        entry=entries[slot]
        scroll_memory[origin:origin+entry['length']]=disk[entry['offset']:entry['offset']+entry['length']]
    assert hashlib.sha256(bytes(scroll_memory[SCROLL_START:SCROLL_END])).hexdigest()==scroll['original_code_sha256']
    scroll_code=[row for region in flow if region['name']=='Controls' for row in region['instructions']
                 if row['slot']==23 and SCROLL_START<=row['address']<SCROLL_END]
    assert analyze_scroll(scroll_memory,scroll_code)['push_instructions']==216
    initialize_scroll_reference(scroll_memory)
    assert hashlib.sha256(bytes(scroll_memory[SCROLL_START:SCROLL_END])).hexdigest()==scroll['prepared_code_sha256']
    scroll_bounds=analyze_scroll(scroll_memory,scroll_code)
    assert sorted(set(scroll_bounds['screen_write_addresses']))==scroll['screen_write_addresses']
    assert scroll_bounds['code_write_addresses']==scroll['code_write_addresses']
    scroll_sites=[row['pc'] for row in rows if row['path']=='Source/Controls/ScrollTextWindow.asm' and row['kind']=='stack_store']
    assert len(scroll_sites)==216
    # Проверка символических указателей копировщика и отдельного условного писателя через родительский CALL.
    from CheckControlsBufferCopyStoreBounds import analyze as analyze_copy
    copy_path=ROOT/'Tools/Disasm/Reports/ControlsBufferCopyStoreBoundsVerification.json'
    copy_proof=json.loads(copy_path.read_bytes())
    copy_memory=[0]*65536
    entry=entries[22]
    copy_memory[0xC000:0xC000+entry['length']]=disk[entry['offset']:entry['offset']+entry['length']]
    assert copy_proof['passed'] and copy_proof['worker_own_writes_disjoint_from_bank1_DB01_DB02']
    assert hashlib.sha256(bytes(copy_memory[0xC882:0xCA8D])).hexdigest()==copy_proof['original_code_sha256']
    assert hashlib.sha256(bytes(copy_memory[0xC870:0xC882])).hexdigest()==copy_proof['parent_code_sha256']
    copy_code=[row for region in flow if region['name']=='Controls' for row in region['instructions']
               if row['slot']==22 and 0xC882<=row['address']<0xCA8D]
    copy_union=set();copy_profiles=0
    for third in range(3):
        for line in range(8):
            for count in range(1,9-line):
                bound=analyze_copy(copy_code,0x400F+third*2048+line*32,count)
                assert len(bound['screen_write_addresses'])==len(set(bound['screen_write_addresses']))==count*256
                assert set(bound['code_write_addresses'])=={0xCA84,0xCA8A,0xCA8B}
                copy_union.update(bound['screen_write_addresses']);copy_profiles+=1
    assert copy_profiles==copy_proof['profile_count']==108 and copy_union==set(range(0x4000,0x5800))
    assert bytes(copy_memory[0xC879:0xC87C])==bytes.fromhex('cd82c8')
    assert copy_proof['parent_stack_alias']['input_SP']==0xDB03
    assert copy_proof['parent_stack_alias']['bank1_length_operand_written']==0xC87C
    copy_sites=[row['pc'] for row in rows if row['path']=='Source/Controls/CopyScreenRows.asm' and row['kind']=='stack_store']
    assert len(copy_sites)==128
    return dict(source_region='Controls', source_storage_bank=1,
        source_storage_bank_is_not_execution_bank_proof=True, source_cpu_address_minimum=0xC000,
        original_physical_instruction_bytes_matched=True, counts=dict(counts),
        register_rotate_and_implicit_memory_mnemonics_distinguished=True,
        qualified_buffer_point_domains=buffer_point_store_domains(flow,disk,entries,functions,rows,symbols),
        qualified_three_row_glyph_domains=three_row_glyph_store_domains(flow,disk,entries,functions,rows),
        qualified_station_reload_transfer_domains=station_reload_transfer_domains(flow,disk,entries,rows),
        qualified_text_queue_store_domains=text_queue_store_domains(flow,disk,entries,functions,rows),
        qualified_text_window_patch_domains=text_window_patch_domains(flow,disk,entries,functions,rows),
        qualified_parameter_store_domains=dict(
            proof_report=bounds_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(bounds_path.read_bytes()).hexdigest(),
            original_code_sha256=bounds['original_code_sha256'],
            own_indirect_store_pcs=parameter_sites, domains=bounds['domains'],
            independent_of_seed_and_computed_values=True,
            own_stores_do_not_reach_DB01_DB02=True,
            child_explicit_seed_and_stack_writes_are_separate=True,
            all_callers_stack_placements_and_interrupt_writes_proved=False),
        qualified_parameter_call_chain=dict(
            proof_report=call_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(call_path.read_bytes()).hexdigest(),
            nonstack_destinations=call_writes['nonstack_destinations'],
            nonstack_destinations_disjoint_from_DB01_DB02=True,
            maximum_additional_stack_bytes=call_writes['maximum_additional_stack_bytes'],
            stack_byte_depths=call_writes['stack_byte_depths'],
            stack_overlap_input_SP=call_writes['stack_overlap_input_SP'],
            required_preconditions=call_writes['required_preconditions'],
            all_callers_stack_and_banking_preconditions_proved=False,
            entire_program_length_writers_excluded=False),
        qualified_parameter_activation_banks=dict(
            proof_report=activation_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(activation_path.read_bytes()).hexdigest(),
            unique_nonstack_physical_destinations=activation_banks['unique_nonstack_physical_destinations'],
            maximum_additional_stack_bytes=activation_banks['maximum_additional_stack_bytes'],
            physical_bank_1_unchanged_under_common_RAM_stack_preconditions=True,
            bank1_DB01_DB02_not_written_under_preconditions=True,
            required_preconditions=activation_banks['required_preconditions'],
            all_game_callers_meet_preconditions_proved=False,
            full_program_DB01_DB02_writer_graph_proved=False),
        qualified_interior_row_store_domains=dict(
            proof_report=interior_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(interior_path.read_bytes()).hexdigest(),
            own_raster_store_pcs=interior_sites, domains=interior['domains'],
            raster_destination_count=interior['raster_destination_count'],
            raster_address_minimum=interior['raster_address_minimum'],
            raster_address_maximum=interior['raster_address_maximum'],
            raster_physical_bank=2, code_patch_physical_bank=1,
            raster_and_code_patch_destinations_disjoint_from_DB01_DB02=True,
            stack_overlap_input_SP=interior['stack_overlap_input_SP'],
            required_preconditions=interior['required_preconditions'],
            all_game_callers_and_stack_placements_proved=False,
            all_temporary_module_length_writers_excluded=False),
        qualified_scroll_stack_store_domains=dict(
            proof_report=scroll_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(scroll_path.read_bytes()).hexdigest(),
            original_code_sha256=scroll['original_code_sha256'],
            own_push_pcs=scroll_sites,push_instructions=216,screen_write_count=432,
            screen_physical_bank=5,screen_write_addresses=scroll['screen_write_addresses'],
            code_physical_bank=1,code_write_addresses=scroll['code_write_addresses'],
            input_SP_and_pixel_values_do_not_change_write_addresses=True,
            own_writes_disjoint_from_bank1_DB01_DB02=True,
            initialized_operands_and_unmodified_opcodes_required=True,
            scroll_execution_model_rerun=False,all_callers_and_runtime_modifications_proved=False,
            all_temporary_module_length_writers_excluded=False),
        qualified_buffer_copy_stack_store_domains=dict(
            proof_report=copy_path.relative_to(ROOT).as_posix(),
            proof_report_sha256=hashlib.sha256(copy_path.read_bytes()).hexdigest(),
            original_code_sha256=copy_proof['original_code_sha256'],
            own_push_pcs=copy_sites,static_push_sites=128,profile_count=108,
            source_page_base_symbolic=True,pixel_words_do_not_feed_address_registers=True,
            screen_physical_bank=5,screen_union_start=0x4000,screen_union_end_exclusive=0x5800,
            code_physical_bank=1,code_write_addresses=[0xCA84,0xCA8A,0xCA8B],
            worker_own_writes_disjoint_from_bank1_DB01_DB02=True,
            conditional_parent_CALL_stack_alias=copy_proof['parent_stack_alias'],
            copy_execution_models_rerun=False,all_callers_stack_domains_proved=False,
            natural_temporary_module_length_writer_proved=False),
        observed_parameter_store_domains=dict(
            model_report='Tools/Disasm/Reports/ControlsParameterStoreDomainsVerification.json',
            model_report_sha256=hashlib.sha256(parameter_report_path.read_bytes()).hexdigest(),
            cases=parameter_proof['total_cases'],
            own_stores=parameter_proof['own_indirect_store_domains'],
            DB01_DB02_not_reached_in_these_cases=True,
            all_input_combinations_or_callers_proved=False,
            arbitrary_stack_and_interrupt_writes_excluded=False),
        owner_files=len({row['path'] for row in rows}), sites=rows,
        effective_pointer_and_stack_domains_proved=False,
        relocation_common_RAM_and_other_region_stores_included=False,
        generated_code_and_hardware_interrupt_writes_included=False,
        all_possible_runtime_writes_excluded=False)


def noise_irq_length_domains():
    """Повторная проверка ROM-графов, адреса длины отсутствуют до учёта банков."""
    from CheckActionNoiseIrqAddressDomain import (
        HALT_SP, NOISE_ENTRY_SP, ROM48, ROM128, check_rom, flat_action, target_accesses,
    )
    path = ROOT / 'Tools/Disasm/Reports/ActionNoiseIrqAddressDomainVerification.json'
    proof = json.loads(path.read_bytes())
    assert proof['passed'] and proof['noise_entry_sp'] == NOISE_ENTRY_SP
    assert proof['noise_halt_sp'] == HALT_SP
    assert proof['rom_irq_temporary_module_length_access_possible_with_verified_frame'] is False
    action = flat_action()
    profiles = []
    for rom, extended in ((ROM48, False), (ROM128[1], True)):
        profile = check_rom(rom, action, extended=extended)
        profile['temporary_module_length_accesses'] = [target_accesses(profile, address)
                                                       for address in (0xDB01, 0xDB02)]
        assert not any(row['access_possible'] for row in profile['temporary_module_length_accesses'])
        profiles.append(profile)
    assert json.loads(json.dumps(profiles)) == proof['profiles']
    return dict(proof_report=path.relative_to(ROOT).as_posix(),
                proof_report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_ROM_graphs_and_address_domains_recomputed=True,
                noise_entry_SP=NOISE_ENTRY_SP, noise_halt_SP=HALT_SP,
                target_addresses=[0xDB01, 0xDB02],
                any_numeric_target_access_possible=False,
                all_game_irq_handlers_and_stack_frames_proved=False)


def observed_copy_caller_stacks(disk, entries):
    """Ограниченная модель вызывающих состояний, не универсальная область SP."""
    path = ROOT / 'Tools/Disasm/Reports/BufferCopyCallerStacksVerification.json'
    proof = json.loads(path.read_bytes())
    assert proof['passed'] and proof['original_disk_sha256'] == hashlib.sha256(disk).hexdigest()
    start = entries[22]['offset'] + 0x870
    assert proof['original_parent_code_sha256'] == hashlib.sha256(disk[start:start + 18]).hexdigest()
    assert proof['all_game_caller_stacks_proved'] is False
    assert proof['temporary_module_natural_length_writer_proved'] is False
    assert proof['bank1_length_runtime_writes'] == []
    assert [row['input_SP'] for row in proof['calls']] == [0xBFFA, 0xBFF8, 0xBFF8]
    assert [row['external_return'] for row in proof['calls']] == [0xAAAF, 0x6085, 0x6085]
    for row in proof['calls']:
        assert row['bank1_PackedLength_unchanged'] and row['copied_bytes_compared'] == 3072
        assert row['final_SP'] == row['input_SP'] + 2
        assert sorted((write['address'], write['value'], write['bank']) for write in row['call_writes']) == [
            (row['input_SP'] - 2, 0x7C, 2), (row['input_SP'] - 1, 0xC8, 2)]
    return dict(proof_report=path.relative_to(ROOT).as_posix(),
                proof_report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                observed_calls=proof['calls'], model_execution_rerun_by_inventory=False,
                all_game_caller_stacks_proved=False,
                temporary_module_natural_length_writer_proved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    reports=ROOT/'Tools/Disasm/Reports'
    def read(name):return json.loads((reports/(name+'.json')).read_bytes())
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    flow=read('ControlFlow');functions=read('Functions');entries={e['slot']:e for e in manifest['entries']}
    payloads={slot:(ROOT/(e['path']+'.bin')).read_bytes() for slot,e in entries.items()}
    template=payloads[23][:127];assert template[:6]==bytes.fromhex('DDE5ED73335E')
    assert template[0xDB01-0xDADE:0xDB03-0xDADE]==bytes(2)
    relocated_entries={0x5DA0,0x5E1F}
    relocated_body_start=0x5DA0
    relocated_body_end=relocated_body_start+len(template)
    relocated_body_references=[]
    watched=(0xDADE,0xDB01,0xDB02,0x5E33,0x5E34,0xC600,0x6500,0x5DA0,0x5E1F,0xDB5D)
    decoded=[]
    for region in flow:
        for item in region['instructions']:
            literals={int(x,16) for x in re.findall(r'#([0-9A-F]{4})\b',item['operation'])}
            # Поиск операндов внутри всего тела условной копии, включая байты операнда длины.
            body_literals=sorted(value for value in literals if relocated_body_start<=value<relocated_body_end)
            if body_literals:
                relocated_body_references.append(dict(region=region['name'],slot=item['slot'],
                    address=item['address'],operation=item['operation'],matching_literals=body_literals))
            if not literals.intersection(watched):continue
            owners=[f for f in functions if f['region']==region['name'] and f['slot']==item['slot']
                    and f['offset']<=item['offset']<f['end_offset']]
            decoded.append(dict(region=region['name'],slot=item['slot'],offset=item['offset'],
                address=item['address'],operation=item['operation'],
                path=owners[0]['path'] if len(owners)==1 else None,
                matching_literals=sorted(literals.intersection(watched))))
    # Проверка буквальных копий всего шаблона, совпадение само по себе не доказывает вызов.
    copies=[];pairs=[]
    for slot,data in payloads.items():
        begin=0
        while (offset:=data.find(template,begin))>=0:
            copies.append(dict(slot=slot,offset=offset));begin=offset+1
        for address in watched:
            needle=address.to_bytes(2,'little');begin=0;offsets=[]
            while (offset:=data.find(needle,begin))>=0:offsets.append(offset);begin=offset+1
            if offsets:pairs.append(dict(slot=slot,value=address,offsets=offsets,
                                         raw_pair_occurrence_is_not_pointer_or_instruction_proof=True))
    assert copies==[dict(slot=23,offset=0)]
    # Поиск по всем физическим байтам TRD, включая хвосты секторов, удалённые записи и свободную область.
    disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert len(disk)==manifest['size']==655360 and hashlib.sha256(disk).hexdigest()==manifest['sha256']
    physical_matches={}
    for name,pattern in (('complete_template',template),('push_ix_store_sp_prefix',template[:4])):
        offsets=[];begin=0
        while (offset:=disk.find(pattern,begin))>=0:
            offsets.append(offset);begin=offset+1
        assert offsets==[entries[23]['offset']]
        physical_matches[name]=dict(pattern_bytes=len(pattern),disk_offsets=offsets)
    physical_search=dict(bytes_scanned=len(disk),original_disk_sha256=hashlib.sha256(disk).hexdigest(),
        full_physical_image_not_only_logical_payloads=True,matches=physical_matches,
        owner_slot=23,owner_file_offset=0,other_exact_or_same_prefix_physical_copies_found=False,
        packed_or_runtime_generated_copies_excluded=False)
    restore=next(f for f in functions if f['region']=='Action' and f['address']==0x6000)
    assert restore['path']=='Source/Action/QueueNumberBank1.asm'
    # Проверка ссылки HELP с тем же CPU-адресом, это другой банк и другой операнд.
    shared=next(i for i in decoded if i['region']=='Help' and i['address']==0xDB57)
    assert shared['operation']=='LD (#DB01),A' and shared['path']=='Source/Help/SelectText.asm'
    assert not any(relocated_entries.intersection(item['matching_literals']) for item in decoded)
    assert relocated_body_references==[]
    aliases=[item for item in decoded if 0xDB5D in item['matching_literals']]
    assert {(item['region'],item['slot'],item['address'],item['operation']) for item in aliases}=={
        ('Action',17,0xDAE2,'JP #DB5D'),('ThreeD',19,0xDAE2,'JP #DB5D')}
    symbols=read('Symbols')
    for region in ('Action','ThreeD'):
        name=region+'.ProjectRenderVertex'
        assert symbols[name+'.SecondSplit10']==0xDADE and symbols[name+'.SecondBit06']==0xDB5D
        renderer=(ROOT/f'Source/{region}/ProjectRenderVertex.asm').read_text('utf-8')
        block=renderer.split('SecondSplit10:',1)[1].split('SecondSplit11:',1)[0]
        assert f'JP @{name}.SecondBit06' in block and 'CALL' not in block and 'OUT' not in block
    proof=read('ControlsTemporaryModuleVerification');assert proof['passed'] and proof['direct_switch_changes_next_opcode']
    # Проверка имён раннего переходника в оставшихся структурированных STORM.
    storm=inspect_storm_symbols({'ADHDP','JL1','JL2','SETHJRET','M18','M20','$M18','$M20'})
    assert storm['source_entries']==31 and storm['records']==18123
    assert not storm['mentions']
    storm_transfer={key:storm[key] for key in ('archive_sha256','queried_names',
        'source_entries','records','decoded_symbol_occurrences','mentions','method')}
    storm_transfer.update(numeric_or_aliased_references_excluded=False,
        current_caller_proved=False)
    result=dict(passed=True,method='original_payload_exact_template_and_decoded_literal_reference_audit',
        template_bytes=127,template_sha256=hashlib.sha256(template).hexdigest(),exact_original_payload_copies=copies,
        original_length_operand=0,decoded_references=decoded,raw_little_endian_pair_occurrences=pairs,
        absolute_length_store_audit=absolute_length_stores(flow,disk,entries),
        indirect_control_store_inventory=indirect_control_stores(flow,disk,entries,functions,symbols),
        qualified_noise_irq_length_domains=noise_irq_length_domains(),
        observed_buffer_copy_caller_stacks=observed_copy_caller_stacks(disk,entries),
        physical_disk_template_search=physical_search,
        archived_STORM_named_transfer_search=storm_transfer,
        same_numeric_help_write_is_not_control_length_writer=True,
        inferred_fixed_ram_entries_with_no_decoded_literal_reference=sorted(relocated_entries),
        relocated_body_literal_audit=dict(start_address=relocated_body_start,end_exclusive=relocated_body_end,
            bytes=len(template),packed_length_operand_addresses=[0x5DC3,0x5DC4],
            regions_scanned=len(flow),instructions_scanned=sum(len(region['instructions']) for region in flow),
            decoded_literal_references=relocated_body_references,
            computed_addresses_and_runtime_generated_instructions_excluded=False,
            legitimate_relocation_proved=False),
        bank0_db5d_jumps_target_renderer_second_bit06=True,
        restored_unchanged_action_core_entry=restore['path'],restored_entry_address=0x6000,
        direct_bank_switch_next_opcode=proof['bank6_panel_opcode'],template_next_opcode=proof['stored_opcode'],
        dynamic_reference_graph_complete=False,legitimate_relocation_proved=False,nonzero_length_writer_proved=False,
        temporary_module_payload_and_real_caller_proved=False,semantic_contract_complete=False,
        assembly_executed=False,native_execution=False)
    target=reports/'ControlsTemporaryModuleReferenceAudit.json'
    if target.exists():
        previous=json.loads(target.read_bytes())
        assert args.refresh and previous['method']==result['method']
        assert previous['template_sha256']==result['template_sha256']
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('decoded_references','raw_little_endian_pair_occurrences')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
