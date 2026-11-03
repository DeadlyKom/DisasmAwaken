"""60AE, ветвь состояния 80, настоящее сообщение F248 банка 1 и полная физическая RAM."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from CheckActionMissileLaunch import queue_cost


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in banks],out7ffd=0x10)
    simulator=Simulator(memory);counts=Counter();touched=set();previous_target=None
    text=[];address=0xF248
    while banks[1][address-0xC000]!=10:text.append(banks[1][address-0xC000]);address+=1
    assert bytes(text).decode('cp866').rstrip('\r')=='Цель потеряна.'
    def check(target,head,mask,flags,old):
        nonlocal touched,previous_target
        serial=counts.total();memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=banks[bank][index]
        if previous_target is not None:memory[previous_target]=flat[previous_target]
        memory.out7ffd(old);target_state=0xA101+64*target;memory[target_state]=128;previous_target=target_state
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=0x80 if mask&(1<<i) else 1
            memory.banks[1][0x2C81+2*i]=(serial+i*73)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes([0,0]);cursor=QUEUE+2*head
        memory.banks[1][0x2C5D:0x2C5F]=bytes([cursor&255,cursor>>8]);put(memory,0xBFFE,[255,63])
        initial=get_registers({'AF':0xA500|flags,'HL':0x1357,'DE':0x2468,'BC':0x3600|target,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x60AE},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=[bytearray(bank) for bank in memory.banks];writes=[]
        def emit(bank,index,value):writes.append((bank,index,value));expected[bank][index]=value
        def common(address,value):emit(5 if address<0x8000 else 2 if address<0xC000 else 0,address&0x3FFF,value)
        def word(address,value):common(address,value&255);common(address+1,value>>8)
        word(0xBFFC,0x60B2)
        # Обновление именно банка 0 по ECA9, адрес совпадает с другим контекстом Controls банка 1.
        word(0xECA9,0xEDA8)
        stack=0xBFFE
        def push(value):
            nonlocal stack
            word(stack-2,value);stack-=2
        bc=0x3600|target
        # Создание эталона всех рамок настоящей банковой обёртки и сохранённого родителем DE.
        push(0x2468);push(0x60C5);push(0x8042);push(bc);push(0xEDA8);push(0x6048);push(bc);stack+=4
        push(0x604B);push(0xEDA8);push(bc);push(0x1142);stack+=8
        virtual={a:expected[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
        virtual[PRODUCER],virtual[PRODUCER+1]=expected[1][0x2C5D],expected[1][0x2C5E]
        result=insert(virtual,0xF248)
        for a,v in result['writes']:emit(1,a-0xC000,v)
        push(0x6050);push(bc)
        wanted[0:2]=[128,0x90];wanted[6:8]=[0xED,0xA8]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],50+queue_cost(virtual,result))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(450):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',target,head,mask))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(target,head,mask,flags,old,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10)] and memory.o7ffd==0x10
        assert all(a==b for a,b in zip(memory.banks,expected)) and Counter(memory.writes)==Counter(writes)
        assert min(i for b,i,_ in memory.writes if b==2 and i>=0x3FD0)==0x3FEC
        touched={(bank,index) for bank,index,_ in writes};counts['accepted' if result['accepted'] else 'dropped']+=1
    # Проверка каждого кода цели, четырёх незаблокированных конфигураций банка 0 и четырёх входных флагов.
    for target in range(256):
        for old in (0,8,16,24):
            for flags in (0,1,128,255):
                for head in (0,15,16):
                    for mask in (0,0x7FFF,0xFFFF):check(target,head,mask,flags,old)
    report=dict(passed=True,total_cases=counts.total(),queue_results=dict(counts),
        method='lost_target_parent_oracle_with_real_banked_queue_and_index_child',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_target_index_bytes=True,all_unlocked_bank0_configurations=True,queue_drop_and_end_marker_checked=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_checked=True,
        actual_bank0_eca9_write_distinguished_from_bank1=True,real_out_and_physical_eight_banks=True,
        maximum_additional_stack_bytes=18,word_text_f248_verified_from_bank1=True,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLostMissileTargetVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
