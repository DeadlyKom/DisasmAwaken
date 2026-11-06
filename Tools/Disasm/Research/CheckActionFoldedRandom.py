"""Все младшие слова при трёх старших байтах и все байты на границах, реальные три потока."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh
from ReferenceActionFoldedRandom import step
from ActionRandomStreamLayout import STREAMS

ROOTS=tuple((entry,pointer) for _,entry,pointer in STREAMS)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    expected=[bytearray(b) for b in base];simulator=Simulator(memory);touched=set();cases=0;counts=Counter()
    flow=json.loads((ROOT/'Tools/Disasm/Reports/ControlFlow.json').read_text('utf-8'))
    code=[i for r in flow if r['name']=='Action' for i in r['instructions'] if 0xEC08<=i['address']<0xEC54]
    assert len(code)==61
    core_m1=sum(2 if bytes.fromhex(i['hex'])[0] in (0xED,0xCB,0xDD,0xFD) else 1 for i in code)
    assert core_m1==63
    for entry,pointer in ROOTS:
        assert bytes(flat[entry:entry+7])==bytes((0xD9,0x21,pointer&255,pointer>>8,0xC3,0x08,0xEC))

    def bank(address):return 5 if address<0x8000 else 2 if address<0xC000 else 0

    def check(entry,pointer,word,fold,kind,stack=0xBFFE):
        nonlocal cases,touched
        memory.recording=False
        for page,offset in touched:
            memory.banks[page][offset]=expected[page][offset]=base[page][offset]
        touched=set()

        def setup(address,value):
            page=bank(address);offset=address&0x3FFF
            memory[address]=value;expected[page][offset]=value;touched.add((page,offset))

        for address,value in ((pointer,word&255),(pointer+1,word>>8),(pointer+2,fold),(stack,255),(stack+1,63)):setup(address,value)
        initial=get_registers({'AF':((cases*109)&255)*256+(cases&255),
            'HL':pointer if entry==0xEC08 else 0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
            'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=cases&255,(cases*73)&255,cases&1,cases%3
        value=step(word,fold);writes=[]

        def put(address,byte):
            page=bank(address);offset=address&0x3FFF
            expected[page][offset]=byte;touched.add((page,offset));writes.append((page,offset,byte))

        def put_word(address,value):put(address,value&255);put(address+1,value>>8)

        # Сохранение курсора третьего байта, запись нового состояния и стековая передача слова между наборами.
        put_word(stack-2,pointer+2)
        put(pointer+2,value['fold']);put_word(pointer,value['word'])
        put_word(stack-2,value['word'])
        wanted=list(initial);wanted[0:2]=[value['fold'],value['flags']]
        if entry==0xEC08:wanted[2:6]=initial[18:22]
        wanted[6:8]=[value['word']>>8,value['word']&255]
        wanted[18:24]=[0,value['mixed_low']&255,value['word']>>8,value['word']&255,pointer>>8,pointer&255]
        wanted[15]=refresh(initial[15],core_m1+(0 if entry==0xEC08 else 3))
        wanted[SP],wanted[PC]=stack+2,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        # Проверка полного обмена регистров, R и каждого физического байта с кратностью записей.
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(hex(entry),hex(pointer),word,fold,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(hex(entry),word,fold,'RAM')
        assert Counter(writes)==Counter(memory.writes),(hex(entry),word,fold,'writes')
        cases+=1;counts[kind]+=1

    # Проверка всех 65536 слов при трёх значениях FoldByte, включая полный перенос между байтами.
    for fold in (0,127,255):
        for word in range(65536):check(0xEC08,0xEBDE,word,fold,'all_low_words')
        print('Все слова, FoldByte='+str(fold)+' проверены',flush=True)
    # Проверка перехода страницы и конца RAM без оборачивания трёхбайтовой записи в ROM.
    for pointer in (0x90FF,0xFFFD):
        for fold in range(256):
            for word in (0,1,0x7FFF,0x8000,0xFFFF):check(0xEC08,pointer,word,fold,'pointer_boundaries',stack=0x9AFE)
    for entry,pointer in ROOTS:
        for fold in range(256):
            for word in (0,1,0x7FFF,0x8000,0xFFFF):check(entry,pointer,word,fold,'stream_wrappers',stack=0x5FFE)
        check(entry,pointer,flat[pointer]+256*flat[pointer+1],flat[pointer+2],'original_initial_states')
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(counts),
        all_low_words_at_fold_values=[0,127,255],all_fold_bytes_at_boundary_words=True,
        original_stream_entries=len(ROOTS),all_original_wrapper_bytes_verified=True,original_initial_states_checked=True,
        core_instruction_count=61,core_refresh_m1=63,wrapper_refresh_m1=66,
        all_registers_including_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        maximum_additional_CPU_stack_bytes=2,independent_numeric_oracle=True,
        full_24_bit_state_domain_exhausted=False,period_and_uniformity_proved=False,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionFoldedRandomVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
