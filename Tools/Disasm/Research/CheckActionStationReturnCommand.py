"""7606, настоящий переход в Controls.PrepareStationReload до перенесённого входа 4200."""
from collections import Counter
import json,sys
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckControlsTextQueue import base_memory
from CheckActionTextQueueCalls import Memory,Ports
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from CheckActionRecordSearch import inc_flags
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000])
    baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    counts=Counter()
    def cost(end):return sum(2 if i.bytes[0] in (0xCB,0xED,0xDD,0xFD) else 1 for i in decoder(flat).disassemble(0x7606,end,'h'))
    def check(delay,equipment,pattern=0):
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16);serial=counts['cases']
        # Подготовка исходных состояния и атрибутов, произвольная следующая стадия только копируется и не исполняется.
        blob=bytes((pattern+109*i)&255 for i in range(512));payload=bytes((3*pattern+73*i)&255 for i in range(256))
        put(memory,0x9BBD,blob);memory.banks[1][0x1D23:0x1E23]=payload
        memory[0xA85F]=delay;memory[0x9C27]=equipment;put(memory,0xBFFE,[255,63])
        memory.banks[5][0x1800:0x1B00]=bytes((pattern+31*i)&255 for i in range(768))
        expected=[bytearray(b) for b in memory.banks]
        initial=get_registers({'AF':0xA5EF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5678,'PC':0x7606,'SP':0xBFFE},None,False)
        initial[14]=serial&255;initial[15]=pattern;initial[26]=serial&1;initial[27]=serial%3
        wanted=list(initial);wanted_ports=[];wanted[PC]=0x3FFF;wanted[SP]=0xC000;changes=[]
        def byte(bank,offset,value):expected[bank][offset]=value;changes.append((bank,offset,value))
        if delay:
            wanted[:2]=[delay,and_flags(delay)];m1=cost(0x760B);counts['delay_exit']+=1
        else:
            byte(0,0x2CA9,27);byte(0,0x2CAA,238);byte(2,0x285F,20);wanted[6:8]=[238,27]
            if equipment==255:
                wanted[:2]=[0,0x50];m1=cost(0x761B);counts['missing_equipment']+=1
            else:
                byte(2,0x1C27,255);wanted_ports=[(0x7FFD,25)]
                # Расчёт конечного состояния трёх переносов и счётчика, независимо от последовательности инструкций ребёнка.
                low=expected[2][0x1BBF];high=expected[2][0x1BC0]
                byte(2,0x1BBF,high);byte(2,0x1BC0,low)
                saved=bytes(expected[2][0x1BBD:0x1DBD])
                for i in range(768):byte(5,0x1800+i,0)
                for i,value in enumerate(saved):byte(5,i,value)
                byte(5,0x1FFD,0);byte(5,0x1FFE,0x42)
                for i,value in enumerate(payload):byte(5,0x200+i,value)
                addition=(low+payload[-1])&255;flags=inc_flags(equipment,0)
                wanted[:8]=[63,(flags&0xC1)|(addition&8)|((addition&2)<<4),0,0,0x43,0,0xDE,0x23]
                wanted[10:13]=[0x5C,0x3A,0x5FFF];wanted[14]=63;wanted[PC]=0x4200;wanted[26]=0;wanted[27]=1
                m1=cost(0x762A)+3097;counts['prepared_station_entry']+=1
        wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial;ports.events=[];memory.writes=[];memory.recording=True
        for _ in range(5000):
            if simulator.registers[PC]==wanted[PC]:break
            simulator.run()
        else:raise AssertionError(('граница',delay,equipment))
        memory.recording=False
        assert all(simulator.registers[i]==wanted[i] for i in (*range(13),14,15,*range(16,24),PC,26,27)),[(i,simulator.registers[i],wanted[i]) for i in (*range(13),14,15,*range(16,24),PC,26,27) if simulator.registers[i]!=wanted[i]]
        assert memory.banks==expected
        assert Counter(memory.writes)==Counter(changes)
        assert ports.events==wanted_ports and memory.o7ffd==(25 if wanted_ports else 16)
        counts['cases']+=1
    # Проверка каждого байта допуска, каждого кода оборудования и всех граничных сумм последнего LDIR.
    for delay in range(256):check(delay,254)
    for equipment in range(256):check(0,equipment)
    for pattern in range(256):
        for equipment in (0,127,128,254,255):check(0,equipment,pattern)
    result=dict(passed=True,total_cases=counts['cases'],counts=dict(counts),
        actual_station_prepare_executed=True,all_registers_except_T_checked=True,
        all_physical_ram_and_write_multiplicity_checked=True,exact_OUT_and_refresh_checked=True,
        successful_entry_not_a_return=True,stop_before_relocated_4200=True,
        TRDOS_and_station_loading_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionStationReturnCommandVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
