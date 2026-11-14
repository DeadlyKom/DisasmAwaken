"""Условный подбор записи, действительно созданной EjectMine, без подмены её полей.

Документация: ../../../Docs/ActionEjectCommands.md
Документация: ../../../Docs/ActionTractorCollect.md
Документация: ../../../Docs/ActionFrameGates.md
Документация: ../../../Docs/ActionNoiseExit.md
"""
from collections import Counter
from hashlib import sha256
import json

from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC
from ReferenceActionTractorCollect import TractorCollectMachine
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from skoolkit.simutils import I,IFF,IM,R,T,SP

SHIELD_INPUTS = (0,1,3,4,39,40,41,42,43,44,255)


def first_noise_irq_profiles(memory,cpu,counts):
    """Два явно подготовленных состояния системных переменных, оригинальный HALT и ROM IM 1."""
    from CheckActionNoiseExit import NoiseMatrix,PERIOD
    assert cpu.registers[PC] == 0x607B and cpu.registers[IM] == 1
    for frames in (0,65535):
        clone = Memory(banks=[bytearray(bank) for bank in memory.banks],out7ffd=16)
        clone.roms = memory.roms
        # Системные переменные задают отдельные входные условия ROM, они не получены предыдущим игровым запуском.
        clone[0x5C00] = clone[0x5C04] = 255
        clone[0x5C3B] = 8
        put(clone,0x5C78,bytes((frames&255,frames>>8,0x52)))
        irq_cpu = Simulator(clone,config={'frame_duration':PERIOD,'int_active':36})
        irq_cpu.registers[:] = cpu.registers
        tracer = NoiseMatrix(irq_cpu,100)
        irq_cpu.set_tracer(tracer)
        registers = irq_cpu.registers
        saved = registers.copy()
        pool = bytes(clone[address] for address in range(0xA100,0xA780))
        stock,inventory = clone[0x9C14],clone[0x9BD4]
        clone.writes,clone.recording = [],True
        # Исполнение HALT до активного интервала модельного IRQ, затем реальный вход ROM по #0038.
        for _ in range(PERIOD//4+1):
            irq_cpu.run()
            if registers[PC] == 0x607C:
                break
        else:
            raise AssertionError('Первый шумовой HALT не дождался IRQ')
        assert registers[T]%PERIOD < 36
        assert irq_cpu.accept_interrupt(registers,clone,0x607B) and registers[PC] == 0x0038
        low_sp = registers[SP]
        for _ in range(1024):
            if registers[PC] == 0x607C:
                break
            low_sp = min(low_sp,registers[SP])
            irq_cpu.run()
        else:
            raise AssertionError('ROM IM 1 не вернула управление к DI')
        clone.recording = False
        assert registers[:15] == saved[:15] and registers[16:24] == saved[16:24]
        assert registers[IM] == 1 and registers[IFF] and clone.o7ffd == 16
        expected_frames = ((frames+1)&65535)|(0x53 if frames==65535 else 0x52)<<16
        assert int.from_bytes(bytes(clone[address] for address in range(0x5C78,0x5C7B)),'little') == expected_frames
        assert bytes(clone[address] for address in range(0xA100,0xA780)) == pool
        assert (clone[0x9C14],clone[0x9BD4],clone[0xA794]) == (stock,inventory,39)
        assert all(bank != 0 for bank,offset,value in clone.writes)
        assert tracer.reads == [] and tracer.writes == []
        irq_cpu.run()
        assert registers[PC] == 0x607D and not registers[IFF]
        counts['first_noise_IRQ_cases'] += 1
        counts['first_noise_IRQ_FRAMES_wrap' if frames==65535 else 'first_noise_IRQ_FRAMES_plain'] += 1
        counts['first_noise_IRQ_min_SP_'+hex(low_sp)] += 1


def noise_prefix_to_first_halt(memory,cpu,ports,counts,first_irq=False):
    """Продолжение реального перехода по #6054, до исполнения первого HALT."""
    assert cpu.registers[PC] == 0x6054 and memory[0xA78C] == 0 and memory[0xA794] == 39
    initial_sp = cpu.registers[12]
    saved_pool = bytes(memory[address] for address in range(0xA100,0xA780))
    stock,inventory = memory[0x9C14],memory[0x9BD4]
    virtual = {address:memory.banks[1][address-0xC000] for address in range(QUEUE,QUEUE+34)}
    for address in (PRODUCER,PRODUCER+1):
        virtual[address] = memory.banks[1][address-0xC000]
    expected_queue = dict(virtual)
    queued = insert(virtual,0xF2A5)
    for address,value in queued['writes']:
        expected_queue[address] = value
    memory.writes,ports.events,memory.recording = [],[],True
    expected_buffer,seed = None,None
    for _ in range(5000):
        pc = cpu.registers[PC]
        if pc == 0x607B:
            break
        if pc == 0x6070:
            # ED 5F выполняет две выборки M1 до получения байта из R.
            old_r = cpu.registers[R]
            seed = (old_r&128)|((old_r+2)&127)
            expected_buffer = bytes(memory[0x500+seed+i] for i in range(0xC00))
        cpu.run()
    else:
        raise AssertionError('Шумовой префикс не достиг первого HALT')
    memory.recording = False
    assert expected_buffer is not None
    assert bytes(memory[address] for address in range(0x8000,0x8C00)) == expected_buffer
    assert cpu.registers[12] == initial_sp-2
    assert memory[initial_sp-2] == 4 and memory[initial_sp-1] == 100
    assert cpu.registers[I] == 0x3F and cpu.registers[10]*256+cpu.registers[11] == 0x5C3A
    assert cpu.registers[IFF] and cpu.registers[2:4] == [0,0]
    assert cpu.registers[4]*256+cpu.registers[5] == 0x8C00
    assert cpu.registers[6]*256+cpu.registers[7] == 0x1100+seed
    assert memory[0xECF6] == 0x4D and memory[0xECF7] == 0xEE
    for address,value in expected_queue.items():
        assert memory.banks[1][address-0xC000] == value
    assert ports.events == [(0x7FFD,17),(0x7FFD,16)] and memory.o7ffd == 16
    assert (memory[0x9C14],memory[0x9BD4],memory[0xA794]) == (stock,inventory,39)
    assert bytes(memory[address] for address in range(0xA100,0xA780)) == saved_pool
    counts['noise_prefix_cases'] += 1
    counts['destroyed_text_queued' if queued['accepted'] else 'destroyed_text_dropped'] += 1
    counts['noise_ROM_seed_'+hex(seed)] += 1
    if first_irq:
        first_noise_irq_profiles(memory,cpu,counts)


def frame_event_window(memory,cpu,ports,counts,noise_prefix=False,first_irq=False):
    """Исходный участок A8EB..A97D, точный порядок записей и остановка перед шумовым выходом."""
    saved = [bytearray(bank) for bank in memory.banks]
    for energy in SHIELD_INPUTS:
        memory.recording = False
        for bank,raw in zip(memory.banks,saved):
            bank[:] = raw
        memory.out7ffd(16)
        memory[0xA794] = energy
        flags,blink,phase = memory[0xA78C],memory[0xA92D],memory[0xA966]
        assert memory[0xA968] == 0x50
        expected = [bytearray(bank) for bank in memory.banks]
        writes = []
        def write(address,value):
            bank = 5 if address < 0x8000 else 2 if address < 0xC000 else 0
            expected[bank][address&0x3FFF] = value
            writes.append((bank,address&0x3FFF,value))
        value,failure = energy,False
        # Биты проверяются по сохранённой маске, очистка памяти не отменяет последующие события.
        if flags&1:
            write(0xA78C,0)
            write(0xECA9,0x22); write(0xECAA,0xEF)
            cost = next((3-i for i in range(3) if memory[0x9C1C+i] != 255),4)
            failure = value < cost
            if not failure:
                value -= cost
                write(0xA794,value); write(0x664A,1)
        if not failure:
            if flags&2:
                write(0xA92D,(blink>>1)|((blink&1)<<7))
                if blink&1:
                    write(0xECF6,0x8F); write(0xECF7,0xED)
                write(0x5A1C,0x35 if blink&1 else 5)
                write(0xA78C,0)
            else:
                write(0x5A1C,5)
            if flags&4:
                write(0xA78C,0)
                failure = value < 40
                if not failure:
                    value -= 40
                    write(0xA794,value); write(0x664A,1)
            if not failure:
                write(0xA966,(phase+80)&255)
                if phase >= 176 and value < 46:
                    write(0xA794,value+1); write(0x664A,1)
        cpu.registers[:] = get_registers(dict(PC=0xA8EB,SP=0xBFFE,HL=0x1357,DE=0x2468,BC=0x369C),None,False)
        memory.writes,ports.events,memory.recording = [],[],True
        for _ in range(150):
            if cpu.registers[PC] in (0x6054,0xA97E):
                break
            cpu.run()
        else:
            raise AssertionError('Участок событий не завершился')
        memory.recording = False
        assert cpu.registers[PC] == (0x6054 if failure else 0xA97E)
        assert cpu.registers[12] == 0xBFFE
        assert memory.banks == expected and memory.writes == writes
        assert ports.events == [] and memory.o7ffd == 16
        counts['event_windows'] += 1
        counts['noise_transfer' if failure else 'event_window_complete'] += 1
        if noise_prefix and failure and flags == 4 and energy == 39:
            noise_prefix_to_first_halt(memory,cpu,ports,counts,first_irq=first_irq)


def main(frame_events=False,noise_prefix=False,first_irq=False):
    # Проверка ранее установленных исходных цепочек и идентичности созданного класса.
    for name in ('ActionEjectCommandsVerification','ActionTractorCollectVerification','ActionCargoIdentityVerification'):
        assert json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_bytes())['passed']
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    sources = {}
    for slot in (17,22,23):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        sources[slot] = (ROOT/(entry['path']+'.bin')).read_bytes()
        assert sources[slot] == disk[entry['offset']:entry['offset']+entry['length']]
    flat = flat_action()
    assert bytes(flat[0x6000:0x7F8F]) == sources[17][0x23D:0x21CC]
    assert bytes(flat[0x7F8F:]) == sources[17][0x1F8F:]
    control = base_memory()
    assert bytes(control[0xDADE:0xDADE+len(sources[23])]) == sources[23]
    baseline = [bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5],baseline[2],baseline[0] = bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1] = bytearray(base_memory()[0xC000:])
    memory = Memory(banks=[bytearray(bank) for bank in baseline],out7ffd=16)
    cpu = Simulator(memory)
    ports = Ports(memory)
    cpu.set_tracer(ports)
    # Положительный контроль записи в физический банк через CPU, затем сценарии восстанавливают все банки.
    put(memory,0x4000,bytes.fromhex('3E6B320070'))
    memory.writes,memory.recording = [],True
    cpu.run(start=0x4000,stop=0x4005)
    memory.recording = False
    assert memory.writes == [(5,0x3000,0x6B)]
    counts,paths = Counter(),Counter()
    for slot in (0,12,24):
        for stock in (1,255):
            for stored in (0,199,200,255):
                for current in (0,254,255):
                    for limit in (0,255):
                        for full_queue in (False,True):
                            for old_flags in (0,0xA9,255):
                                memory.recording = False
                                for bank,raw in zip(memory.banks,baseline):
                                    bank[:] = raw
                                memory.out7ffd(16)
                                # Подготовка родителя и пула, координаты ребёнка получаются нулевыми настоящим сложением с 200.
                                for index in range(25):
                                    address = 0xA100+64*index
                                    memory[address],memory[address+1],memory[address+24] = 0,1,0
                                child = 0xA100+64*slot
                                memory[child+1] = 128
                                put(memory,0xA740,(128,128))
                                put(memory,0xA780,bytes.fromhex('38FF38FF38FF'))
                                for offset in (7,8,9,16):
                                    memory[0xA780+offset] = 0
                                memory[0xA78C] = old_flags
                                put(memory,0x9BD2,(current,limit))
                                memory[0x9BD4],memory[0x9C14],memory[0xA85F] = stored,stock,0
                                memory[0x7318] = 1
                                put(memory,0x73A4,(0x34,0x12))
                                memory[0xA8BC] = 255
                                put(memory,0x9B19,(119,43))
                                for index in range(16):
                                    memory.banks[1][0x2C80+2*index] = 1 if full_queue else 128
                                    memory.banks[1][0x2C81+2*index] = (index*37)&255
                                memory.banks[1][0x2CA0:0x2CA2] = bytes(2)
                                memory.banks[1][0x2C5D:0x2C5F] = bytes.fromhex('80EC')
                                put(memory,0xBFFE,(255,63))
                                initial = get_registers(dict(PC=0x75CF,SP=0xBFFE,AF=0xA5EF,HL=0x1357,DE=0x2468,
                                    BC=0x369C,IX=0xABCD,IY=0x5C3A,
                                    **{'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),None,False)
                                cpu.registers[:] = initial
                                ports.events = []
                                # Настоящая команда мины исполняется до внешнего возврата с реальным создателем и очередью.
                                for _ in range(3500):
                                    if cpu.registers[PC] == 0x3FFF:
                                        break
                                    cpu.run()
                                else:
                                    raise AssertionError('EjectMine не вернулась')
                                assert memory[0x9C14] == stock-1
                                assert cpu.registers[10]*256+cpu.registers[11] == child
                                assert bytes(memory[child+i] for i in range(6)) == bytes(6)
                                assert (memory[child+6],memory[child+10],memory[child+17],memory[child+18],memory[child+24],memory[child+35]) == (0x98,4,1,0x13,0x10,0)
                                assert memory[0x9BD4] == stored and memory[0xA78C] == old_flags
                                assert ports.events == [(0x7FFD,17),(0x7FFD,16)]
                                # Выбор созданной цели задаёт сценарий, поля ребёнка и очередь после выброса не сбрасываются.
                                memory[0x9B1B] = slot
                                put(memory,0xBFFE,(255,63))
                                collect_initial = get_registers(dict(PC=0x7317,SP=0xBFFE,AF=0xA5EF,HL=0x1357,DE=0x2468,
                                    BC=0x369C,IX=0xABCD,IY=0x5C3A,
                                    **{'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),None,False)
                                model = TractorCollectMachine(memory.banks,collect_initial)
                                model.collect_or_aim()
                                cpu.registers[:] = collect_initial
                                memory.writes,ports.events,memory.recording = [],[],True
                                for _ in range(7000):
                                    if cpu.registers[PC] == 0x3FFF:
                                        break
                                    cpu.run()
                                else:
                                    raise AssertionError('Подбор созданной записи не вернулся')
                                memory.recording = False
                                compared = (*range(13),14,*range(16,24),PC,26,27)
                                assert all(cpu.registers[i] == model.r[i] for i in compared)
                                model.banks[2][0x3FEC:0x3FFE] = memory.banks[2][0x3FEC:0x3FFE]
                                assert memory.banks == model.banks
                                def outside(rows):
                                    return [row for row in rows if row[0] != 2 or not 0x3FEC <= row[1] < 0x3FFE]
                                assert Counter(outside(memory.writes)) == Counter(outside(model.writes))
                                assert ports.events == model.ports and memory.o7ffd == 16
                                # Независимая проверка итогов по фактическому неизменённому правилу вида 0.
                                rule = memory[0x741D]
                                candidate = (current+1)&255 if rule&192 == 0 else current
                                accepted = (rule&192 != 0 or candidate <= limit) and ((stored+1)&255) < 201
                                assert memory[0x9B1B] == 255 and memory[0x9C14] == stock-1
                                assert memory[0x9BD4] == (((stored+1)&255) if accepted else stored)
                                assert memory[0x9BD2] == (candidate if accepted else current)
                                assert memory[0xA78C] == (old_flags|4 if accepted else old_flags)
                                assert memory[child+1] == (128 if accepted else 0)
                                counts['accepted' if accepted else 'refused'] += 1
                                counts['full_queue' if full_queue else 'empty_queue'] += 1
                                counts['cases'] += 1
                                paths.update(model.path)
                                if frame_events:
                                    frame_event_window(memory,cpu,ports,counts,noise_prefix=noise_prefix,first_irq=first_irq)
    assert counts['cases'] == 864 and counts['accepted'] and counts['refused']
    result = dict(passed=True,method='original_eject_mine_then_selected_original_collection',
        original_disk_sha256=manifest['sha256'],original_logical_files_checked=[17,22,23],
        original_common_code_relocation_checked=True,CPU_write_watch_positive_probe_passed=True,
        counts=dict(counts),collector_paths=dict(paths),original_kind0_rule=baseline[5][0x341D],
        child_fields_not_overwritten_between_calls=True,queue_not_reset_between_calls=True,
        mine_stock_remains_spent_after_collection=True,accepted_pickup_increments_inventory_byte_9BD4=True,
        accepted_pickup_sets_ActionPanelEvents_Flags_bit2=True,
        created_record_marked_free_only_after_accepted_pickup=True,
        target_cleared_even_on_capacity_or_byte_limit_refusal=True,
        collector_registers_except_R_T_and_RAM_and_write_multiplicity_checked=True,
        collector_18_byte_temporary_stack_values_excluded=True,
        eject_phase_checks_critical_postconditions_and_ports_only=True,
        target_selection_is_fixture=True,parent_coordinates_chosen_for_near_child=True,
        full_native_mine_or_flight_behavior_proved=False,
        IRQ_executed=False,assembly_executed=False,native_execution=False)
    if frame_events:
        assert counts['event_windows'] == counts['cases']*len(SHIELD_INPUTS) == 9504
        result.update(frame_event_window_start=0xA8EB,frame_event_window_end_exclusive=0xA97E,
            frame_event_window_cases=9504,shield_inputs=list(SHIELD_INPUTS),
            original_shield_equipment_bytes=list(baseline[2][0x1C1C:0x1C1F]),
            original_cost_bit0_amount=next((3-i for i in range(3) if baseline[2][0x1C1C+i] != 255),4),
            original_regen_phase=baseline[2][0x2966],original_blink_phase=baseline[2][0x292D],
            original_regen_step_80_required=True,
            full_banked_RAM_and_exact_event_write_order_checked=True,event_window_SP_preserved=True,
            real_noise_loader_not_executed=True,whole_frame_before_event_window_not_executed=True,
            event_window_registers_except_SP_PC_not_independently_checked=True)
    target = 'EjectedMineCollectionFrameEventsVerification.json' if frame_events else 'EjectedMineCollectionVerification.json'
    if noise_prefix:
        assert counts['noise_prefix_cases'] == 144
        assert counts['destroyed_text_queued'] == counts['destroyed_text_dropped'] == 72
        result.pop('real_noise_loader_not_executed')
        result.update(noise_prefix_cases=144,noise_prefix_start=0x6054,noise_prefix_stop_before_HALT=0x607B,
            noise_prefix_pure_new_bit2_and_shield39_only=True,
            event_window_registers_initialized_by_fixture=True,event_window_initial_R=0,
            collector_R_not_propagated_into_event_window=True,
            noise_model_ROM1_sha256=sha256(bytes(memory.roms[1])).hexdigest(),
            destroyed_text_F2A5_queue_and_producer_checked=True,noise_CursorB_EE4D_checked=True,
            exact_first_3072_byte_ROM_buffer_checked=True,
            prefix_HL_DE_BC_SP_I_IY_IFF_and_pushed_BC_checked=True,
            record_pool_inventory_and_mine_stock_preserved_through_prefix=True,
            noise_prefix_all_RAM_flags_R_T_and_write_order_not_independently_checked=True,
            HALT_ROM_interrupt_and_noise_display_not_executed=True,
            keyboard_and_station_reload_not_executed=True)
        target = 'EjectedMineNoisePrefixVerification.json'
    if first_irq:
        assert noise_prefix and counts['first_noise_IRQ_cases'] == 288
        assert counts['first_noise_IRQ_FRAMES_wrap'] == counts['first_noise_IRQ_FRAMES_plain'] == 144
        result.pop('HALT_ROM_interrupt_and_noise_display_not_executed')
        result.update(first_noise_IRQ_cases=288,first_noise_IRQ_frame_period=70908,
            first_noise_IRQ_input_FRAMES_low_words=[0,65535],first_noise_IRQ_input_FRAMES_high_byte=0x52,
            first_noise_IRQ_sysvars_prepared_after_prefix=True,
            first_noise_IRQ_KSTATE_slots_FF_and_FLAGS_08=True,
            first_noise_HALT_and_original_ROM_IM1_executed=True,
            first_noise_IRQ_architectural_registers_except_R_T_PC_preserved=True,
            first_noise_IRQ_FRAMES_24bit_and_DI_checked=True,
            first_noise_IRQ_did_not_write_bank0_or_object_pool=True,
            first_noise_IRQ_all_RAM_refresh_and_cycle_bus_sequence_not_independently_modelled=True,
            viewport_noise_display_not_executed=True,
            IRQ_executed=True,IRQ_scope_first_noise_HALT_clones_only=True)
        target = 'EjectedMineFirstIrqVerification.json'
    (ROOT/'Tools/Disasm/Reports'/target).write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,counts=dict(counts),original_kind0_rule=result['original_kind0_rule']),indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame-events',action='store_true')
    parser.add_argument('--noise-prefix',action='store_true')
    parser.add_argument('--first-noise-irq',action='store_true')
    args = parser.parse_args()
    main(args.frame_events or args.noise_prefix or args.first_noise_irq,
         noise_prefix=args.noise_prefix or args.first_noise_irq,first_irq=args.first_noise_irq)
