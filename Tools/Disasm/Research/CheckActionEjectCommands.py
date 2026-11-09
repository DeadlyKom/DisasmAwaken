"""7594 и 75CF, выброс груза и мины с настоящими создателем и очередью."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckActionTextQueueCalls import Memory,Ports
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from CheckActionMissileConsume import dec_flags
from ReferenceActionClass19Spawn import Class19Machine
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*16384) for i in range(8)]
    baseline[5]=bytearray(flat[0x4000:0x8000]);baseline[2]=bytearray(flat[0x8000:0xC000])
    baseline[0]=bytearray(flat[0xC000:]);baseline[1]=bytearray(base_memory()[0xC000:])
    memory=Memory(banks=[bytearray(b) for b in baseline],out7ffd=16);simulator=Simulator(memory);ports=Ports(memory);simulator.set_tracer(ports)
    counts=Counter();paths=Counter()
    def check(entry,delay=0,index=None,amount=0,free_style=1,list_style=1,head=0,mask=0):
        memory.recording=False
        for bank,raw in zip(memory.banks,baseline):bank[:]=raw
        memory.out7ffd(16);serial=counts['cases']
        for row in range(25):
            address=0xA100+64*row;memory[address]=0;memory[address+1]=1;memory[address+24]=0
        if free_style:
            memory[0xA101]=128
            if free_style==2:memory[0xA118]=255;memory[0xA141]=128
            if free_style==3:memory[0xA101]=1;memory[0xA141]=128
        memory[0xA740]=128;memory[0xA741]=128
        for i,value in enumerate(((254,),(255,254),(1,255,254),(0,1,254),(254,255,254),(254,))[list_style]):memory[0xA01C+i]=value
        for offset,value in enumerate((0xFF,0x7F,0,0x80,0xFF,0xFF,0,71,193,5,0,0,0,0,0,0,serial&255)):memory[0xA780+offset]=value
        put(memory,0x9BD4,[0]*30)
        if index is not None:memory[0x9BD4+index]=amount
        memory[0x9C14]=amount;memory[0xA85F]=delay;put(memory,0xBFFE,[255,63])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1;memory.banks[1][0x2C81+2*i]=(i*37)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes((0,0));memory.banks[1][0x2C5D:0x2C5F]=(QUEUE+2*head).to_bytes(2,'little')
        initial=get_registers({'PC':entry,'SP':0xBFFE,'AF':0xA5EF,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=serial&255;initial[15]=serial&255;initial[26]=serial&1;initial[27]=serial%3
        model=Class19Machine(memory.banks,initial);wanted_ports=[]
        if delay:
            model.r[:2]=[delay,and_flags(delay)];counts['delay_exit']+=1
        else:
            model.put_word(0xECA9,0xEE1B);model.put(0xA85F,20);model.pair(6,0xEE1B)
            if entry==0x7594:
                found=next((i for i in range(30) if model.read(0x9BD4+i)),None)
                if found is None:
                    model.pair(6,0x9BF1);model.r[2]=0;model.r[:2]=[0,0x54];message=0xF41C;counts['empty_cargo']+=1
                else:
                    value=model.read(0x9BD4+found);model.put(0x9BD4+found,0)
                    model.r[:2]=[value,(and_flags(value)&0xC4)|0x11];model.pair(6,found);model.pair(4,0x642C)
                    model.r[2]=30-found;model.pair(8,0xA780)
                    model.call(0x6441,0x75C6,lambda:model.class19_spawn(prepared=True));message=0xF3F3;counts['cargo_byte_cleared_before_spawn']+=1
            else:
                stock=model.read(0x9C14)
                if stock==0:model.r[:2]=[0,0x54];message=0xF412;counts['empty_mines']+=1
                else:
                    model.put(0x9C14,stock-1);model.r[:2]=[1,dec_flags(stock,0)];model.pair(6,0xEE80);model.pair(8,0xA780)
                    model.call(0x6441,0x75F4,lambda:model.class19_spawn(prepared=True));message=0xF402;counts['mine_removed_before_spawn']+=1
            # Расчёт приёма единственного сообщения исходной кольцевой очередью, регистры обёртка сохраняет.
            virtual={a:model.banks[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER]=model.banks[1][0x2C5D];virtual[PRODUCER+1]=model.banks[1][0x2C5E]
            inserted=insert(virtual,message)
            for address,value in inserted['writes']:model.banks[1][address-0xC000]=value;model.writes.append((1,address-0xC000,value))
            counts['accepted_message' if inserted['accepted'] else 'dropped_message']+=1;wanted_ports=[(0x7FFD,17),(0x7FFD,16)]
        model.finish();simulator.registers[:]=initial;ports.events=[];memory.writes=[];memory.recording=True
        for _ in range(3500):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('нет возврата',entry,index,amount,free_style,list_style))
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(simulator.registers[i]==model.r[i] for i in compared),(entry,index,amount,free_style,list_style,[(i,simulator.registers[i],model.r[i]) for i in compared if simulator.registers[i]!=model.r[i]])
        assert ports.events==wanted_ports and memory.o7ffd==16
        model.banks[2][0x3FEC:0x3FFE]=memory.banks[2][0x3FEC:0x3FFE];assert memory.banks==model.banks
        outside=lambda records:[r for r in records if r[0]!=2 or not 0x3FEC<=r[1]<0x3FFE]
        assert Counter(outside(memory.writes))==Counter(outside(model.writes))
        assert all(offset>=0x3FEC for bank,offset,value in memory.writes if bank==2 and offset>=0x3FE0)
        paths.update(model.path);counts['cargo_cases' if entry==0x7594 else 'mine_cases']+=1;counts['cases']+=1
    # Проверка всех задержек, каждого положения груза и запаса мин, отказов размещения и приёма сообщения.
    for entry in (0x7594,0x75CF):
        for delay in range(256):check(entry,delay,index=0,amount=5)
    for index in range(30):
        for amount in (1,2,127,128,255):
            for free_style in range(4):
                for list_style in range(6):check(0x7594,index=index,amount=amount,free_style=free_style,list_style=list_style)
    for amount in range(256):
        for free_style in range(4):
            for list_style in range(6):check(0x75CF,amount=amount,free_style=free_style,list_style=list_style)
    for entry in (0x7594,0x75CF):
        for head in range(17):
            for mask in (0,65535,0xAAAA,0x5555):
                for index,amount in ((None,0),(0,1),(29,255)):check(entry,index=index,amount=amount,head=head,mask=mask)
    result=dict(passed=True,total_cases=counts['cases'],counts=dict(counts),paths=dict(paths),
        real_prepared_spawn_and_queue_executed=True,all_registers_except_R_and_T_checked=True,
        all_ram_and_write_multiplicity_outside_18_byte_stack_checked=True,exact_OUT_checked=True,
        removed_stock_not_restored_after_failed_spawn=True,cargo_total_counter_not_decremented=True,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionEjectCommandsVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
