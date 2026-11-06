"""Полная цепь 6C8F, настоящий арифметический SP, восстановление CPU SP и публикация третьего знака."""
from collections import Counter
from itertools import product
import json,random
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import xor_flags
from ReferenceActionPatchedVector import evaluate
from CheckActionThirdGlyphPublish import quarter
from ReferenceControlsPointRespawn import refresh

INPUTS=(0xAF48,0xAF56,0xAF69)
OUTPUTS=(0xD9B6,0xD7C4,0xD7A2)
COEFFICIENTS=((0xCB3E,0xCB54,0xCB6F),(0xCB8B,0xCBA1,0xCBBC),(0xCBD8,0xCBEE,0xCC09))


def profiles():
    diagonal=((127,0,0),(0,127,0),(0,0,127))
    # Проверка каждого полного значения запрета и каждого входного F.
    for gate in range(256):
        for flags in range(256):yield gate,flags,(flags*257,(flags*73)&65535,flags^65535),diagonal,'gate_and_flags'
    # Проверка знаков и границ копируемых слов во всех трёх позициях.
    edges=(0,1,127,128,255,32767,32768,65535)
    for vector in product(edges,repeat=3):yield 0,sum(vector)&255,vector,diagonal,'vector_edges'
    # Проверка каждого коэффициента в каждой из девяти физических позиций.
    for row in range(3):
        for column in range(3):
            for coefficient in range(256):
                matrix=[[0]*3 for _ in range(3)];matrix[row][column]=coefficient
                yield 0,coefficient,(32767,32768,65535),matrix,'coefficient_positions'
    # Проверка всех шести мест досрочного выхода, оба знака и частично записанные выходы.
    for row in range(3):
        matrix=[[0]*3 for _ in range(3)];matrix[row]=[127]*3
        for word in (32767,32768,16000,(-16000)&65535):yield 0,word&255,(word,word,word),matrix,'overflow_sites'
    randomizer=random.Random(0x6C8F)
    for _ in range(4096):yield 0,randomizer.randrange(256),tuple(randomizer.randrange(65536) for _ in range(3)),[
        [randomizer.randrange(256) for _ in range(3)] for _ in range(3)],'mixed_vectors_and_matrices'


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    cases=0;counts=Counter();paths=Counter();overflow_sites=Counter()
    for gate,flags,vector,matrix,kind in profiles():
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        def fixture_word(address,value):memory[address],memory[address+1]=value&255,value>>8
        for address,value in zip((0x9B79,0x9B7C,0x9B7F),vector):fixture_word(address,value)
        for addresses,values in zip(COEFFICIENTS,matrix):
            for address,value in zip(addresses,values):memory[address]=value
        old_outputs=(0x5342,0x6453,0x7564)
        for address,value in zip(OUTPUTS,old_outputs):fixture_word(address,value)
        memory[0x9B82]=gate
        for delta in range(3):memory[0x9B84+delta]=(cases*73+delta*109)&255
        stack=0x8002 if cases&1 else 0xBFFE;fixture_word(stack,0x3FFF)
        initial=get_registers({'AF':((cases*73)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0x6C8F},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,cases&255,cases&1,cases%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]

        def put(address,value):
            bank=5 if address<0x8000 else 2 if address<0xC000 else 0
            expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))

        def word(address,value):put(address,value&255);put(address+1,value>>8)

        if gate:
            wanted[0:2]=[gate,xor_flags(gate)];m1=3;paths['gate']+=1
        else:
            result=evaluate(vector,matrix,old_outputs)
            for address,value in zip(INPUTS,vector):word(address,value)
            word(0x6CB2,stack);word(0xAFF1,0xABCD)
            for row in result['performed']:word(OUTPUTS[row],result['outputs'][row])
            wanted[0:2]=result['af'];wanted[3]=0;wanted[4:6]=[result['de']>>8,result['de']&255]
            wanted[6:8]=[result['hl']>>8,result['hl']&255];wanted[16:18]=result['alternate_af'];wanted[10:12]=[0x6C,0xB1]
            if result['overflow']:
                m1=16+result['refresh_m1'];paths['overflow']+=1
                overflow_sites[str(result['stop_position'])]+=1
            else:
                x,_,_=quarter(result['outputs'][0]);y,f,hl=quarter(result['outputs'][1]);sign=result['outputs'][2]>>8
                for address,value in ((0x9B85,x),(0x9B84,y),(0x9B86,sign)):put(address,value)
                wanted[0:2]=[sign,f];wanted[6:8]=[hl>>8,hl&255];m1=37+result['refresh_m1'];paths['published']+=1
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6C8F,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(cases,kind,gate,vector,matrix,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(cases,kind,'RAM')
        assert Counter(memory.writes)==Counter(writes),(cases,kind,'writes')
        cases+=1;counts[kind]+=1
    assert len(overflow_sites)==6,overflow_sites
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(counts),paths=dict(paths),overflow_sites=dict(overflow_sites),
        all_gate_and_initial_F_pairs=True,all_matrix_byte_positions=True,all_six_overflow_sites=True,
        full_vector_and_matrix_product_exhausted=False,compositional_numeric_oracle=True,independent_new_vector_oracle=False,
        actual_arithmetic_SP_children_executed=True,real_stack_restore_and_publisher_executed=True,
        exact_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        cpu_stack_written=False,partial_vector_outputs_preserved_on_overflow=True,third_fields_preserved_on_overflow=True,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionThirdGlyphVectorVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
