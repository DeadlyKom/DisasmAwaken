"""State0D, все пути до внешнего RET, включая общий вычислитель.

Документация: ../../../Docs/ActionSelectedRecordProximity.md#полный-внешний-возврат
"""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from CheckActionRecordIndex import decode
from ReferenceControlsPointRespawn import cp_flags,refresh
from CheckActionNearestCandidate import NearestMachine
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes
from CheckActionSelectedRecordStep import arguments
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference


def main():
    flat=flat_action();flat[0x9100:0x9200]=[value&255 for value in LOG]
    flat[0x9200:0x9300]=[value>>8 for value in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=banks,out7ffd=16)
    baseline=[bytearray(bank) for bank in banks];ratio_table=bytes(flat[0x9A00:0x9B00]);root_table=bytes(banks[1][:768])
    simulator=Simulator(memory);counts=Counter();cases=0;max_stack=0
    for index in range(256):
        for mode in range(4):
            memory.recording=False
            for bank in range(8):memory.banks[bank][:]=baseline[bank]
            old=(cases%4)*8;memory.out7ffd(old);stack=0xBFFE;ix=0xA100;selected=0xA100+64*index
            # Создание текущей записи и необязательной резервной записи класса 8.
            current=(0,0,0) if mode==2 else (0,1000,2000)
            for axis,value in enumerate(current):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
            memory[ix+18]=0
            if index%2==0:
                memory[0xA180],memory[0xA181],memory[0xA192]=0,1,8
            delta=(512,1024,0xF000) if mode==3 else (0,511,0xFE01)
            if index<25:
                target=tuple((a+b)&65535 for a,b in zip(current,delta))
                for axis,value in enumerate(target):memory[selected+2*axis],memory[selected+2*axis+1]=value&255,value>>8
                selected_class=(index*37+3)&255
                memory[selected+18],memory[selected+24]=selected_class,(cases*137)&255
                if mode==0:memory[selected+1]=128
            else:
                # Сохранение оригинальных байтов за исходным массивом, там находятся также вызываемые математические процедуры.
                selected_class=memory[selected+18]
            mismatch=mode==1 or (index>=25 and mode==0)
            memory[ix+32],memory[ix+33]=index,selected_class^(1 if mismatch else 0)
            columns=((cases*73)&255,(cases*109)&255);rate=(0,1,2,3,127,128,255)[cases%7]
            memory[ix+8],memory[ix+9],memory[ix+37]=*columns,rate
            memory[stack],memory[stack+1]=255,63
            for offset,byte in {7:cases&255,10:13,15:(0,3,127,255)[cases&3],16:cases&255,36:cases*73&255}.items():
                memory[ix+offset]=byte
            expected=[bytearray(bank) for bank in memory.banks]
            initial=get_registers({'PC':0xF04A,'SP':stack,'AF':(cases*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                '^AF':(cases*109)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
            initial[14],initial[15],initial[26],initial[27]=cases&255,cases&255,cases&1,cases%3
            wanted=list(initial);wanted[10:12]=[selected>>8,selected&255]
            operations=[]
            def put_word(address,value):operations.extend(((address,value&255),(address+1,value>>8)))
            put_word(stack-2,0xF050);put_word(stack-4,0x1357)
            put_word(stack-6,0xE6A2);put_word(stack-6,selected)
            ports=[]
            unavailable=memory[selected+1]==128
            wrong_class=memory[selected+18]!=memory[ix+33]
            # Расчёт R селектора и достигнутых проверок доступности и полного класса.
            timing=NearestMachine(memory.banks,initial);timing.r[10:12]=[selected>>8,selected&255]
            timing.m1(26+(0 if unavailable else 5));wanted[15]=timing.r[15]
            if unavailable or wrong_class:
                kind='unavailable_fallback' if unavailable else 'class_mismatch_fallback'
                wanted[4],wanted[2],wanted[3]=8,0,64
                put_word(stack-2,0xE981);cursor=0xA100;found=False
                # Независимый поиск первой активной записи класса 8, включая прежний индекс и саму текущую запись.
                while True:
                    put_word(stack-4,0xE997)
                    while memory[cursor+1]==128 and memory[cursor]!=128:cursor+=64
                    if memory[cursor+1]==128 and memory[cursor]==128:break
                    if memory[cursor+18]==8:found=True;break
                    cursor+=64
                wanted[10:12]=[cursor>>8,cursor&255]
                if found:
                    selected_index,flags,_=decode(cursor);wanted[0:2]=[selected_index,flags]
                    put_word(stack-2,0xE987);put_word(stack-4,0x1357)
                    put_word(stack-6,cursor);put_word(stack-6,0xE6C5)
                    operations.append((ix+32,selected_index))
                else:wanted[0:2]=[128,0x42]
                wanted[PC],wanted[SP]=0xF0F8,stack
                # Расчёт R резервного поиска и условного преобразования найденного адреса.
                timing.r[4]=8;timing.m1(1);timing.call(0xE98D,0xE981,timing.find_code);timing.m1(1)
                if found:
                    timing.call(0xE6BE,0xE987,timing.iy_index);timing.m1(3)
                wanted[15]=timing.r[15]
                counts['fallback_found' if found else 'fallback_absent']+=1
            else:
                current=tuple(memory[ix+2*axis]+256*memory[ix+2*axis+1] for axis in range(3))
                target=tuple(memory[selected+2*axis]+256*memory[selected+2*axis+1] for axis in range(3))
                differences=tuple((a-b)&65535 for a,b in zip(target,current))
                magnitudes=tuple((-value)&65535 if value&32768 else value for value in differences)
                distance=max(value>>8 for value in magnitudes)
                put_word(stack-2,0xF064);put_word(stack-4,magnitudes[0]);put_word(stack-6,magnitudes[1])
                wanted[4:8]=[magnitudes[0]>>8,magnitudes[0]&255,magnitudes[2]>>8,magnitudes[2]&255]
                wanted[0:2]=[distance,cp_flags(distance,2)]
                # Расчёт R вызова расстояния и сравнения с порогом близости.
                timing.call(0xEAE9,0xF064,timing.distance);timing.m1(2);wanted[15]=timing.r[15]
                if distance<2:
                    operations.extend(((selected+24,memory[selected+24]&~4),(ix+1,128),(ix,0),(ix+24,255)))
                    wanted[PC],wanted[SP]=0x3FFF,stack+2;kind='near_reuse'
                    wanted[15]=refresh(wanted[15],10)
                else:
                    put_word(stack-2,0xF072)
                    child=arguments(wanted,current,target);child[SP]=stack-4;child[PC]=0xAD5A
                    # Учёт двух настоящих CALL между родителем и входом числовой геометрии.
                    child[15]=refresh(child[15],2)
                    put_word(stack-4,0x6268)
                    calculated=geometry(child,ratio_table,root_table,return_address=0x6268)
                    local=apply_codes(calculated['registers'],*columns,rate,return_address=0xF072)
                    operations.extend(calculated['writes']);operations.extend(local['writes'])
                    wanted=local['registers'];wanted[PC]=0xF0F8;ports=calculated['ports'];kind='far_step'
                    wanted[15]=refresh(wanted[15],1)
            total_m1=timing.m1_count+(10 if kind=='near_reuse' else 30+calculated['refresh_m1']+local['refresh_m1'] if kind=='far_step' else 0)
            writes=[]
            for address,value in operations:
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
            if wanted[PC]==0xF0F8:
                view=RecordedBanks(banks=expected,out7ffd=16 if ports else old)
                record={offset:view[ix+offset] for offset in (1,7,8,9,10,15,16,18,36)}
                wanted,extra,common_path=prepare_reference(wanted,ix,record)
                total_m1+=4 if record[1]==128 else 30+int(common_path=='preserve')+4*int(record[18]<16)+2*int(record[18]<16 and record[10]!=19)
                def apply(extra):
                    for address,byte in extra:
                        bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                        expected[bank][address&0x3FFF]=byte
                        writes.append((bank,address&0x3FFF,byte));operations.append((address,byte))
                apply(extra)
                if wanted[PC]==0x6D06:
                    result=vector_reference(view,wanted,(record[7],(record[8]+128)&255,record[9]),0x3FFF)
                    wanted=result['registers'];total_m1+=result['refresh_m1'];apply(result['writes'])
                counts['common/'+common_path]+=1
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.writes=[];memory.recording=True
            measured_m1=0
            for _ in range(20000):
                if simulator.registers[PC]==0x3FFF:break
                previous_r=simulator.registers[15]
                simulator.run()
                increment=(simulator.registers[15]-previous_r)&127
                assert increment in (1,2)
                measured_m1+=increment
            else:raise AssertionError(('не достигнут выход',index,mode))
            assert measured_m1==total_m1,(index,mode,'M1',measured_m1,total_m1)
            memory.recording=False
            compared=(*range(25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(index,mode,kind,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(index,mode,kind,'RAM')
            assert trace.writes==ports and memory.o7ffd==(16 if ports else old)
            max_stack=max(max_stack,max((stack-address for address,_ in operations if stack-64<=address<stack),default=0))
            counts[kind]+=1;cases+=1
    assert cases==1024
    outcomes={name:counts[name] for name in ('unavailable_fallback','class_mismatch_fallback','near_reuse','far_step')}
    assert sum(outcomes.values())==cases
    result=dict(passed=True,total_cases=cases,outcomes=outcomes,
        fallback_outcomes={name:counts[name] for name in ('fallback_found','fallback_absent')},all_256_selected_indices=True,
        no_25_slot_index_clamp_introduced=True,self_selection_alias_preserved=True,
        out_of_initial_array_target_bytes_preserved=True,
        actual_selector_search_distance_geometry_and_reuse_executed=True,
        exact_registers_including_r=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_extra_stack_bytes=max_stack,real_ports_verified=True,common_offset_tail_executed=True,full_external_return=True,correlated_phase_scale_profiles=True,
        common_paths={k:v for k,v in counts.items() if k.startswith("common/")},
        full_M1_count_compared_not_only_R_modulo_128=True,
        near_path_external_ret_executed=True,all_record_contents_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSelectedRecordProximityCompositionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
