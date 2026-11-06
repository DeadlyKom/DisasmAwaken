"""704C..709A, композиция трёх запросов и общего хвоста, настоящие дочерние инструкции."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from ReferenceControlsTextQueue import QUEUE,PRODUCER,insert
from ReferenceActionPatchedVector import evaluate
from CheckActionPatchedVector import INPUTS,COEFFICIENTS,OUTPUTS
from CheckActionPatchSwap import PAIRS


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory);counts=Counter();queue_results=Counter();touched=set()
    entries=(0x704C,0x7075,0x7088)
    deltas=(-6,10,15,18,9,-6,-6,-6,6,0,0,0,0,0,0,0)
    identity=((127,0,0),(0,127,0),(0,0,127))
    def check(which=0,target=4,free=0,preferred=2,fallback=3,flags=64,lost=False,
              class_code=0,old_state=40,mode=0,head=0,mask=0,old_page=16,matrix=identity,skip=False,shared=False):
        nonlocal touched
        assert free is None or free!=target
        memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old_page)
        # Создание фиксированных исходных записей для проверки переходов, это не доказательство предела массива игры.
        for i in range(26):
            base=0xA100+64*i;put(memory,base,[(i*67+j*13)&255 for j in range(64)])
            put(memory,base,[0x23,0]);memory[base+24]=73
            if skip and i!=target and (free is None or i<free):
                put(memory,base,[0,128]);memory[base+24]=255
        put(memory,0xA740,[128,128])
        if free is not None:put(memory,0xA100+64*free,[0,128]);memory[0xA118+64*free]=0
        if target!=255:memory[0xA101+64*target]=128 if lost else 0;memory[0xA112+64*target]=class_code
        put(memory,0x9B1B,[5,6,7]);memory[0x9B1B+which]=target
        put(memory,0x9C12,[fallback,preferred]);put(memory,0x9BD2,[0,0xA9])
        memory[0x9BCD],memory[0x9B83],memory[0xA85F]=old_state,mode,37
        memory[0x612E]=77;put(memory,0xECA9,[0x34,0x12])
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        old_outputs=(0x5342,0x6453,0x7564)
        for address,value in zip(OUTPUTS,old_outputs):put(memory,address,[value&255,value>>8])
        for i in range(16):
            memory.banks[1][0x2C80+2*i]=128 if mask&(1<<i) else 1
            memory.banks[1][0x2C81+2*i]=(i*73)&255
        memory.banks[1][0x2CA0:0x2CA2]=bytes([0,0]);cursor=QUEUE+2*head
        memory.banks[1][0x2C5D:0x2C5F]=bytes([cursor&255,cursor>>8]);put(memory,0xBFFE,[255,63])
        entry=0x705D if shared else entries[which]
        initial=get_registers({'AF':0xA500|flags,'HL':0x1357,'DE':0x2468,'BC':0x3600|(target if shared else 0x9C),
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=counts.total()&255,counts.total()&255,counts.total()&1,counts.total()%3
        wanted=list(initial);expected=[bytearray(b) for b in memory.banks];writes=[];ports=[]
        def byte(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            writes.append((bank,address&0x3FFF,value));expected[bank][address&0x3FFF]=value
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        def pair(position,value):wanted[position:position+2]=[value>>8,value&255]
        def queue(value):
            virtual={a:expected[1][a-0xC000] for a in range(QUEUE,QUEUE+34)}
            virtual[PRODUCER],virtual[PRODUCER+1]=expected[1][0x2C5D],expected[1][0x2C5E]
            result=insert(virtual,value)
            for address,value in result['writes']:
                writes.append((1,address-0xC000,value));expected[1][address-0xC000]=value
            ports.extend([(0x7FFD,17),(0x7FFD,16)]);queue_results['accepted' if result['accepted'] else 'dropped']+=1
        # Проверка допуска клавиатурного вызова по входному Z, прямой общий вход этого условия не содержит.
        if not shared and not flags&64:path='mode_blocked';depth=0
        elif not shared and target==255:
            queue(0xF2C5);wanted[0:2]=[0,0x50|(flags&1)];path='missing_capture';depth=20
        elif not shared and not (preferred or fallback):
            byte(0xA85F,5)
            for address in range(0x9B1B,0x9B1E):byte(address,255)
            queue(0xF280);pair(6,0x9C12);wanted[0:2]=[0,0x44];path='empty_stock';depth=20
        else:
            if not shared:byte(0xA85F,5);byte(0x9B1B+which,255)
            pair(2,0x3600|target);word(0xECA9,0xEDA8)
            if lost:
                word(0xECA9,0xEDA8);queue(0xF248);pair(6,0xEDA8);wanted[0:2]=[128,0x90];path='lost_target';depth=20
            else:
                # Расчёт геометрических компонентов независимым родительским эталоном с ранее проверенным вычислителем.
                for address,value in zip(INPUTS,(0,0,400)):word(address,value)
                for left,right in PAIRS:
                    a=expected[0][left-0xC000]+256*expected[0][left-0xC000+1]
                    b=expected[0][right-0xC000]+256*expected[0][right-0xC000+1];word(right,a);word(left,b)
                word(0xAD08,0xBFF4);word(0xAFF1,0xABCD)
                vector=evaluate((0,0,400),list(map(list,zip(*matrix))),old_outputs)
                assert vector['overflow'] is False
                for row in vector['performed']:word(OUTPUTS[row],vector['outputs'][row])
                for left,right in PAIRS:
                    a=expected[0][left-0xC000]+256*expected[0][left-0xC000+1]
                    b=expected[0][right-0xC000]+256*expected[0][right-0xC000+1];word(right,a);word(left,b)
                for position,value in zip((22,20,18),vector['outputs']):pair(position,value)
                byte(0x612E,50 if preferred else 10)
                # Поиск с теми же правилами пропуска, но без вызова машинного итератора в эталоне.
                found=None
                for i in range(26):
                    base=0xA100+64*i;data=expected[2];index=base&0x3FFF
                    if data[index+1]!=128:continue
                    if data[index]==128:break
                    tag=data[index+24];byte(base+24,0)
                    if tag==255:continue
                    found=i;break
                assert found==free
                if free is None:
                    pair(6,0x9C13 if preferred else 0x9C12);pair(4,64);pair(2,0x1A00|target)
                    pair(10,0xA740);wanted[0:2]=[128,0x42];wanted[16:18]=[1,vector['af'][1]];path='no_slot';depth=12
                else:
                    base=0xA100+64*free;target_base=0xA100+64*target
                    for offset,value in zip((0,2,4),vector['outputs']):word(base+offset,value)
                    for offset,value in ((6,144),(7,0),(8,0),(9,0),(10,8),(11,0),(12,0),(13,26),
                        (15,target),(17,1),(18,17),(19,50 if preferred else 10),(37,2)):byte(base+offset,value)
                    byte(target_base+12,expected[2][(target_base+12)&0x3FFF]|2);byte(target_base+11,free)
                    pair(10,base);wanted[16:18]=[17,0x44]
                    # Расчёт поправки именно по ClassCode исходной цели, DE возвращён равным target+0B.
                    if class_code<16:
                        delta=deltas[class_code]+(10 if mode and deltas[class_code]>=0 else 0)
                        signed=old_state if old_state<128 else old_state-256
                        new=max(0,min(127,signed+delta))|(32 if old_state<32 else 0)
                        byte(0x9BCD,new);pair(2,(old_state<<8)|new)
                    else:pair(2,(class_code<<8)|target)
                    # Списание запаса начинается только после успешного создания, счётчик 9BD2 меняется отдельно.
                    selected=0x9C13 if preferred else 0x9C12
                    if preferred:preferred=(preferred-1)&255
                    else:fallback=(fallback-1)&255
                    byte(selected,preferred if selected==0x9C13 else fallback);byte(0x9BD2,255)
                    new_count=preferred if preferred else fallback
                    for value in (0xF2E9,0xF26D,0x0200|new_count,0xF277):queue(value)
                    pair(6,0x9C13 if preferred else 0x9C12);pair(4,0x0200|new_count)
                    wanted[0:2]=[16,and_flags(preferred)];path='created';depth=18
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(6500):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',which,path,target,free))
        memory.recording=False
        # Проверка всех договорных регистров, R и T не входят в эту родительскую модель стоимости.
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(path,which,target,free,class_code,old_state,mode,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        def stack_write(item):return item[0]==2 and 0x3FEA<=item[1]<0x3FFE
        actual_data=[w for w in memory.writes if not stack_write(w)]
        assert Counter(actual_data)==Counter(writes),(path,Counter(actual_data)-Counter(writes),Counter(writes)-Counter(actual_data))
        stack_writes=[w for w in memory.writes if stack_write(w)]
        assert (0x3FFE-min(w[1] for w in stack_writes) if stack_writes else 0)==depth,(path,depth,stack_writes)
        # Проверка всей физической RAM вне временной рамки CPU-стека, содержимое рамки здесь отдельно не оракулится.
        expected[2][0x3FEA:0x3FFE]=memory.banks[2][0x3FEA:0x3FFE]
        assert all(a==b for a,b in zip(expected,memory.banks)),path
        assert trace.writes==ports and memory.o7ffd==(16 if ports else old_page),(path,trace.writes,ports)
        touched={(bank,index) for bank,index,_ in memory.writes};counts[path]+=1
    # Проверка всех входных флагов у каждого обработчика, включая оба вида предварительного отказа и поздние отказы.
    for which in range(3):
        for flags in range(256):
            for options in ({},{'target':255},{'preferred':0,'fallback':0},{'lost':True},{'free':None}):check(which=which,flags=flags,**options)
    # Проверка всех различных пар начальных слотов цели и ракеты и обоих полей боезапаса.
    for which in range(3):
        for target in range(25):
            for free in range(25):
                if target!=free:
                    for preferred,fallback in ((1,0),(1,9),(0,1),(255,255)):
                        check(which=which,target=target,free=free,preferred=preferred,fallback=fallback,skip=(free%2==1))
    # Проверка всех кодов класса и всех прежних байтов состояния по отдельным сечениям, без утверждения полного декартова перебора.
    for class_code in range(256):
        for old_state in (0,31,32,127,128,255):
            for mode in (0,255):check(which=class_code%3,class_code=class_code,old_state=old_state,mode=mode)
    for old_state in range(256):
        for class_code in (0,1,2,3,4,8):check(old_state=old_state,class_code=class_code,mode=old_state&1)
    # Проверка переполненной очереди, её маркера и изменения конфигурации банка, а также прямого общего входа без запаса.
    for which in range(3):
        for head in (0,15,16):
            for mask in (0,32767,65535):
                for old_page in (0,8,16,24):
                    for options in ({},{'target':255},{'lost':True},{'preferred':0,'fallback':0}):
                        check(which=which,head=head,mask=mask,old_page=old_page,**options)
    for preferred,fallback in ((0,0),(0,1),(1,0),(1,9)):
        for free,lost in ((0,False),(None,False),(0,True)):
            for flags in (0,64,255):check(shared=True,preferred=preferred,fallback=fallback,free=free,lost=lost,flags=flags)
    for coefficient in range(256):
        check(matrix=((127,0,0),(0,127,0),(coefficient,128,255)))
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),queue_results=dict(queue_results),
        method='functional_parent_oracle_with_real_children_and_banked_queue',independent_complete_child_oracle=False,
        children_executed_without_stubs=True,all_input_flags_for_three_entries=True,all_initial_distinct_slot_pairs=True,
        class_code_of_target_proved=True,capture_cleared_before_creation=True,stock_only_consumed_after_creation=True,
        direct_shared_entry_zero_stock_underflow_preserved=True,physical_eight_banks_and_out_checked=True,
        exact_contract_registers_and_flags=True,non_stack_memory_and_write_multiplicity_checked=True,
        temporary_stack_contents_independently_checked=False,refresh_and_timing_checked=False,maximum_additional_stack_bytes=20,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionMissileRequestsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
