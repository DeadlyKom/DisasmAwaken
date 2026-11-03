"""70C6, два декремента и четыре записи очереди, реальный код без подмен детей."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from CheckActionMissileLaunch import queue_cost
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert


def dec_flags(value,carry):
    result=(value-1)&255
    return (result&0xA8)|(64 if result==0 else 0)|(16 if value&15==0 else 0)|(4 if value==128 else 0)|2|carry


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=0x10)
    simulator=Simulator(memory);touched=set();counts=Counter();queue_results=Counter()

    def check(preferred,fallback,aux=20,flags=0,head=0,mask=0,old=0x10):
        nonlocal touched
        serial=sum(counts.values());memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old);put(memory,0x9C12,[fallback,preferred]);memory[0x9BD2]=aux
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=0x80 if mask&(1<<i) else 1
            memory.banks[1][0x2C81+2*i]=(serial+i*73)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes([0,0]);cursor=QUEUE+2*head
        memory.banks[1][0x2C5D:0x2C5F]=bytes([cursor&255,cursor>>8]);put(memory,0xBFFE,[0xFF,0x3F])
        address=0x9C13 if preferred else 0x9C12
        initial=get_registers({'AF':0xA500|flags,'HL':address,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x70C6},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=[bytearray(bank) for bank in memory.banks];writes=[];ports=[]
        def emit(bank,index,value):writes.append((bank,index,value));expected[bank][index]=value
        def common(address,value):emit(5 if address<0x8000 else 2,address&0x3FFF,value)
        # Расчёт обоих исходных байтовых декрементов, включая переход 00 в FF.
        if preferred:preferred=(preferred-1)&255
        else:fallback=(fallback-1)&255
        common(address,preferred if address==0x9C13 else fallback)
        common(0x9BD2,(aux-1)&255);wanted[0:2]=[(aux-1)&255,dec_flags(aux,flags&1)]
        def queue(value,ret,number=False):
            stack=0xBFFE
            def push(word):
                nonlocal stack
                common(stack-1,word>>8);common(stack-2,word&255);stack-=2
            af=(wanted[0]<<8)|wanted[1];bc=(wanted[2]<<8)|wanted[3];hl=(wanted[6]<<8)|wanted[7]
            if not number:push((wanted[4]<<8)|wanted[5])
            push(ret)
            if not number:push(af);push(bc);push(hl)
            push(0x6006 if number else 0x6048);push(bc);stack+=4
            push(0x600A if number else 0x604B);push(hl);push(bc);push(af if number else 0x1100|wanted[1]);stack+=8
            virtual={a:expected[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER],virtual[PRODUCER+1]=expected[1][0x2C5D],expected[1][0x2C5E]
            result=insert(virtual,value)
            cost=(22 if number else 24)+queue_cost(virtual,result)
            for a,v in result['writes']:emit(1,a-0xC000,v)
            push(0x600F if number else 0x6050);push(bc)
            ports.extend([(0x7FFD,0x11),(0x7FFD,0x10)])
            queue_results['accepted' if result['accepted'] else 'dropped']+=1
            if number:
                wanted[0]=0x10;wanted[4:6]=[2,value&255];wanted[16]=0x11
            return cost
        m1=19+queue(0xF2E9,0x70D5)+queue(0xF26D,0x70DD)
        common(0xBFFD,0x70);common(0xBFFC,0xE1)
        chosen=preferred if preferred else fallback
        wanted[6:8]=[0x9C,0x13 if preferred else 0x12]
        wanted[0:2]=[chosen,and_flags(preferred)]
        m1+=4 if preferred else 7
        m1+=queue(0x0200|chosen,0x70E4,True)+queue(0xF277,0x70EB)
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],m1)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(1100):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',preferred,fallback,head,mask))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(preferred,fallback,aux,head,mask,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert trace.writes==ports and memory.o7ffd==0x10
        assert all(a==b for a,b in zip(memory.banks,expected)) and Counter(memory.writes)==Counter(writes)
        touched={(bank,index) for bank,index,_ in writes}
        assert min(i for b,i,_ in memory.writes if b==2 and i>=0x3FD0)==0x3FEC
        counts['calls']+=1
    # Проверка каждого исходного сочетания запасов, включая переключение поля при исчерпании Preferred.
    for preferred in range(256):
        for fallback in range(256):check(preferred,fallback)
    print('Stock pair sweep complete',flush=True)
    # Проверка каждого значения отдельного байта 9BD2 и всех флагов при значимых переходах выбора.
    for aux in range(256):
        for flags in (0,1,128,255):
            for pair in ((0,0),(0,1),(1,0),(1,100),(2,255)):check(*pair,aux,flags)
    # Проверка четырёх последовательных заявок, отказов, маркера и всех незаблокированных страниц.
    for old in range(32):
        for head in (0,15,16):
            for mask in (0,0x7FFF,0xFFFF,0xFFF0):check(1,100,0,old,head,mask,old)
    report=dict(passed=True,total_cases=counts['calls'],queue_results=dict(queue_results),
        method='composition_of_checked_stock_and_banked_queues_with_parent_reference',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        all_stock_pairs=True,all_auxiliary_counter_bytes=True,all_unlocked_initial_pages=True,
        sequential_four_queue_requests_checked=True,queue_silent_drop_preserved=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_checked=True,
        real_out_and_physical_eight_banks=True,maximum_additional_stack_bytes=18,
        selected_stock_and_9bd2_byte_decremented=True,byte_underflow_preserved=True,
        final_de_is_number_record=True,final_af_prime_a_is_11=True,
        auxiliary_counter_game_meaning_proved=False,rocket_object_creation_proved=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileConsumeVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
