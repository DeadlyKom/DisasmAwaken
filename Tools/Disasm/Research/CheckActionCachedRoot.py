"""Все 16-битные входы прямого помощника и банковой обёртки, буквальные исходные три страницы."""
from collections import Counter
import json,math
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckScreenUpdate import PortTrace
from ReferenceActionCachedRoot import evaluate
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    base[1]=bytearray(base_memory()[0xC000:]);table=bytes(base[1][:768])
    # Проверка каждого физического байта трёх страниц по двум фактическим областям исходных данных.
    for index in range(256):
        root={9:47,169:207,225:239}.get(index,math.isqrt(index*256))
        expected_initial=(root^255) if index<233 else root
        expected_base=(-root*root)&65535 if index<233 else root*root
        assert table[index]==expected_initial and table[256+index]+256*table[512+index]==expected_base,index
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17);simulator=Simulator(memory)
    counts=Counter();mismatches=Counter();costs={};cases=0
    for entry in (0xB0E9,0xAD48):
        m1_values=[]
        for value in range(65536):
            memory.recording=False
            for page in (0,2,5):memory.banks[page][:]=base[page]
            wrapped=entry==0xAD48;old=value&31 if wrapped else 17;memory.out7ffd(old)
            stack=0x8002 if value&1 else 0xBFFE;memory[stack],memory[stack+1]=255,63
            initial=get_registers({'AF':value,'HL':value^0x1357,'DE':value,'BC':0x369C,
                '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
            initial[14],initial[15],initial[26],initial[27]=value&255,value&255,value&1,value%3
            result=evaluate(value,value^0x1357,(0x32,0x10),table)
            wanted=list(initial);wanted[0:2]=result['af'];wanted[6:8]=[result['hl']>>8,result['hl']&255]
            wanted[4:6]=[result['de']>>8,result['de']&255];wanted[16:18]=result['alternate_af']
            expected=[bytearray(b) for b in memory.banks];writes=[];ports=[]

            def put(address,byte):
                bank=5 if address<0x8000 else 2
                expected[bank][address&0x3FFF]=byte;writes.append((bank,address&0x3FFF,byte))

            def word(address,word):put(address,word&255);put(address+1,word>>8)

            if wrapped:
                word(stack-2,0x369C);word(stack-4,0xAD4E);word(stack-6,0x369C)
                word(stack-4,0xAD51);word(stack-4,0xAD57);word(stack-6,result['bc'])
                wanted[16]=16;ports=[(0x7FFD,17),(0x7FFD,16)]
            else:wanted[2:4]=[result['bc']>>8,result['bc']&255]
            m1=result['refresh_m1']+(22 if wrapped else 0)
            wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),stack+2,0x3FFF
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.writes=[];memory.recording=True;simulator.run(start=entry,stop=0x3FFF);memory.recording=False
            assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(hex(entry),value,result,
                [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)),(hex(entry),value,'RAM')
            assert Counter(memory.writes)==Counter(writes),(hex(entry),value,'writes')
            assert trace.writes==ports and memory.o7ffd==(16 if wrapped else 17)
            correct=result['af'][0]==math.isqrt(value)
            assert correct==(value<0xE900),(value,result)
            if not correct:
                assert result['af'][0]==261-math.isqrt(value&0xFF00)
                mismatches[format(entry,'04X')]+=1
            counts[format(entry,'04X')]+=1;cases+=1;m1_values.append(m1)
        costs[format(entry,'04X')]=dict(min=min(m1_values),max=max(m1_values))
    report=dict(passed=True,total_cases=cases,cases_by_entry=dict(counts),all_input_words_each_entry=True,
        all_768_table_bytes_proved=True,ordinary_root_domain=[0,0xE8FF],different_upper_domain=[0xE900,65535],
        different_results_vs_isqrt=dict(mismatches),upper_table_rows=23,original_upper_table_behavior_preserved=True,
        original_lower_seed_exceptions={9:47,169:207,225:239},
        domain_validity_in_game_callers_proved=False,exact_registers_including_R=True,observed_m1_costs=costs,
        independent_numeric_oracle=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        hardware_bus_stack_write_order_proved=False,direct_entry_CPU_stack_written=False,
        wrapper_maximum_additional_stack_bytes=6,real_paging_and_children_executed=True,
        paging_and_stack_profiles_distributed_across_words=True,full_word_paging_stack_product_exhausted=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionCachedRootVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
