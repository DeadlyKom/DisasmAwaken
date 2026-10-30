"""Геометрические коды областей, четырёхбайтовый шаг и банковая характеристика исходного пятибайтового ключа."""
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
from CheckGlyphRenderer import compare_flags


def logical_flags(value):return (value&0xA8)|(0x40 if value==0 else 0)|(4 if not value.bit_count()%2 else 0)


def step_key(first,second):
    total=first+0x101;adjusted=total&65535
    total=adjusted+second;intermediate=total&65535;carry=total>>16
    mix=((second&255)+(intermediate&255)+carry)&255
    combined=(intermediate+((first&255)<<8)+mix)&65535
    low=((combined&255)^mix^0x75)&255
    high=((combined>>8)^(first&255)^0xA7)&255
    new_second=high*256+low
    checksum=(second>>8)^(second&255)^high^low
    return second,new_second,checksum


def classify_region(word):
    high,low=word>>8,word&255
    if 0x4A<=high<0x4E and 0x36<=low<0x3A:return 0
    if 0x47<=high<0x4A and 0x34<=low<0x38:return 1
    if 0x47<=high<0x4A and 0x38<=low<0x3B:return 2
    return 3


def region_flags(word):
    high,low=word>>8,word&255;region=classify_region(word)
    if region==0:return compare_flags(low,0x3A)
    if region==1:return compare_flags(low,0x38)
    if region==2:return compare_flags(low,0x3B)
    if high<0x47:return compare_flags(high,0x47)
    if high>=0x4A:return compare_flags(high,0x4A)
    return compare_flags(low,0x38 if low<0x38 else 0x3B)


def signature(first,second,variant):
    fingerprint=((first>>8)^(first&255)^(second>>8)^(second&255))&7
    result=max(fingerprint-1,0)
    flags=0x44 if fingerprint==0 else (0x42 if fingerprint==1 else 2)
    region=classify_region(first)
    iterations=variant+1
    for _ in range(iterations):first,second,checksum=step_key(first,second)
    inverted=checksum^255
    major=4 if region==3 else inverted>>6
    size=((inverted>>2)&15)+1;minor=inverted&3
    return dict(result=result,flags=flags,region=region,major=major,size=size,minor=minor,
                first=first,second=second,alt_af=minor*256+(logical_flags(minor)|0x10))


def main():
    _,_,base=make_context();memory=bytearray(65536)
    for start,page in ((0x4000,5),(0x8000,2),(0xC000,1)):memory[start:start+16384]=bytes(base[page])
    simulator=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                           'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                           '^BC':0x58BE,'^AF':0x69CF},None,False)
    region_cases=key_cases=signature_cases=banked_cases=0
    def run(entry):
        memory[0x7FFE:0x8000]=bytes([255,63]);simulator.registers[:]=initial
        return simulator.registers
    # Проверка всех пар H,L по независимым прямоугольникам, остальные регистры классификатор сохраняет.
    for word in range(65536):
        r=run(0xE779);r[H],r[L]=word>>8,word&255
        simulator.run(start=0xE779,stop=0x3FFF)
        assert (r[A],r[F],r[SP])==(classify_region(word),region_flags(word),0x8000)
        assert r[H]*256+r[L]==word
        for reg in (*range(2,6),*range(8,12),*range(16,24)):assert r[reg]==initial[reg]
        region_cases+=1
    # Проверка всех первых слов с граничными вторыми словами, включая переносы на каждом сложении.
    for first,second in product(range(65536),(0,1,0x7FFF,0xFFFF)):
        r=run(0xA9F3);memory[0x631C:0x6320]=first.to_bytes(2,'little')+second.to_bytes(2,'little')
        simulator.run(start=0xA9F3,stop=0x3FFF)
        a,b,checksum=step_key(first,second)
        assert memory[0x631C:0x6320]==a.to_bytes(2,'little')+b.to_bytes(2,'little')
        assert (r[H]*256+r[L],r[D]*256+r[E],r[A],r[F],r[SP])==(a,b,checksum,logical_flags(checksum),0x8000)
        assert r[B]*256+r[C]==0x36C9 and r[8:12]==initial[8:12] and r[16:24]==initial[16:24]
        key_cases+=1
    # Проверка банкового ядра в плоском представлении банка 1, все варианты задают от 1 до 256 шагов.
    words=(0,0x4733,0x4734,0x4737,0x4738,0x473A,0x473B,0x4937,0x4A35,0x4A36,0x4D39,0x4E39,0xFFFF)
    for first,second,variant in product(words,(0,1,0x7FFF,0xFFFF),range(256)):
        r=run(0xC9B9);r[H],r[L]=first>>8,first&255;r[D],r[E]=second>>8,second&255;r[A]=variant
        simulator.run(start=0xC9B9,stop=0x3FFF);expected=signature(first,second,variant)
        assert (r[H],r[L],r[D],r[E],r[A],r[F])==tuple(expected[k] for k in ('major','size','region','minor','result','flags'))
        assert r[B]*256+r[C]==0x36C9 and r[SP]==0x8000
        assert r[16]*256+r[17]==expected['alt_af']
        signature_cases+=1
    # Проверка исходных обёрток с физическими переключениями банка и загрузкой ключа из памяти станции.
    for first,second,variant,old in product(words,(0,0xFFFF),(0,1,255),range(32)):
        banked=SliceableMemory(banks=[bank.copy() for bank in base],out7ffd=old)
        put(banked,0x983F,list(first.to_bytes(2,'little')+second.to_bytes(2,'little')+bytes([variant])))
        banked[0x6306]=old;put(banked,0x7FFE,[255,63]);sim=Simulator(banked);trace=PortTrace(sim);sim.set_tracer(trace)
        sim.registers[:]=initial;sim.run(start=0xA464,stop=0x3FFF);r=sim.registers;expected=signature(first,second,variant)
        assert (r[H],r[L],r[D],r[E],r[A],r[F])==tuple(expected[k] for k in ('major','size','region','minor','result','flags'))
        final=(old&0xF8)|0x10
        assert trace.writes==[(0x7FFD,(old&0xF8)|0x11),(0x7FFD,final)]
        assert banked[0x6306]==final and banked.o7ffd==final and r[SP]==0x8000
        assert (r[16],r[17])==(final,logical_flags(final))
        banked_cases+=1
    report=dict(passed=True,method='original_region_key_step_and_signature_against_independent_integer_reference',
                region_cases=region_cases,key_step_cases=key_cases,signature_cases=signature_cases,
                banked_wrapper_cases=banked_cases,all_variants=True,variant255_means256_steps=True,
                region_names_or_game_roles_proved=False,random_quality_or_period_proved=False,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/WorldSignatureVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
