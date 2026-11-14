"""State0C с полным общим хвостом до внешнего RET.

Документация: ../../../Docs/ActionClass18Proximity.md#полный-внешний-возврат
"""
from collections import Counter
from itertools import product
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceControlsPointRespawn import cp_flags,refresh
from CheckActionNearestCandidate import NearestMachine
from ReferenceActionLogRatio import LOG,EXP
from ReferenceActionHalfDeltaCodes import evaluate as geometry
from ReferenceActionRecordCodeStep import apply_codes
from CheckActionSelectedRecordStep import arguments


from CheckActionClass18Proximity import profiles
from CheckActionObjectOffsetTransfer import reference as prepare_reference
from ReferenceActionObjectOffsetVector import evaluate as vector_reference

def main():
    flat=flat_action();flat[0x9100:0x9200]=[value&255 for value in LOG]
    flat[0x9200:0x9300]=[value>>8 for value in LOG];flat[0x9300:0x9400]=EXP
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[1]=bytearray(base_memory()[0xC000:]);memory=RecordedBanks(banks=banks,out7ffd=16)
    baseline=[bytearray(bank) for bank in banks];ratio_table=bytes(flat[0x9A00:0x9B00]);root_table=bytes(banks[1][:768])
    simulator=Simulator(memory);counts=Counter();found_positions=set();cases=0;max_stack=0
    for position,differences in profiles():
        memory.recording=False
        for bank in range(8):memory.banks[bank][:]=baseline[bank]
        old=(cases%4)*8;memory.out7ffd(old);stack=0xBFFE;ix=0xA100
        # Создание активной текущей записи и отвлекающих классов, остальные слоты сохраняют исходные коды доступности.
        for index in range(25):
            address=0xA100+64*index
            if index%3==cases%3:
                memory[address],memory[address+1],memory[address+18]=index,1,index%18
        current=(0,(cases*73)&65535,(cases*109)&65535)
        for axis,value in enumerate(current):memory[ix+2*axis],memory[ix+2*axis+1]=value&255,value>>8
        memory[ix+18]=0
        if position<25:
            address=0xA100+64*position
            target=tuple((a+b)&65535 for a,b in zip(current,differences))
            if position==0:current=target
            for axis,value in enumerate(target):memory[address+2*axis],memory[address+2*axis+1]=value&255,value>>8
            memory[address+18]=18
        rate=(0,1,2,3,127,128,255)[cases%7];columns=((cases*73)&255,(cases*109)&255)
        memory[ix+8],memory[ix+9],memory[ix+37]=*columns,rate
        memory[stack],memory[stack+1]=255,63
        for offset,byte in {7:cases&255,10:12,15:(0,3,127,255)[cases&3],16:cases&255,36:cases*73&255}.items():
            memory[ix+offset]=byte
        expected=[bytearray(bank) for bank in memory.banks]
        initial=get_registers({'PC':0xF356,'SP':stack,'AF':(cases*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(cases*109)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0x5C3A},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,cases&255,cases&1,cases%3
        wanted=list(initial);wanted[4]=18;wanted[2:4]=[0,64]
        operations=[]
        def put_word(address,value):operations.extend(((address,value&255),(address+1,value>>8)))
        put_word(stack-2,0xF35B)
        # Поиск первой доступной записи класса 18 независимым обходом подготовленных данных.
        cursor=0xA100;found=False
        while True:
            put_word(stack-4,0xE997)
            while memory[cursor+1]==128 and memory[cursor]!=128:cursor+=64
            if memory[cursor+1]==128 and memory[cursor]==128:break
            if memory[cursor+18]==18:found=True;break
            cursor+=64
        wanted[10:12]=[cursor>>8,cursor&255]
        wanted[PC],wanted[SP]=0xF0F8,stack
        ports=[]
        # Расчёт R подготовки и настоящего поиска по ранее проверенным числовым договорам.
        timing=NearestMachine(memory.banks,initial);timing.r[4]=18;timing.m1(1)
        timing.call(0xE98D,0xF35B,timing.find_code);timing.m1(1)
        wanted[15]=timing.r[15]
        if not found:
            wanted[0:2]=[128,0x42];kind='no_class18'
        else:
            found_positions.add((cursor-0xA100)//64)
            target=tuple(memory[cursor+2*axis]+256*memory[cursor+2*axis+1] for axis in range(3))
            current=tuple(memory[ix+2*axis]+256*memory[ix+2*axis+1] for axis in range(3))
            deltas=tuple((a-b)&65535 for a,b in zip(target,current))
            magnitudes=tuple((-value)&65535 if value&32768 else value for value in deltas)
            high=tuple(value>>8 for value in magnitudes);distance=max(high)
            put_word(stack-2,0xF361);put_word(stack-4,magnitudes[0]);put_word(stack-6,magnitudes[1])
            wanted[4:8]=[magnitudes[0]>>8,magnitudes[0]&255,magnitudes[2]>>8,magnitudes[2]&255]
            wanted[0:2]=[distance,cp_flags(distance,2)]
            # Расчёт R вызова расстояния, сравнения и исходной условной передачи.
            timing.call(0xEAE9,0xF361,timing.distance);timing.m1(2)
            wanted[15]=timing.r[15]
            if distance<2:
                operations.extend(((ix+1,128),(ix,0),(ix+24,255)))
                wanted[PC],wanted[SP]=0x3FFF,stack+2;kind='near_reuse'
                wanted[15]=refresh(wanted[15],7)
            else:
                put_word(stack-2,0xF368)
                child=arguments(wanted,current,target);child[SP]-=4;child[PC]=0xAD5A
                # Два M1 принадлежат CALL обёртки и CALL геометрии внутри StepRecordTargetCodes.
                child[15]=refresh(child[15],2)
                put_word(stack-4,0x6268)
                calculated=geometry(child,ratio_table,root_table,return_address=0x6268)
                local=apply_codes(calculated['registers'],*columns,rate,return_address=0xF368)
                operations.extend(calculated['writes']);operations.extend(local['writes'])
                wanted=local['registers'];wanted[PC]=0xF0F8;ports=calculated['ports'];kind='far_step'
                wanted[15]=refresh(wanted[15],1)
        total_m1=timing.m1_count+(7 if kind=='near_reuse' else 30+calculated['refresh_m1']+local['refresh_m1'] if kind=='far_step' else 0)
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
        else:raise AssertionError(('не достигнут выход',position,differences))
        assert measured_m1==total_m1,(cases,kind,'M1',measured_m1,total_m1)
        memory.recording=False
        assert all(wanted[index]==simulator.registers[index] for index in (*range(25),26,27)),(cases,kind,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert memory.banks==expected and Counter(memory.writes)==Counter(writes),(cases,kind,'RAM')
        assert trace.writes==ports and memory.o7ffd==(16 if ports else old)
        max_stack=max(max_stack,max((stack-address for address,_ in operations if stack-64<=address<stack),default=0))
        counts[kind]+=1;cases+=1
    assert cases==958 and all(counts[k] for k in ('no_class18','near_reuse','far_step'))
    result=dict(passed=True,total_cases=cases,outcomes=dict(counts),found_record_positions=sorted(found_positions),
        actual_class_search_distance_geometry_and_reuse_executed=True,independent_existing_child_models_composed=True,
        exact_registers_including_r=True,full_eight_bank_ram_and_write_multiplicity_compared=True,
        real_ports_verified=True,maximum_extra_stack_bytes=max_stack,common_offset_tail_executed=True,full_external_return=True,correlated_scale_phase_profiles=True,
        full_M1_count_compared_not_only_R_modulo_128=True,
        common_tail_boundary=0x3FFF,near_path_external_ret_executed=True,
        all_input_records_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionClass18ProximityCompositionVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
