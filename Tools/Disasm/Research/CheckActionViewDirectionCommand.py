"""762A, настоящий разворот базиса, построитель точек и две записи очереди."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from ReferenceControlsBufferPoints import random_step,coordinates
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from CheckActionReverseViewBasis import ADDRESSES


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000])
    baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports);counts=Counter()
    seeds=(0,1,255,256,32767,32768,65534,65535)
    matrices=((0,0,0,0,0,0),(1,2,3,4,5,6),(32768,)*6,(65535,)*6,
        (32767,32768,0,1,65535,30000),(0x1234,0xABCD,0x8001,0x7FFF,0xFF,0xFF00),
        (0x100,0x200,0x300,0x400,0x500,0x600),(65535,0,1,32767,32768,65534))
    def check(delay,mode,seed,matrix=matrices[0],head=0,mask=0):
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16);serial=counts['cases'];memory[0xA85F]=delay
        for i,address in enumerate((0x6E75,0x6E88,0x6E9B)):put(memory,address,[mode if i==0 else (serial+73*i)&255,(serial+109*i)&255])
        for address,value in zip(ADDRESSES,matrix):put(memory,address,value.to_bytes(2,'little'))
        memory.banks[1][0xA8F:0xA91]=seed.to_bytes(2,'little');put(memory,0xBFFE,[255,63])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1;memory.banks[1][0x2C81+2*i]=(i*37)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0));memory.banks[1][0x2C5D:0x2C5F]=(QUEUE+2*head).to_bytes(2,'little')
        expected=[bytearray(b) for b in memory.banks];changes=[];wanted_ports=[]
        initial=get_registers({'PC':0x762A,'SP':0xBFFE,'AF':0xA5EF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        wanted=list(initial);wanted[PC]=0x3FFF;wanted[SP]=0xC000
        def byte(bank,offset,value):expected[bank][offset]=value;changes.append((bank,offset,value))
        def word(bank,offset,value):byte(bank,offset,value&255);byte(bank,offset+1,value>>8)
        if delay:wanted[:2]=[delay,and_flags(delay)];counts['delay_exit']+=1
        else:
            word(0,0x2CA9,0xEE1B);byte(2,0x285F,20)
            for address,value in zip(ADDRESSES,matrix):word(2,address&0x3FFF,(-value)&65535)
            # Расчёт 70 состояний генератора и исходных ограничений координат по ранее проверенному числовому договору.
            state=seed
            for index in range(35):
                state,mixed,difference,_=random_step(state);word(1,0xA8F,state)
                raw_x=state&255;x=2 if raw_x==0 else raw_x-2 if raw_x>=254 else raw_x
                state,mixed,difference,_=random_step(state);word(1,0xA8F,state)
                raw_y=state&127;y=2 if raw_y==0 else raw_y-64 if raw_y>=95 else raw_y
                byte(1,0x500+2*index,y);byte(1,0x501+2*index,x)
            following,points,y_flags=coordinates(seed);assert state==following
            wanted[16:24]=[points[-2],y_flags&1,0,mixed&255,difference>>8,difference&255,state>>8,state&255]
            wanted[4:6]=[matrix[-1]>>8,matrix[-1]&255]
            opcode_word=0 if mode else 0x44ED
            for address in (0x6E75,0x6E88,0x6E9B):word(5,address&0x3FFF,opcode_word)
            wanted[:2]=[mode,and_flags(mode)];wanted[6:8]=[opcode_word>>8,opcode_word&255]
            wanted_ports=[(0x7FFD,17),(0x7FFD,16)]
            virtual={a:expected[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER]=expected[1][0x2C5D];virtual[PRODUCER+1]=expected[1][0x2C5E]
            for message in (0xF1E1,0xF228 if mode else 0xF239):
                inserted=insert(virtual,message);counts['accepted_message' if inserted['accepted'] else 'dropped_message']+=1
                for address,value in inserted['writes']:virtual[address]=value;byte(1,address-0xC000,value)
                wanted_ports.extend(((0x7FFD,17),(0x7FFD,16)))
            counts['front' if mode else 'rear']+=1
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;ports.events=[]
        for _ in range(6000):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',delay,mode,seed))
        memory.recording=False;compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==wanted[i] for i in compared),[(i,simulator.registers[i],wanted[i]) for i in compared if simulator.registers[i]!=wanted[i]]
        expected[2][0x3FEC:0x3FFE]=memory.banks[2][0x3FEC:0x3FFE];assert memory.banks==expected
        outside=lambda rows:[r for r in rows if r[0]!=2 or not 0x3FEC<=r[1]<0x3FFE]
        assert Counter(outside(memory.writes))==Counter(changes)
        assert all(offset>=0x3FEC for bank,offset,value in memory.writes if bank==2 and offset>=0x3FE0)
        assert ports.events==wanted_ports and memory.o7ffd==16;counts['cases']+=1
    # Проверка всех задержек и байтов выбора направления, граничных Seed, смешанных базисов и очереди.
    for delay in range(256):check(delay,0,0)
    for mode in range(256):
        for seed in seeds:check(0,mode,seed)
    for matrix in matrices:
        for seed in seeds:
            for mode in (0,237):check(0,mode,seed,matrix)
    for head in range(17):
        for mask in (0,65535,0xAAAA,0x5555):
            for mode in (0,237):check(0,mode,1,head=head,mask=mask)
    result=dict(passed=True,total_cases=counts['cases'],counts=dict(counts),real_basis_point_builder_and_queue_executed=True,
        all_registers_except_R_and_T_checked=True,all_ram_and_write_multiplicity_outside_18_byte_stack_checked=True,
        all_mode_and_delay_bytes_tested=True,three_opcode_pairs_synchronized=True,
        code_pairs_never_executed_by_this_model=True,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionViewDirectionCommandVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
