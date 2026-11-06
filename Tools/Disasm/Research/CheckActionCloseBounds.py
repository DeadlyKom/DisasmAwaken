"""E1D1..E212, цепочка Carry трёх компонент и настоящий DispatchCloseRecord, без исполнения продолжений."""
from collections import Counter
from itertools import product
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from CheckControlsEvenSpan import and_flags
from CheckActionTypeDelta import cp_flags
from ReferenceControlsPointRespawn import refresh
RESPONSE=(0xE5B3,0xE5D2,0xE5ED)


def arithmetic(left,right,carry,negative):
    total=left+right+carry if negative else left-right-carry;value=total&65535
    overflow=((~(left^right) if negative else left^right)&(left^value)&32768)!=0
    flag=((value>>8)&0xA8)|(64 if value==0 else 0)|(16 if (left^right^value)&4096 else 0)|(4 if overflow else 0)
    flag|=(0 if negative else 2)|(int(total>65535) if negative else int(total<0))
    return value,flag


def main():
    flat=flat_action();baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    baseline[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory);counts=Counter();touched=set();maximum_depth=0
    def check(components=(0,0,0),bound=40,class_code=0,gate=0,old=16):
        nonlocal touched,maximum_depth
        memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=baseline[bank][index]
        memory.out7ffd(old);serial=sum(counts.values());record=0xA100+64*(serial%25)
        memory[record+18]=class_code;memory[0xE507]=gate;memory[0xA794]=0x77;memory[0x6EAD]=0x5A
        scalar=(serial*109)&65535;response=(0x1357,0xACE0,(serial*257)&65535)
        for address,value in zip((0xAF48,0xAF56,0xAF69),components):put(memory,address,[value&255,value>>8])
        for address,value in zip((*RESPONSE,0xA78F),(*response,scalar)):put(memory,address,[value&255,value>>8])
        bc=(serial*31)&65535
        initial=get_registers({'AF':(serial*73)&65535,'HL':bound,'DE':0x2468,'BC':bc,
            '^AF':(serial*17)&65535,'^HL':record,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE1D1},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=[bytearray(b) for b in memory.banks];writes=[];ports=[]
        def byte(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            index=address&0x3FFF;expected[bank][index]=value;writes.append((bank,index,value))
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        def pair(position,value):wanted[position:position+2]=[value>>8,value&255]
        # Сохранение BC и исходной границы, первая компонента использует unsigned-половину и её младший бит как Carry.
        word(0xBFFC,bc);word(0xBFFA,bound);carry=bound&1;m1=0;called=False;transferred=False
        for sequence,index in enumerate((0,2,1)):
            if sequence:word(0xBFFA,bound)
            left=bound>>1 if sequence==0 else bound;right=components[index];negative=bool(right&32768)
            value,flag=arithmetic(left,right,carry,negative);carry=flag&1
            pair(6,value);pair(4,right);wanted[1]=flag
            m1+=(14 if sequence==0 else 10)+int(negative)
            if value&32768:path='component_'+str(index)+'_rejected';break
            if sequence==2:called=True
        if called:
            # Создание эталона настоящего CALL P, три корневых вида возврата и передача не смешиваются.
            word(0xBFF8,0xE211)
            if gate:wanted[0:2]=[gate,and_flags(gate)];m1+=3;path='dispatch_blocked'
            else:
                word(0xBFF6,record);pair(8,record)
                if class_code in (17,20):wanted[0:2]=[class_code,0x42];m1+=12 if class_code==17 else 14;path='ignored_class'
                elif class_code==18:
                    word(0xBFF6,0x6CEC);word(0xBFF4,bc);pair(4,0);wanted[0:2]=[17,0x42]
                    wanted[SP],wanted[PC]=0xBFF8,0xDCE3;ports=[(0x7FFD,17)];m1+=27;transferred=True;path='station_transfer'
                else:
                    # Обновление состояния по ранее проверенному договору общего хвоста, реальные дочерние инструкции исполняются ниже.
                    byte(0xE507,255);word(0xBFF6,0xE551);byte(0x6EAD,1)
                    for index in (0,2,1):word(RESPONSE[index],(-response[index])&65535)
                    negated=(-scalar)&65535;signed=negated if negated<32768 else negated-65536;new=((signed>>1)+1)&65535
                    word(0xA78F,new);pair(6,new);wanted[0:2]=[class_code,cp_flags(class_code,18)];m1+=67;path='reverse_response'
        if not transferred:
            pair(4,bound);pair(2,bc);wanted[PC]=0xE213;m1+=2
        wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(220):
            if simulator.registers[PC] in (0xE213,0xDCE3):break
            simulator.run()
        else:raise AssertionError('граница проверки')
        memory.recording=False;compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(components,bound,class_code,gate,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(memory.writes)==Counter(writes),(path,memory.writes,writes)
        assert trace.writes==ports and memory.o7ffd==(17 if ports else old)
        stack_indices=[index for bank,index,_ in memory.writes if bank==2 and 0x3FF4<=index<0x3FFE]
        depth=0x3FFE-min(stack_indices);maximum_depth=max(maximum_depth,depth)
        assert depth==(10 if transferred else 8 if called and not gate else 6 if called else 4),(path,depth)
        touched={(b,i) for b,i,_ in writes};counts[path]+=1
    # Проверка каждого слова всех четырёх числовых аргументов по отдельным сечениям.
    for value in range(65536):
        check(bound=value)
        for index in range(3):
            components=[0,0,0];components[index]=value;check(tuple(components))
    # Проверка всех классов диспетчера и вариантов запрета при заведомом допуске трёх координат.
    for class_code in range(256):
        for gate in (0,1,255):
            for old in (0,8,16,24):check(class_code=class_code,gate=gate,old=old)
    for gate in range(256):
        for class_code in (0,17,18,20):check(gate=gate,class_code=class_code)
    # Проверка совместных крайних слов и Carry нечётной границы, без замены проверками независимых модулей.
    for components in product((0,1,32767,32768,65535),repeat=3):
        for bound in (0,1,2,3,40,8160,32767,32768,65535):check(components,bound)
    assert set(counts)=={'component_0_rejected','component_2_rejected','component_1_rejected','dispatch_blocked','ignored_class','station_transfer','reverse_response'}
    report=dict(passed=True,total_cases=sum(counts.values()),paths=dict(counts),
        method='word_carry_chain_parent_oracle_with_real_close_record_dispatch',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_word_arguments_by_separate_slices=True,carry_propagated_between_axes=True,
        first_component_uses_unsigned_half_bound=True,maximum_additional_stack_bytes=maximum_depth,
        station_transfer_retains_six_parent_stack_bytes=True,unknown_a794_not_written_by_root_path=True,
        execution_boundary='E1D1..E213 or bank1 DCE3, no continuation executed',
        all_joint_inputs_exhausted=False,whole_projection_scan_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionCloseBoundsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
