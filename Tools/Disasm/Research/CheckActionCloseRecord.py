"""Три входа E506, E51F и E54A, реальные инверсия и банковая передача, цель DCE3 не исполняется."""
from collections import Counter
from itertools import product
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from CheckMusicGateTicks import xor_flags
from CheckActionTypeDelta import cp_flags
from ReferenceControlsPointRespawn import refresh
COMPONENTS=(0xE5B3,0xE5D2,0xE5ED)


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory);counts=Counter();touched=set()
    def check(entry=0xE506,class_code=0,gate=0,reuse=16,highs=(0,0,0),old=16,scalar=None):
        nonlocal touched
        memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old);serial=sum(counts.values());record=0xA100+64*(serial%25)
        memory[record+18],memory[record+24]=class_code,reuse
        for offset,value in zip((1,3,5),highs):memory[record+offset]=value
        memory[0xE507],memory[0xA794],memory[0x6EAD]=gate,0x77,0x5A
        scalar=(serial*73)&65535 if scalar is None else scalar
        components=(0x1357,0xACE0,(serial*257)&65535)
        for address,value in zip((*COMPONENTS,0xA78F),(*components,scalar)):put(memory,address,[value&255,value>>8])
        put(memory,0xBFFE,[255,63])
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(serial*73)&65535,'^HL':record if entry==0xE506 else 0xA400,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD if entry==0xE506 else record,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=[bytearray(b) for b in memory.banks];writes=[];ports=[];m1=0;depth=0
        def byte(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            index=address&0x3FFF;expected[bank][index]=value;writes.append((bank,index,value))
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        action=None
        # Проверка отдельного корневого входа и двух дополнительных входов, их условия не подменяют друг друга.
        if entry==0xE506:
            m1=3;wanted[0:2]=[gate,and_flags(gate)]
            if gate:action='blocked'
            else:
                word(0xBFFC,record);wanted[8:10]=[record>>8,record&255];depth=2;m1+=5+2+2
                wanted[0:2]=[class_code,cp_flags(class_code,17)]
                if class_code==17:action='ignored_11'
                else:
                    m1+=2;wanted[1]=cp_flags(class_code,20)
                    if class_code==20:action='ignored_14'
                    else:
                        m1+=2;wanted[1]=cp_flags(class_code,18)
                        if class_code==18:m1+=1;action='transfer_root'
                        else:action='reverse'
        elif entry==0xE51F:
            m1=3
            if not reuse&16:action='reverse'
            else:
                for high in highs:
                    folded=(~high)&255 if high>=128 else high;m1+=6+int(high>=128)
                    wanted[0:2]=[folded,cp_flags(folded,4)]
                    if folded>=4:action='reverse';break
                else:action='transfer_components'
        else:assert entry==0xE54A;action='reverse'
        if action.startswith('transfer'):
            # Создание эталона рамок настоящего селектора в общем коде, внешний возврат остаётся на стеке.
            word(0xBFFC,0x6CEC);word(0xBFFA,0x369C);depth=4;m1+=10
            wanted[0]=17;wanted[4:6]=[0,0];wanted[PC]=0xDCE3;ports=[(0x7FFD,17)]
        elif action=='reverse':
            # Обновление косвенного байта запрета и всех данных настоящего ReverseScaledVector, без подмены вызова.
            byte(0xE507,(gate-1)&255);word(0xBFFC,0xE551);depth=max(depth,2)
            byte(0x6EAD,1)
            for index in (0,2,1):word(COMPONENTS[index],(-components[index])&65535)
            negated=(-scalar)&65535;signed=negated if negated<32768 else negated-65536;new=((signed>>1)+1)&65535
            word(0xA78F,new);wanted[6:8]=[new>>8,new&255];m1+=51
            if class_code==18:byte(0xA794,0);wanted[0:2]=[0,xor_flags(0)];m1+=3;action='reverse_class12'
            else:wanted[0:2]=[class_code,cp_flags(class_code,18)]
            wanted[SP],wanted[PC]=0xC000,0x3FFF
        else:wanted[SP],wanted[PC]=0xC000,0x3FFF
        wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(200):
            if simulator.registers[PC] in (0xDCE3,0x3FFF):break
            simulator.run()
        else:raise AssertionError('граница проверки')
        memory.recording=False;compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(hex(entry),class_code,gate,reuse,highs,action,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(memory.writes)==Counter(writes),(action,memory.writes,writes)
        assert trace.writes==ports and memory.o7ffd==(17 if ports else old)
        stack_writes=[i for b,i,_ in memory.writes if b==2 and 0x3FF8<=i<0x3FFE]
        assert (0x3FFE-min(stack_writes) if stack_writes else 0)==depth,(action,depth,stack_writes)
        touched={(b,i) for b,i,_ in writes};counts[hex(entry)+':'+action]+=1
    # Проверка каждого класса, всех байтов запрета и всех незаблокированных исходных конфигураций банка 0.
    for class_code in range(256):
        for old in (0,8,16,24):
            for gate in (0,1,255):check(class_code=class_code,old=old,gate=gate)
    for gate in range(256):
        for class_code in (0,17,18,20):
            for old in (0,8,16,24):check(gate=gate,class_code=class_code,old=old)
    # Проверка полного дополнительного входа по всем значениям ReuseByte и каждому старшему байту компонент.
    for reuse in range(256):
        for class_code in (0,17,18,20,255):
            for old in (0,8,16,24):check(entry=0xE51F,reuse=reuse,class_code=class_code,old=old)
    for high in range(256):
        for axis in range(3):
            highs=[0,0,0];highs[axis]=high
            for class_code in (0,18,17,20):
                for old in (0,8,16,24):check(entry=0xE51F,highs=tuple(highs),class_code=class_code,gate=high,old=old)
    for highs in product((0,3,4,127,128,251,252,255),repeat=3):
        for class_code in (0,18):
            for gate in (0,1,255):check(entry=0xE51F,highs=highs,class_code=class_code,gate=gate)
    # Проверка самостоятельного общего хвоста по всем классам и прежним кодам запрета.
    for class_code in range(256):
        for gate in range(256):check(entry=0xE54A,class_code=class_code,gate=gate)
    report=dict(passed=True,total_cases=sum(counts.values()),paths=dict(counts),
        method='three_entry_parent_oracle_with_real_vector_reverse_and_station_transfer',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_class_and_inhibit_bytes=True,all_reuse_bytes_and_component_high_bytes=True,
        three_distinct_entry_contracts_checked=True,auxiliary_entry_native_caller_proved=False,
        nonreturning_bank1_transfer_boundary_checked=True,station_disk_load_executed=False,
        maximum_additional_stack_bytes=4,real_out_and_eight_banks=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionCloseRecordVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
