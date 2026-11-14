"""Свидетели изменения R у четырёх процедур точек карты, HALT пробуждается явно.

Документация: ../../../Docs/MapPointRefresh.md
"""
from hashlib import sha256
import json

from CheckRowHighlight import ROOT, make_context
from CheckMusic import Simulator, get_registers, PC, SP
from ReferenceControlsPointRespawn import refresh


class RejectPorts:
    def write_port(self, *arguments):
        raise AssertionError(('Неожиданная запись порта', arguments))

    def read_port(self, *arguments):
        raise AssertionError(('Неожиданное чтение порта', arguments))


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest() == manifest['sha256']
    for slot in (4,7):
        entry = next(row for row in manifest['entries'] if row['slot'] == slot)
        source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
        assert source == disk[entry['offset']:entry['offset']+len(source)]
    _, karta, banks = make_context()
    base = bytearray(65536)
    base[0x4000:0x8000] = bytes(banks[5])
    base[0x8000:0xC000] = bytes(banks[2])
    base[0xC000:0xC000+len(karta)] = karta
    profiles = [
        ('BuildMapPointOutcodes',0xD430,'inside',None),
        ('BuildMapPointOutcodes',0xD430,'negative_and_upper',None),
        ('BuildVisibleMapPoints',0xC4E5,'empty',None),
        ('BuildVisibleMapPoints',0xC4E5,'one_point',None),
        ('SelectNearestVisiblePoint',0xC38C,'outside',None),
        ('SelectNearestVisiblePoint',0xC38C,'one_point',None),
        ('MeasureCoordinateDistance',0xE7BA,'equal',(0,0,0,0)),
        ('MeasureCoordinateDistance',0xE7BA,'small',(0,0,3,4)),
        ('MeasureCoordinateDistance',0xE7BA,'square_overflow',(0,0,256,0))]
    results = []
    changed = set()
    paired = 0
    for name, entry, profile, coordinates in profiles:
        uses_halt = name in ('BuildVisibleMapPoints','SelectNearestVisiblePoint')
        for initial_r in (0,0x95):
            signatures = []
            for halt_cycles in ((1,4) if uses_halt else (0,)):
                memory = bytearray(base)
                initial = get_registers({'SP':0x7FFE,'PC':entry,'HL':0x1357,'DE':0x247A,
                    'BC':0x36C9,'AF':0x5A5C,'IX':0x2468,'IY':0x5C3A,
                    '^HL':0xB000,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
                initial[15] = initial_r
                initial[26] = 0
                memory[0x7FFE:0x8000] = bytes([255,63])
                if name == 'BuildMapPointOutcodes':
                    memory[0xB000] = 1
                    memory[0xF800:0xF900] = bytes(256)
                    if profile == 'negative_and_upper':
                        memory[0xF800:0xF805] = bytes([255,255,0,1,0xA7])
                elif uses_halt:
                    memory[0x6300:0x6306] = bytes([0,0,4,3,2,2])
                    memory[0xF200:0xF600] = bytes([100,100])*512
                    memory[0xF600:0xF800] = bytes([0xA7])*512
                    if profile == 'one_point':
                        memory[0xF200:0xF202] = bytes([1,1])
                    if name == 'SelectNearestVisiblePoint':
                        initial[6:8] = [0x10,0x10]
                        memory[0x6307:0x6309] = bytes([0x11,0x11]) if profile == 'one_point' else bytes(2)
                        memory[0xC3E8:0xC3EA] = bytes([0,0xF6])
                        memory[0x990A:0x9910] = bytes([0x80])*6
                else:
                    x0,y0,x1,y1 = coordinates
                    initial[2:6] = [y0&255,x0&255,y0>>8,x0>>8]
                    initial[18:22] = [y1&255,x1&255,y1>>8,x1>>8]
                cpu = Simulator(memory)
                cpu.registers[:] = initial
                cpu.set_tracer(RejectPorts())
                m1 = wakeups = instructions = 0
                for _ in range(100000):
                    pc = cpu.registers[PC]
                    if pc == 0x3FFF:
                        break
                    first, second = memory[pc], memory[(pc+1)&65535]
                    assert (first,second) != (0xED,0x4F)
                    assert not (first in (0xDD,0xFD) and second in (0xDD,0xFD,0xED))
                    # Подсчёт M1 по достигнутому опкоду, включая повторную выборку префикса.
                    step = 2 if first in (0xCB,0xED,0xDD,0xFD) else 1
                    if first == 0x76:
                        assert pc == 0xC4E5 and uses_halt and wakeups == 0
                        # Выполнение заданного числа HALT-циклов, ISR и его записи не подменяются моделью IRQ.
                        for _ in range(halt_cycles):
                            cpu.run()
                            m1 += 1
                            instructions += 1
                            assert cpu.registers[PC] == pc and cpu.registers[28] == 1
                            assert cpu.registers[15] == refresh(initial_r,m1)
                        # Явное пробуждение после последнего цикла, аппаратный источник не моделируется.
                        cpu.registers[PC] = pc+1
                        cpu.registers[28] = 0
                        wakeups += 1
                    else:
                        cpu.run()
                        m1 += step
                        instructions += 1
                        assert cpu.registers[15] == refresh(initial_r,m1)
                else:
                    raise AssertionError((name,profile,'не завершилось'))
                assert wakeups == int(uses_halt) and cpu.registers[SP] == 0x8000
                assert cpu.registers[15] & 128 == initial_r & 128
                if cpu.registers[15] != initial_r:
                    changed.add(name)
                # Сравнение только двух явно заданных HALT-задержек одного и того же входа.
                signature = ([value for i,value in enumerate(cpu.registers) if i not in (15,25)], bytes(memory))
                signatures.append((m1,signature))
                results.append(dict(function='Map.'+name,entry=entry,profile=profile,
                    initial_R=initial_r,final_R=cpu.registers[15],observed_M1=m1,
                    executed_instruction_and_HALT_cycles=instructions,
                    explicit_HALT_cycles=halt_cycles,wakeups_without_ISR=wakeups))
            if uses_halt:
                assert signatures[1][0] == signatures[0][0]+3
                assert signatures[0][1] == signatures[1][1]
                paired += 1
    assert changed == {row[0] for row in profiles} and len(results) == 26 and paired == 8
    report = dict(passed=True,method='original_map_point_procedures_opcode_prefix_refresh_witnesses',
        original_disk_sha256=manifest['sha256'],cases=len(results),profiles=results,
        all_four_procedures_have_changed_R_witness=True,
        R_checked_after_every_instruction_and_HALT_cycle=True,
        paired_explicit_HALT_delay_comparisons=paired,
        three_extra_HALT_cycles_add_three_M1_without_other_final_state_changes_in_pairs=True,
        initial_R_high_bit_preserved=True,functions_stubbed=False,
        source_tables_and_saved_variant_records_are_fixtures=True,
        IRQ_ISR_or_native_HALT_wakeup_proved=False,all_input_paths_and_M1_costs_proved=False,
        hardware_bus_timing_proved=False,assembly_executed=False,native_execution=False)
    path = ROOT/'Tools/Disasm/Reports/MapPointRefreshWitnessVerification.json'
    data = (json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if path.exists():
        assert path.read_bytes().replace(b'\r\n',b'\n') == data, 'Отчёт отличается, автоматическая замена запрещена'
    else:
        path.write_bytes(data)
    print('26 исходных вызовов, четыре изменяемых R, восемь пар заданной HALT-задержки, точные M1 контрольных входов.')


if __name__ == '__main__':
    main()
