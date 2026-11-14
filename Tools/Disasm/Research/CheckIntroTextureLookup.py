"""Независимая модель двух стадий таблицы и заполнения пропусков, без сборки.

Документация: ../../../Docs/IntroGeneratedEffects.md#построение-и-заполнение-таблицы-выборок
"""
from hashlib import sha256
from itertools import product
import json

from CheckIntro import ROOT, original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckScreenUpdate import PortTrace
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def reference(coordinates, parameters, opcode, initial_iyl, rom):
    table = bytearray([255]*32768)
    iyl = initial_iyl
    de = 0
    # Построение координат и запись пар, с сохранением последовательного порядка коллизий.
    for number, parameter in enumerate(parameters, 1):
        iyl = parameter if opcode == 0x6F else (iyl+1)&255
        step = 4*number
        origin = 0x4000-256*number
        table[:128] = bytes(((origin+k*step)&65535)>>8 for k in range(128))
        for index in range(256):
            low = (table[coordinates[index]>>1]*2)&255
            high = table[coordinates[(index+64)&255]>>1]|128
            de = high*256+low+1
            table[de-0x8001] = index
            table[de-0x8000] = iyl
    fills = []
    # Два прохода переносят только пары с маркером FF во втором байте.
    for _ in range(2):
        count = 0
        for address in range(0x8100,0x10000,2):
            last_a = table[address+1-0x8000]
            if last_a == 255:
                source = (address+256)&65535
                low = table[source-0x8000] if source>=0x8000 else rom[source]
                high = table[source+1-0x8000] if source>=0x8000 else rom[source+1]
                table[address-0x8000:address+2-0x8000] = bytes((low,high))
                de = high*256+low
                count += 1
        fills.append(count)
    return table, iyl, de, last_a, 0x42|int(last_a<255), fills


def main():
    flat = original_memory()
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text(encoding='utf-8'))
    entry = next(row for row in manifest['entries'] if row['slot']==3)
    disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    for start,end in ((0x6763,0x67F1),(0x6A0B,0x6A13),(0x6A17,0x6A1E)):
        assert bytes(flat[start:end]) == disk[entry['offset']+start-0x6300:entry['offset']+end-0x6300]
    parameters = bytes(flat[0x6663:0x66A2])
    coordinates_cases = [bytes(range(256)),bytes(reversed(range(256))),bytes([0x80]*256)]
    rom_paths = ['48.rom','128-1.rom']
    results = []
    full_alternating_cases = 0
    for case,(opcode,coordinates,rom_name,parameter_case) in enumerate(product((0x6F,0x2C),coordinates_cases,rom_paths,range(3))):
        rom = (ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources'/rom_name).read_bytes()
        banks = [bytearray([0xA0+i]*0x4000) for i in range(8)]
        banks[5][:] = bytes(flat[0x4000:0x8000])
        memory = RecordedBanks(banks=banks,out7ffd=0x14)
        memory.roms = (list(rom),list(rom))
        memory.out7ffd(0x14)
        memory[0x5FFE],memory[0x5FFF] = 255,63
        memory.banks[5][0x2400:0x2500] = coordinates
        current_parameters = parameters if parameter_case==0 else bytes([0 if parameter_case==1 else 255]*63)
        memory.banks[5][0x2663:0x26A2] = current_parameters
        baseline = [bank.copy() for bank in memory.banks]
        expected = [bank.copy() for bank in memory.banks]
        iyl_in = (case*37+0xC0)&255
        table,iyl,de,a,f,fills = reference(coordinates,current_parameters,opcode,iyl_in,rom)
        expected[2][:] = table[:0x4000]
        expected[1][:] = table[0x4000:]
        # Проверка ожидаемых изменяемых операндов и последнего сохранённого BC цикла.
        for address,values in ((0x6786,bytes.fromhex('a266')),(0x678E,bytes([opcode])),
                               (0x6793,bytes.fromhex('fc00')),(0x679E,bytes.fromhex('0001')),
                               (0x5FFC,bytes.fromhex('0001'))):
            expected[5][address-0x4000:address-0x4000+len(values)] = values
        initial = get_registers(dict(PC=0x6763,SP=0x5FFE,AF=opcode*256+0xA5,HL=0x6663,
            DE=0x2468,BC=0x369C,IX=0xABCD,IY=0x5C00|iyl_in,I=case,R=(case*19)&255,
            **{'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),
            {'im':case%3,'iff':case&1},False)
        wanted = list(initial)
        wanted[:12] = [a,f,0,0,de>>8,de&255,0,0,0x64,0,0x5C,iyl]
        wanted[PC],wanted[SP] = 0x3FFF,0x6000
        # Расчёт M1 по фиксированным циклам и числу действительно заполненных пропусков.
        prefix_m1 = sum((1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,65534,1,1))
        pair_m1 = sum((1,1,1,2,1,2,2,1,2,2,1,1,1,2,1,2,1,1))
        m1 = prefix_m1+63*(18+128*7+3+256*pair_m1+2)+2+2*(1+16256*8+2+1)+1+8*sum(fills)
        wanted[R] = (initial[R]&128)|((initial[R]+m1)&127)
        cpu = Simulator(memory)
        cpu.registers[:] = initial
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        cpu.run(0x6763,0x3FFF)
        # Проверка всех физических банков и регистров, исключено только время.
        assert all(cpu.registers[i]==wanted[i] for i in (*range(25),26,27)), (case,[(i,wanted[i],cpu.registers[i]) for i in range(25) if wanted[i]!=cpu.registers[i]])
        assert memory.banks==expected, (case,'RAM',[(b,next((i for i in range(16384) if memory.banks[b][i]!=expected[b][i]),None)) for b in range(8) if memory.banks[b]!=expected[b]])
        assert ports.writes==[(0x7FFD,0x11)] and memory.o7ffd==0x11
        if opcode==0x6F and parameter_case==0:
            # Проверка полного вызывающего входа, включая чтение и преобразование перекрывающейся таблицы.
            full_memory = RecordedBanks(banks=[bank.copy() for bank in baseline],out7ffd=0x14)
            full_memory.roms = (list(rom),list(rom))
            full_memory.out7ffd(0x14)
            full_initial = list(initial)
            full_initial[PC] = 0x6638
            full_wanted = list(wanted)
            source = table[0x2000:0x6000]
            output = bytes(value>>2 if i%2==0 else value for i,value in enumerate(source))
            last_sum = (0x16+output[-1])&255
            final_flags = ((source[-2]>>1)&1)|(last_sum&8)|((last_sum&2)<<4)
            full_wanted[:8] = [0x16,final_flags,0,0,0,0,0xC0,0]
            full_wanted[R] = (initial[R]&128)|((initial[R]+m1+139664)&127)
            full_expected = [bank.copy() for bank in expected]
            full_expected[2][:] = output
            full_expected[6][:] = output
            full_expected[5][0x1FFA:0x1FFC] = bytes.fromhex('0001')
            full_expected[5][0x1FFC:0x1FFE] = bytes.fromhex('6066')
            full_cpu = Simulator(full_memory)
            full_cpu.registers[:] = full_initial
            full_ports = PortTrace(full_cpu)
            full_cpu.set_tracer(full_ports)
            full_cpu.run(0x6638,0x3FFF)
            assert all(full_cpu.registers[i]==full_wanted[i] for i in (*range(25),26,27)),(case,'full registers')
            assert full_memory.banks==full_expected,(case,'full RAM')
            assert full_ports.writes==[(0x7FFD,0x11),(0x7FFD,0x16)] and full_memory.o7ffd==0x16
            full_alternating_cases += 1
        results.append(dict(opcode=opcode,coordinates_case=case//6%3,rom=rom_name,parameter_case=parameter_case,M1=m1,
            rom_sha256=sha256(rom).hexdigest(),fills=fills,A=a,F=f,DE=de,IYL=iyl,
            table_sha256=sha256(table).hexdigest()))
    report = dict(passed=True,total_cases=len(results),profiles=results,full_BuildAlternatingTexture_cases=full_alternating_cases,
        both_opcode_variants=True,all_physical_banks_compared=True,
        exact_registers_except_T=True,original_parameter_count=63,additional_constant_parameters=[0,255],
        all_coordinate_and_parameter_inputs_exhausted=False,
        IRQ_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/IntroTextureLookupVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
