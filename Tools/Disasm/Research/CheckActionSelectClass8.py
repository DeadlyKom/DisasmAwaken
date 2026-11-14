"""E97C..E98C, поиск полного кода 08 и сохранение индекса, точные флаги, R и стек."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionRecordDistance import Recorded
from CheckActionRecordIndex import decode
from ReferenceControlsPointRespawn import refresh


def main():
    memory=Recorded(flat_action());simulator=Simulator(memory);cases=0;counts=Counter();positions=set()
    for position in range(26):
        for code in range(256):
            memory.recording=False
            # Создание исходного списка с текущей активной записью и одной проверяемой записью произвольного класса.
            for index in range(25):
                address=0xA100+64*index
                memory[address],memory[address+1],memory[address+18]=0,128,0
            memory[0xA100],memory[0xA101],memory[0xA112]=0,1,7
            if position<25:
                address=0xA100+64*position
                memory[address],memory[address+1],memory[address+18]=position,1,code
            memory[0xA740],memory[0xA741]=128,128
            stack=0xBFFE;memory[stack:stack+2]=[255,63]
            memory[0xA120]=(cases*137)&255
            # Подготовка различимого требуемого класса, резервный поиск не должен его заменять.
            prior_class=(cases*73+85)&255;memory[0xA121]=prior_class
            initial=get_registers({'PC':0xE97C,'SP':stack,'AF':(cases*73)&65535,
                'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xA100,'IY':0x5C3A,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC},None,False)
            initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*17)&255,cases&1,cases%3
            wanted=list(initial);wanted[4]=8;wanted[2:4]=[0,64]
            operations=[]
            def put_word(address,value):operations.extend(((address,value&255),(address+1,value>>8)))
            put_word(stack-2,0xE981)
            # Поиск совпадения независимой фильтрацией данных, стоимость итератора учитывает реальные пропущенные слоты.
            cursor=0xA100;found=False;m1=3
            while True:
                put_word(stack-4,0xE997);m1+=2
                while True:
                    m1+=6
                    if memory[cursor+1]!=128:break
                    m1+=4
                    if memory[cursor]==128:m1+=1;break
                    cursor+=64
                if memory[cursor+1]==128 and memory[cursor]==128:break
                m1+=4
                if memory[cursor+18]==8:m1+=2;found=True;break
                cursor+=64
            wanted[10:12]=[cursor>>8,cursor&255]
            if found:
                index,flags,_=decode(cursor);wanted[0:2]=[index,flags]
                put_word(stack-2,0xE987);put_word(stack-4,0x1357)
                put_word(stack-6,cursor);put_word(stack-6,0xE6C5)
                operations.append((0xA120,index));positions.add(index);m1+=23
            else:wanted[0:2]=[128,0x42];m1+=3
            wanted[15]=refresh(initial[15],m1);wanted[PC],wanted[SP]=0xF0F8,stack
            memory.writes=[];memory.recording=True;simulator.registers[:]=initial;measured_m1=0
            for _ in range(5000):
                if simulator.registers[PC]==0xF0F8:break
                before_r=simulator.registers[15];simulator.run()
                increment=(simulator.registers[15]-before_r)&127
                assert increment in (1,2)
                measured_m1+=increment
            else:raise AssertionError(('не достигнут общий хвост',position,code))
            memory.recording=False
            # Проверка одинакового Z обоих выходов и различимых PV/N успешного выровненного индекса.
            assert simulator.registers[1]&64
            assert bool(simulator.registers[1]&4)==found and bool(simulator.registers[1]&2)!=found
            assert memory[0xA121]==prior_class
            assert measured_m1==m1,(position,code,measured_m1,m1)
            assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(position,code,[(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
            assert Counter(memory.writes)==Counter(operations)
            last=dict(operations);assert all(memory[address]==value for address,value in last.items())
            assert memory[stack:stack+2]==[255,63]
            counts['found' if found else 'not_found']+=1;cases+=1
    assert cases==6656 and positions==set(range(25))
    result=dict(passed=True,total_cases=cases,outcomes=dict(counts),all_256_candidate_codes_and_26_positions=True,
        found_indices=sorted(positions),exact_registers_flags_r_sp=True,all_ram_writes_and_values_compared=True,
        cpu_stack_bytes=6,original_return_word_unchanged=True,common_offset_tail_executed=False,
        Z_set_on_both_outcomes=True,PV_set_and_N_clear_on_found_aligned_record=True,
        ProximityClass_preserved=True,full_M1_count_compared_not_only_R_modulo_128=True,
        boundary=0xF0F8,all_possible_lists_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSelectClass8Verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in result.items() if key!='found_indices'},indent=2))


if __name__=='__main__':main()
