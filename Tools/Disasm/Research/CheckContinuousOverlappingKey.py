"""Последовательные полётные кадры с удержанием FD,02 после первого входа в сканер.

Документация: ../../../Docs/ActionContinuousKeyClip.md
"""
from collections import Counter
from hashlib import sha256
import json
import argparse

from CheckFlightKeyPaths import ControlSourceMemory, ClipDispatchProbe
from CheckActionParameterActivation import flat_action
from TraceFlight import ROOT, Simulator, Ports, PC, SP, H, L, D, E, F, IFF, main as trace_flight


class ObservedMemory(ControlSourceMemory):
    clip_frame = None
    cpu_registers = None
    interrupt_entry = False
    game_frame = 0
    render_node_index = None

    def __init__(self):
        super().__init__()
        self.clip_writes = []
        self.last_state_writers = {}
        self.slot0_identity_changes = []

    def __setitem__(self, address, value):
        if self.watch_writes and address in (0xA106,0xA10A,0xA112) and self[address] != value:
            self.slot0_identity_changes.append(dict(frame=self.game_frame,pc=self.cpu_registers[PC],
                address=address,before=self[address],after=value))
        if self.watch_writes and (address == 0x9BA3 or self.o7ffd & 7 == 0 and (
                address in (0xCF03,0xCF07) or 0xCF0B <= address < 0xCF10 or 0xCF1B <= address < 0xCF20)):
            pc = self.cpu_registers[PC]
            self.last_state_writers[address] = dict(address=address,frame=self.game_frame,pc=pc,
                selected_upper_bank=self.o7ffd & 7,before=self[address],after=value,
                render_node_index=self.render_node_index,keyboard_clip=self.clip_frame is not None,
                opcode=bytes(self[(pc+i)&65535] for i in range(4)).hex(),interrupt_entry=self.interrupt_entry)
        if self.clip_frame is not None and (0x9000 <= address < 0x9100 or address == 0x9BA3
                or address == 0xCF07 and self.o7ffd & 7 == 0):
            self.clip_writes.append(dict(frame=self.clip_frame, pc=self.cpu_registers[PC],
                bank=2 if address < 0xC000 else self.o7ffd & 7, address=address,
                before=self[address], after=value, interrupt_entry=self.interrupt_entry))
        super().__setitem__(address,value)


class HeldPorts(Ports):
    active = False
    started = False

    def __init__(self,memory):
        super().__init__(memory)
        self.reads = []
        self.scanner_reads = []

    def read_port(self,registers,port):
        if self.active and port & 255 == 0xFE:
            # Одна физическая клавиша остаётся замкнутой и для многорядного опроса.
            value = 253 if not port >> 8 & 2 else 255
        else:
            value = super().read_port(registers,port)
        if self.started and port & 255 == 0xFE:
            self.reads.append((registers[PC],port,value))
            if registers[PC] == 0x6F34:self.scanner_reads.append((port,value))
        return value


class ObservedSimulator(Simulator):
    frame = 0

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.interrupts = []

    def accept_interrupt(self,registers,memory,previous_pc):
        before_pc,before_sp = registers[PC],registers[SP]
        memory.interrupt_entry = True
        accepted = super().accept_interrupt(registers,memory,previous_pc)
        memory.interrupt_entry = False
        if accepted:
            self.interrupts.append(dict(frame=self.frame, previous_pc=previous_pc,
                return_pc=before_pc, target=registers[PC], before_SP=before_sp,
                after_SP=registers[SP], during_clip=memory.clip_frame is not None))
        return accepted


def state(memory):
    def raw(address,count):return bytes(memory[address+i] for i in range(count)).hex()
    return dict(first_point=raw(0xCF0B,5),second_point=raw(0xCF1B,5),
                corner_block=memory[0xCF03],seen=memory[0xCF07],output_size=memory[0x9BA3],
                Y_value=memory[0x9B95],negative_counter=memory[0x7759],
                positive_counter=memory[0x777C],Y_latch=memory[0x6FB0])


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--idle',action='store_true',help='контроль без нажатой клавиши с тем же наблюдателем')
    parser.add_argument('--frames',type=int,default=64,choices=(64,128),help='число полных последовательных кадров')
    args = parser.parse_args(arguments)
    frame_count = args.frames
    held = not args.idle
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    entries = {row['slot']:row for row in manifest['entries']}
    # Проверка оригинального ACTION, дальнейшие загрузки выполняются существующим стендом TR-DOS.
    entry = entries[17]
    action = (ROOT/(entry['path']+'.bin')).read_bytes()
    assert action == disk[entry['offset']:entry['offset']+entry['length']]
    flat = flat_action()
    keys = [tuple(flat[0x9D4C+2*i:0x9D4E+2*i]) for i in range(27)]
    targets = [flat[0x7017+2*i] | flat[0x7018+2*i] << 8 for i in range(27)]
    hit_indices = [i for i,(row,mask) in enumerate(keys) if not ((253 if not row & 2 else 255) & mask)]
    assert hit_indices == [0,26] and [targets[i] for i in hit_indices] == [0x7753,0xC0C9]
    expected_hits = hit_indices if held else []
    expected_reads = [(row*256+0xFE,253 if held and not row & 2 else 255) for row,_ in keys]
    from VerifySources import structure_symbols
    fields = structure_symbols()
    assert (fields['FACTIONRECORD.MODELOFFSET'],fields['FACTIONRECORD.STATECODE'],fields['FACTIONRECORD.CLASSCODE']) == (6,10,18)
    memory = ObservedMemory()
    for offset,value in enumerate(action,0x6000):memory[offset] = value
    cpu = ObservedSimulator(memory,{'PC':0x6000,'SP':0x5FFF,'IY':0x5C3A},
                            config={'fast_ldir':False,'fast_djnz':False})
    memory.cpu_registers = cpu.registers
    ports = None
    def ports_factory(memory):
        nonlocal ports
        ports = HeldPorts(memory)
        return ports
    clip_probe = ClipDispatchProbe(bytes(flat[0xD000:0xD100]))
    scans = []
    render_nodes = []
    enqueued_nodes = {}
    current_scene_record = None
    symbols = json.loads((ROOT/'Tools/Disasm/Reports/Symbols.json').read_bytes())
    read_record_pc = symbols['Action.RenderSceneFrame.ReadRecord']
    write_payload_pc = symbols['Action.InsertRenderQueue.WritePayload']
    model_registry_path = ROOT/'Tools/Disasm/Reports/ResourceSemanticLimits.json'
    named_models = {row['address']:row for row in json.loads(model_registry_path.read_bytes())['model_name_provenance']['named_models']}
    current = None
    pending_target = None
    handler = None
    post_startup = False
    initial_record0 = None
    random0_calls = []
    alternate_entries = []
    pending_random0 = None
    last_random0 = None
    pending_distance_store = None
    temporary_entries = set()
    paths = {0xC4F6:'top_intersection',0xC641:'left_then_corner_request',0xC0E0:'left_then_corner_mark',
             0xC6EA:'special_exit',0xC993:'geometric_continuation'}

    def observe(frame,memory,registers):
        nonlocal current,pending_target,handler,post_startup,current_scene_record,initial_record0
        nonlocal pending_random0,last_random0,pending_distance_store
        pc,sp = registers[PC],registers[SP]
        bank = memory.o7ffd & 7
        cpu.frame = frame+1 if pc == 0xA85E else frame
        memory.game_frame = cpu.frame
        clip_probe.observe(memory,registers)
        if pc == 0xA85E:
            if not post_startup:initial_record0 = bytes(memory[0xA100+i] for i in range(64)).hex()
            post_startup = True
            memory.watch_writes = True
        if pc == 0x7B66:
            assert bank == 0 and pending_random0 is None
            assert bytes(memory[pc+i] for i in range(3)) == bytes.fromhex('cd72eb')
            pending_random0 = dict(frame=frame,call_SP=sp,
                previous_word=memory[0xEBDE] | memory[0xEBDF] << 8)
        elif pc == 0x7B69:
            assert pending_random0 is not None and sp == pending_random0['call_SP']
            word = registers[H]*256+registers[L]
            assert word == memory[0xEBDE] | memory[0xEBDF] << 8
            pending_random0.update(returned_HL=word,stream0_word=word,stream0_fold=memory[0xEBE0])
            last_random0 = pending_random0
            random0_calls.append(last_random0)
            pending_random0 = None
        elif pc == 0x7B6C:
            assert last_random0 is not None and last_random0['frame'] == frame
            assert memory[0x7B6A] == 0xFE
            threshold = memory[0x7B6B]
            assert bool(registers[F]&1) == (registers[L] < threshold)
            last_random0.update(threshold=threshold,branch_to_distance=bool(registers[F]&1))
        elif pc == 0x794B:
            assert last_random0 is not None and last_random0['frame'] == frame
            word = registers[H]*256+registers[L]
            assert last_random0['branch_to_distance'] and word == last_random0['returned_HL']
            assert bytes(memory[pc+i] for i in range(3)) == bytes.fromhex('229c79')
            last_random0.update(distance_entry_HL=word,distance_entry_SP=sp)
            pending_distance_store = last_random0
        elif pc == 0x794E:
            assert pending_distance_store is not None
            stored = memory[0x799C] | memory[0x799D] << 8
            assert stored == pending_distance_store['returned_HL']
            pending_distance_store.update(stored_word=stored,stored_by_original_794B=True)
            pending_distance_store = None
        if pc == 0x7859:
            alternate_entries.append(dict(frame=frame,template_mode=memory[0x9B83],
                third_gate=memory[0x9B82],SP=sp,return_address=memory[sp] | memory[sp+1] << 8,
                saved_word=memory[0x799C] | memory[0x799D] << 8))
        if pc == read_record_pc and bank == 0:
            current_scene_record = registers[H]*256+registers[L]
        if pc == write_payload_pc and bank == 0:
            node = registers[H]*256+registers[L]
            assert node >> 8 == 0x8F and node & 255 == memory[0x9BA2]
            assert current_scene_record is not None and 0xA100 <= current_scene_record < 0xA780
            assert (current_scene_record-0xA100)%64 == 0
            enqueued_nodes[frame,node] = dict(source_record=current_scene_record,
                source_record_index=(current_scene_record-0xA100)//64,
                source_record_bytes=bytes(memory[current_scene_record+i] for i in range(64)).hex(),
                source_model_offset=memory[current_scene_record+6],
                source_state_code=memory[current_scene_record+10],
                source_class_code=memory[current_scene_record+18])
        if pc == 0xE4DB and bank == 0:
            node = memory[sp] | memory[sp+1] << 8
            raw = bytes(memory[node+i] for i in range(14))
            assert raw[3:5] == bytes((memory[0x9B8D],memory[0x9B8E]))
            model_index = memory[0x9B8E]
            assert model_index%2 == 0
            pointer = memory[0x9E00+model_index] | memory[0x9E00+((model_index+1)&255)] << 8
            named = named_models.get(pointer)
            memory.render_node_index = len(render_nodes)
            render_nodes.append(dict(frame=frame,node=node,node_bytes=raw.hex(),
                model_byte_offset=model_index,model_bank4_address=pointer,
                model_name=named['name'] if named else None,
                model_source=named['source_path'] if named else None,
                **enqueued_nodes[frame,node]))
        elif pc == 0xE4FF and bank == 0:
            memory.render_node_index = None
        if post_startup and ((bank == 1 and 0xDADE <= pc < 0xDB5D) or 0x5DA0 <= pc < 0x5EDB):
            temporary_entries.add((bank,pc))
        if pc == 0x6F1D:
            assert current is None and bank == 0
            ports.started = True
            ports.active = held
            current = dict(frame=frame,scan_SP=sp,before=state(memory),handlers=[],returns=0,
                           read_start=len(ports.scanner_reads),clip_paths=[],divisors=[],clip_IFF_values=set())
            scans.append(current)
        if current is None:
            return
        if pending_target is not None and pc == pending_target:
            assert bank == 0
            pending_target = None
        if pc == 0x6F4D:
            assert pending_target is None and sp == current['scan_SP']-10
            assert (memory[sp],memory[sp+1]) == (0x4E,0x6F)
            target = registers[H]*256+registers[L]
            current['handlers'].append((len(ports.scanner_reads)-current['read_start']-1,bank,target))
            pending_target = handler = target
        if handler == 0xC0C9 and pending_target is None:
            if pc == 0xC0C9:
                current['clip_before'] = state(memory)
                previous = scans[-2]['clip_before'] if len(scans)>1 else None
                if previous is None or frame in (64,frame_count) or any(current['clip_before'][k] != previous[k]
                        for k in ('first_point','second_point')):
                    current['state_writer_provenance'] = [dict(row) for _,row in sorted(memory.last_state_writers.items())]
                current['write_start'] = len(memory.clip_writes)
                memory.clip_frame = frame
            if memory.clip_frame is not None:
                current['clip_IFF_values'].add(registers[IFF])
                if pc in paths and bank == 0:current['clip_paths'].append(paths[pc])
                if pc == 0xC88C and bank == 0:current['divisors'].append(registers[D]*256+registers[E])
        if pc == 0x6F4E:
            assert pending_target is None and sp == current['scan_SP']-8
            current['returns'] += 1
            if handler == 0xC0C9:
                memory.clip_frame = None
                current['clip_after'] = state(memory)
                current['writes'] = memory.clip_writes[current.pop('write_start'):]
            handler = None
        if pc == 0x6F55:
            assert pending_target is None and sp == current['scan_SP']
            reads = ports.scanner_reads[current.pop('read_start'):]
            assert reads == expected_reads
            assert current['handlers'] == [(i,0,targets[i]) for i in expected_hits]
            assert current['returns'] == len(expected_hits)
            current['after'] = state(memory)
            current['reads'] = len(reads)
            current['clip_IFF_values'] = sorted(current['clip_IFF_values'])
            current = None

    flight = trace_flight(['--verify-flight-cycle','--frames',str(frame_count+1)],boot_simulator=cpu,
        ports_factory=ports_factory,instruction_observer=observe,save_reports=False,
        instruction_limit=2000000 if frame_count == 64 else 4000000)
    assert current is None and pending_target is None and handler is None
    assert pending_random0 is None and pending_distance_store is None
    assert [row['frame'] for row in scans] == list(range(1,frame_count+1))
    assert flight['complete_frame_returns'] == frame_count and flight['frame_entries'] == frame_count+1
    # Сопоставление наблюдавшегося писателя с исходником, банк верхнего окна учитывается отдельно.
    functions = json.loads((ROOT/'Tools/Disasm/Reports/Functions.json').read_bytes())
    for scan in scans:
        if 'clip_before' not in scan:continue
        for writer in scan.get('state_writer_provenance',[]):
            pc = writer['pc']
            region = 'Action' if pc < 0xC000 or writer['selected_upper_bank'] == 0 else 'Controls' if writer['selected_upper_bank'] == 1 else None
            owners = [f for f in functions if f['region'] == region
                      and f['address'] <= pc < f['address']+f['end_offset']-f['offset']]
            writer['source'] = owners[0]['path'] if len(owners)==1 else None
    # Проверка непрерывного байтового курсора по реально наблюдавшимся растровым записям.
    wraps = []
    for scan in scans:
        if 'clip_before' not in scan:continue
        writes = [row for row in scan['writes'] if 0x9000 <= row['address'] < 0x9100]
        before,after = scan['clip_before']['output_size'],scan['clip_after']['output_size']
        assert len(writes)%2 == 0
        assert [row['address'] for row in writes] == [0x9000+((before+i)&255) for i in range(len(writes))]
        assert after == (before+len(writes))&255
        if before+len(writes) >= 256:wraps.append(scan['frame'])
    result = dict(passed=True,method=(f'continuous_{frame_count}_frame_FD02_hold_from_original_ACTION_bootstrap' if held
                  else f'continuous_{frame_count}_frame_idle_control_from_original_ACTION_bootstrap'),
        original_disk_sha256=manifest['sha256'],continuous_complete_frames=frame_count,
        physical_key_row=0xFD,physical_key_mask=2,key_enabled_at_first_scan_and_never_released=held,
        frame_and_keyboard_state_not_reset_between_frames=True,scans=scans,
        expected_handler_targets=[targets[i] for i in expected_hits],total_scanner_reads=sum(row['reads'] for row in scans),
        total_handlers=sum(len(row['handlers']) for row in scans),output_cursor_wrap_frames=wraps,
        other_active_keyboard_reads=[row for row in ports.reads if row[0] != 0x6F34],
        clip_dispatches=dict(clip_probe.dispatches),clip_targets=sorted(clip_probe.targets),
        alias_entries=sorted(clip_probe.alias_entries),post_startup_temporary_entries=sorted(temporary_entries),
        post_startup_control_source_writes=memory.control_writes,
        accepted_interrupts=cpu.interrupts,flight_cycle=flight,
        render_nodes=render_nodes,model_name_registry_sha256=sha256(model_registry_path.read_bytes()).hexdigest(),
        initial_record0=initial_record0,slot0_identity_changes=memory.slot0_identity_changes,
        **{f'state_before_frame{frame_count+1}_first_instruction':state(memory)},
        spawn_schedule_random0_calls=random0_calls,spawn_alternate_entries=alternate_entries,
        original_handlers_and_clipping_code_not_stubbed=True,TR_DOS_calls_stubbed=True,
        IRQ_scheduled_by_existing_flight_model=True,all_game_states_or_keys_proved=False,
        original_author_intent_proved=False,native_execution=False,assembly_executed=False)
    path = ROOT/('Tools/Disasm/Reports/ActionContinuousKeyClipVerification.json' if held
                 else 'Tools/Disasm/Reports/ActionContinuousKeyIdleControlVerification.json')
    if frame_count != 64:
        # Проверка прежнего непрерывного префикса, удлинение не меняет первые 64 кадра.
        baseline = json.loads(path.read_bytes())
        assert baseline['scans'] == json.loads(json.dumps(scans[:64]))
        assert baseline['render_nodes'] == json.loads(json.dumps([row for row in render_nodes if row['frame'] <= 64]))
        path = path.with_name(path.stem+str(frame_count)+path.suffix)
    data = (json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if path.exists():
        previous = json.loads(path.read_bytes())
        comparable = json.loads(json.dumps(result))
        # Проверка всех старых полей, новые сведения о писателях не должны менять прежний запуск.
        def preserved(old,new,path='report'):
            if isinstance(old,dict):
                assert isinstance(new,dict),path
                for key,value in old.items():
                    assert key in new,(path,key)
                    preserved(value,new[key],path+'.'+key)
            elif isinstance(old,list):
                assert isinstance(new,list) and len(old)==len(new),path
                for index,(a,b) in enumerate(zip(old,new)):preserved(a,b,path+'['+str(index)+']')
            else:assert old==new,(path,old,new)
        preserved(previous,comparable)
        if path.read_bytes().replace(b'\r\n',b'\n') != data:
            path.write_bytes(data)
    else:
        path.write_bytes(data)
    print(json.dumps(dict(passed=True,held=held,frames=frame_count,scans=len(scans),wraps=wraps,
        paths=dict(Counter(p for scan in scans for p in scan['clip_paths'])),
        final_size=scans[-1]['after']['output_size'],render_frames=[row['frame'] for row in render_nodes],
        render_models=sorted({row['model_name'] for row in render_nodes}),interrupts=len(cpu.interrupts)),ensure_ascii=False))


if __name__ == '__main__':
    main()
