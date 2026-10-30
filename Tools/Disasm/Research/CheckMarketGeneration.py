"""Полный исходный генератор тридцати пар рынка, настоящий банковый запрос ключа и генератор Seed1."""
from pathlib import Path
from itertools import product
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,SP
from CheckRowHighlight import make_context
from CheckScreenUpdate import PortTrace,put
from CheckWorldSignature import signature
from CheckRandomState import reference as random_step


def reference(categories,rules,old,second,variant,tick,mode,info):
    if not info['result'] or info['major']==4:return bytes(60),None
    word=second;high=(tick&0xFC)^variant;result=[];details=None
    for index in range(27):
        word,high,_,t_low=random_step(word,high)
        raw=word>>8;low=word&255;delta=low&7
        if low&128:delta=-delta
        bonus=8 if categories[index]==info['minor'] else 0
        interim=(rules[2*index]+delta)&255
        price=5 if interim<=bonus else interim-bonus
        rule=rules[2*index+1]
        if rule==0:mask=0x3F
        elif rule==1:mask=0xBF if not raw&0xC0 else 0x3F
        else:
            mask=0xBF
            if rule>=3 and info['major']==0:raw=(raw|128)&0xCF
        base_quantity=(raw&mask)&127
        generated=max(base_quantity+bonus-10,0)|((raw&mask)&mode)
        quantity=(old[2*index]&(mode^128))|generated
        discount=min((quantity>>1)&63,8)
        final_price=price-discount if price>discount else 5
        result.extend((quantity,final_price))
        details=(word,high,base_quantity,generated,raw,bonus,t_low)
    result.extend((0,rules[54],0,rules[56],0,rules[58]))
    return bytes(result),details


def main():
    source,_,base=make_context();base=[bytearray(bank) for bank in base]
    memory=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=0x10);simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    categories=source[0x34DC:0x34F7];rules=source[0x3518:0x3554]
    words=(0,0x4733,0x4734,0x4737,0x4738,0x473A,0x473B,0x4835,0x4937,0x493A,0x4A35,0x4A36,0x4B38,0x4D39,0x4E39,0xFFFF)
    cases=generated_cases=cleared_cases=prices_below_five=marked_rows=0
    for first,second,variant,tick,mode in product(words,(0,1,0x1357,0x2468,0x7FFF,0xFFFF),
                                                (0,1,7,255),(0,1,3,4,0xFC,0xFF),(0,128)):
        memory.banks=[bank.copy() for bank in base];memory.memory=[None,memory.banks[5],memory.banks[2],None]
        memory.out7ffd(0x10);simulator.registers[:]=initial;r=simulator.registers
        trace=PortTrace(simulator);simulator.set_tracer(trace)
        put(memory,0x7FFE,[255,63]);memory[0x6306]=0x10
        put(memory,0x983F,list(first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([variant])))
        memory[0x983D]=tick;memory[0xA9A9]=mode
        old=bytes((i*73+(second>>8)+tick)&255 for i in range(60));put(memory,0x9555,old)
        put(memory,0xA8AF,[0xCD,0xAB,0xEF]);initial_states=memory[0xA8AC:0xA8C1]
        info=signature(first,second,variant)
        expected,details=reference(categories,rules,old,second,variant,tick,mode,info)
        simulator.run(start=0xA91B,stop=0x3FFF)
        assert memory[0x9555:0x9591]==list(expected),(first,second,variant,tick,mode)
        assert memory[0x9591]==255 and memory[0xA9A9]==mode and r[SP]==0x8000
        assert memory[0x631C:0x6320]==list(info['first'].to_bytes(2,'little')+info['second'].to_bytes(2,'little'))
        assert (r[16],r[17])==(0x10,0)
        if details is None:
            expected_a=0 if not info['result'] else 4
            assert (r[A],r[F],r[H]*256+r[L],r[D]*256+r[E],r[B]*256+r[C])==(expected_a,0x40,0x9590,0x9591,0)
            assert r[8:12]==initial[8:12] and r[18:24]==initial[18:24]
            assert memory[0xA8AC:0xA8C1]==initial_states;cleared_cases+=1
        else:
            word,high,base_quantity,generated,raw,bonus,t_low=details
            expected_states=initial_states.copy();expected_states[3:6]=[word&255,word>>8,high]
            assert memory[0xA8AC:0xA8C1]==expected_states
            assert (r[A],r[F],r[H]*256+r[L],r[D],r[E],r[B],r[C])==(rules[58],0x43,0x9590,generated,raw,0,base_quantity)
            assert r[8]*256+r[9]==0x954E and r[10:12]==initial[10:12]
            assert (r[22]*256+r[23],r[20],r[21],r[18],r[19])==(0x94F7,word>>8,bonus,0,t_low)
            assert memory[0xA967]==info['minor'] and memory[0xA999]==info['major']
            prices_below_five+=sum(value<5 for value in expected[1:54:2]);marked_rows+=sum(bool(value&128) for value in expected[:54:2])
            generated_cases+=1
        assert trace.writes==[(0x7FFD,0x11),(0x7FFD,0x10)]
        for page in (0,1,3,4,6,7):assert memory.banks[page]==base[page]
        cases+=1
    report=dict(passed=True,method='original_market_generation_with_real_banked_signature_and_three_byte_random_stream',
                cases=cases,generated_cases=generated_cases,cleared_cases=cleared_cases,
                generated_rows_per_case=27,special_rows=3,prices_below_five=prices_below_five,
                marked_rows=marked_rows,actual_original_rule_tables_used=True,mode_values=[0,128],
                signature_query_stubbed=False,random_stream_stubbed=False,banks_modeled=8,
                mark_game_meaning_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MarketGenerationVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
