"""Проверка 70A4 и хвоста 709B, настоящая очередь банка 1 и точный отказ без места."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert


def queue_cost(virtual,result):
    m1=9
    for address in result['probes']:
        kind=virtual[address]
        m1+=3 if kind==1 else 7 if kind==0 else 8
    if result['accepted']:m1+=6
    elif virtual[result['probes'][-1]]==0:m1+=1
    return m1


def main():
    def read(name):return json.loads((ROOT/('Tools/Disasm/Reports/'+name+'.json')).read_text('utf-8'))
    assert read('ActionMissileStockVerification')['passed'] and read('ActionTextQueueCallsVerification')['passed']
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:])
    memory=RecordedBanks(banks=[bytearray(bank) for bank in baseline],out7ffd=0x10)
    simulator=Simulator(memory);touched=set();counts=Counter();queue_results=Counter()

    def check(target,preferred,fallback,flags=0,head=0,mask=0,old=0x10,message=False):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old)
        put(memory,0x9C12,[fallback,preferred])
        put(memory,0x9B1B,[(serial*17+i*91)&255 for i in range(3)])
        memory[0xA85F]=(serial+37)&255
        for index in range(16):
            memory.banks[1][0x2C80+2*index]=0x80 if mask&(1<<index) else 1
            memory.banks[1][0x2C81+2*index]=(index*73+serial)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes([0,0])
        cursor=QUEUE+2*head
        memory.banks[1][0x2C5D:0x2C5F]=bytes([cursor&255,cursor>>8])
        put(memory,0xBFFE,[0xFF,0x3F])
        initial=get_registers({'AF':target*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x709B if message else 0x70A4},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);writes=[];ports=[];page=old
        def emit(address,value):writes.append((5 if address<0x8000 else 2,address&0x3FFF,value))
        def report(text,return_address):
            nonlocal page
            virtual={address:memory.banks[1][address-0xC000] for address in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER],virtual[PRODUCER+1]=cursor&255,cursor>>8
            result=insert(virtual,text);queue_results['accepted' if result['accepted'] else 'dropped']+=1
            stack=0xBFFE
            def push(word):
                nonlocal stack
                emit(stack-1,word>>8);emit(stack-2,word&255);stack-=2
            af=(wanted[0]<<8)|wanted[1];bc=(wanted[2]<<8)|wanted[3];hl=(wanted[6]<<8)|wanted[7]
            push((wanted[4]<<8)|wanted[5]);push(return_address)
            push(af);push(bc);push(hl)
            push(0x6048);push(bc);stack+=4
            push(0x604B);push(hl);push(bc);push(0x1100|wanted[1]);stack+=8
            writes.extend((1,address-0xC000,value) for address,value in result['writes'])
            push(0x6050);push(bc)
            ports.extend([(0x7FFD,0x11),(0x7FFD,0x10)]);page=0x10
            return 24+queue_cost(virtual,result)
        if message:
            m1=5+report(0xF2C5,0x70A2);path='message_only'
        elif target==255:
            wanted[0:2]=[0,0x50|(flags&1)]
            m1=7+report(0xF2C5,0x70A2);path='no_target'
        else:
            emit(0xA85F,5);emit(0xBFFD,0x70);emit(0xBFFC,0xAF)
            selected=preferred if preferred else fallback
            wanted[6:8]=[0x9C,0x13 if preferred else 0x12]
            wanted[0:2]=[selected,and_flags(selected)]
            m1=7+(4 if preferred else 7)
            if selected:
                path='ready'
            else:
                wanted[0]=255
                writes.extend((2,address-0x8000,255) for address in (0x9B1D,0x9B1C,0x9B1B))
                m1+=10+report(0xF280,0x70C3)
                wanted[0:2]=[0,0x44];path='empty_stock'
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        expected=[bytearray(bank) for bank in memory.banks]
        for bank,index,value in writes:expected[bank][index]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
        memory.writes=[];memory.recording=True
        for _ in range(290):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',target,preferred,fallback,head,mask,message))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(path,target,preferred,fallback,head,mask,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert trace.writes==ports and memory.o7ffd==page
        assert all(a==b for a,b in zip(memory.banks,expected)) and Counter(memory.writes)==Counter(writes),('RAM',path)
        touched={(bank,index) for bank,index,_ in writes}
        stack=[index for bank,index,_ in memory.writes if bank==2 and index>=0x3FD0]
        assert min(stack)==(0x3FEC if ports else 0x3FFC)
        counts[path]+=1

    # Проверка всех сочетаний двух запасов при существующем коде цели.
    for preferred in range(256):
        for fallback in range(256):check(0,preferred,fallback)
    # Проверка всех входных кодов цели с пустым и двумя непустыми запасами.
    for target in range(256):
        for preferred,fallback in ((0,0),(0,100),(100,0)):check(target,preferred,fallback,flags=target)
    # Проверка всех флагов при обоих отказах, на начале, конце кольца и предельном поиске через маркер.
    for flags in range(256):
        for head in (0,15,16):
            for mask in (0,0x7FFF,0xFFFF):
                check(255,1,1,flags,head,mask)
                check(0,0,0,flags,head,mask)
    # Проверка всех незаблокированных страниц и обеих ошибок с успехом допуска.
    for old in range(32):
        for target,preferred,fallback in ((255,1,1),(0,0,0),(0,1,0)):
            for head in (0,15,16):
                for mask in (0,0x7FFF,0xFFFF):check(target,preferred,fallback,old,head,mask,old)
    # Проверка самостоятельного хвоста сообщения при всех A, четырёх профилях F и граничных очередях.
    for target in range(256):
        for flags in (0,1,128,255):
            for head in (0,15,16):
                for mask in (0,0x7FFF,0xFFFF):check(target,0,0,flags,head,mask,message=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_path=dict(counts),queue_results=dict(queue_results),
        method='composition_of_independently_checked_stock_and_queue_with_parent_control_reference',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_stock_pairs=True,all_target_codes=True,all_flag_bytes_for_failures=True,
        all_unlocked_initial_pages=True,queue_silent_drop_and_end_boundary_checked=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_checked=True,
        real_out_and_physical_eight_banks=True,maximum_additional_stack_bytes=18,
        stock_counters_not_decremented=True,empty_stock_clears_three_target_codes=True,
        all_joint_inputs_exhausted=False,missile_launch_itself_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileLaunchVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
