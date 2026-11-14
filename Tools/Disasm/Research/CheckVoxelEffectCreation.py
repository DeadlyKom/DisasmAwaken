"""Четыре входа создания эффекта, исходный поиск и полные физические изменения.

Документация: ../../../Docs/Effects.md#полные-договоры-создания-эффектов
"""
from collections import Counter
from itertools import product
from struct import pack
import json

from CheckEffects import ROOT, memory_image
from CheckActionParameterActivation import RecordedBanks
from CheckScreenUpdate import PortTrace
from CheckActionVertexCodes import logic_flags
from CheckStationFlightCycle import payload
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def main():
    flat = memory_image()
    assert bytes(flat[0xEC00:0xEC7F])==payload(21)[:0x7F]
    counts = Counter()
    m1_by_outcome = {}
    for entry,occupied,fail,seed in product((0xEC00,0xEC0E,0xEC1B,0xEC33),(0,1,7),(False,True),range(256)):
        banks = [bytearray([0xA0+i]*0x4000) for i in range(8)]
        banks[3][:] = bytes(flat[0xC000:])
        memory = RecordedBanks(banks=banks,out7ffd=0x13)
        memory[0xBFFE],memory[0xBFFF] = 255,63
        memory.banks[5][0x3000:0x3090] = bytes((seed+i*37)&255 for i in range(144))
        for index in range(occupied):
            memory[0x7007+18*index] = 1+(seed+index)%127
        target = 0x7000+18*occupied
        terminal = 0x80|(seed&127) if fail else 0
        memory[target+7] = terminal
        mode,reload,width,height = seed^0xA5,(seed*29)&255,seed^0x55,seed^0xAA
        # Настройка произвольного допустимого содержимого четырёх исходных операндов.
        for address,value in ((0xEC5A,mode),(0xEC6C,reload),(0xEC79,width),(0xEC7D,height)):
            memory[address] = value
        initial = get_registers(dict(PC=entry,SP=0xBFFE,HL=0x1357,DE=0x2468,BC=0x369C,
            AF=(seed<<8)|((seed*43)&255),IX=0xABCD,IY=0x6FEE,I=seed,R=seed,
            **{'^AF':(((seed*73)&255)<<8)|(seed^0x5A),'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),
            {'im':seed%3,'iff':seed&1},False)
        wanted = list(initial)
        expected = [bank.copy() for bank in memory.banks]
        writes = Counter()
        hl,de,prefix_m1 = 0x1357,0x2468,0
        parameters = {}
        if entry==0xEC00:
            hl,de,prefix_m1 = 0xD800,0x00C0,10
            mode,reload,width,height = seed,13,12,12
            parameters = {0xEC5A:mode,0xEC7D:height,0xEC79:width,0xEC6C:reload}
        elif entry==0xEC0E:
            reload,width,prefix_m1 = 13,12,5
            parameters = {0xEC79:width,0xEC6C:reload}
        elif entry==0xEC1B:
            hl,de,prefix_m1 = 0xC400,0x0280,9
            mode,reload,width,height = seed,8,20,20
            parameters = {0xEC5A:mode,0xEC7D:height,0xEC79:width,0xEC6C:reload}
        for address,value in parameters.items():
            expected[3][address-0xC000] = value
            writes[3,address-0xC000,value] += 1
        wanted[2:8] = [0,18,de>>8,de&255,hl>>8,hl&255]
        wanted[10:12] = [target>>8,target&255]
        wanted[SP],wanted[PC] = 0xC000,0x3FFF
        if fail:
            wanted[0:2] = [terminal,logic_flags(terminal)|0x10]
            allocator_m1 = 1+7*occupied+6
        else:
            # Создание всех 18 байтов, даже нулевое либо отрицательное новое State не отвергается.
            record = pack('<HHHBBHHBBHBB',0x1234,0x5678,0x9ABC,mode,initial[16],hl,hl,1,reload,de,width,height)
            expected[5][target-0x4000:target-0x4000+18] = record
            writes.update((5,target-0x4000+i,value) for i,value in enumerate(record))
            wanted[0:2] = [reload,initial[17]]
            wanted[16:18] = [0,0x54]
            allocator_m1 = 49+7*occupied
        m1 = prefix_m1+allocator_m1
        wanted[R] = (initial[R]&128)|((initial[R]+m1)&127)
        cpu = Simulator(memory)
        cpu.registers[:] = initial
        ports = PortTrace(cpu)
        cpu.set_tracer(ports)
        memory.writes = []
        memory.recording = True
        cpu.run(entry,0x3FFF)
        memory.recording = False
        # Проверка всех регистров кроме времени, восьми банков и точной кратности каждой записи.
        assert all(cpu.registers[i]==wanted[i] for i in (*range(25),26,27)),(hex(entry),occupied,fail,seed,[(i,wanted[i],cpu.registers[i]) for i in range(25) if wanted[i]!=cpu.registers[i]])
        assert memory.banks==expected,(entry,occupied,fail,seed,'RAM')
        assert Counter(memory.writes)==writes,(entry,occupied,fail,seed,'writes')
        assert not ports.writes and memory.o7ffd==0x13
        outcome=f'{entry:04X}_'+('negative_end' if fail else 'allocated')
        counts[outcome] += 1
        m1_by_outcome.setdefault(outcome,set()).add(m1)
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_entry_and_outcome=dict(counts),
        observed_M1={key:sorted(value) for key,value in m1_by_outcome.items()},
        all_mode_and_new_state_bytes_observed=True,occupied_prefix_lengths=[0,1,7],
        exact_registers_except_T=True,all_physical_banks_and_write_multiplicities_compared=True,
        new_zero_or_negative_state_not_rejected=True,CPU_stack_writes=0,ports_written=0,
        all_joint_inputs_exhausted=False,IRQ_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/VoxelEffectCreationVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
