"""Пометка Component0=8000 и однократный пропуск FF, точный порядок трёх записей и настоящий поиск."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main(entry=0xF394,index_register='IX',report_tag='ActionRecordReuse'):
    assert (entry,index_register) in ((0xF394,'IX'),(0xF03D,'IY'))
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory);cases=0;counts=Counter()

    def run(initial,wanted,expected,writes,entry):
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(hex(entry),initial[8:10],
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)),(hex(entry),'RAM')
        assert memory.writes==writes,(hex(entry),'write_order',memory.writes,writes)

    def fixture(pointer,flags):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        memory[0xBFFE],memory[0xBFFF]=255,63
        memory[pointer],memory[pointer+1],memory[pointer+24]=flags,(flags*73)&255,(flags*37)&255
        registers={'AF':((flags*109)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':entry}
        registers[index_register]=pointer
        initial=get_registers(registers,None,False)
        initial[14],initial[15],initial[26],initial[27]=flags,flags,flags&1,flags%3
        return initial

    for pointer in (*range(0xA100,0xA780,64),0x90FF,0xBFFF,0xFFBF):
        for flags in range(256):
            # Создание случая без пересечения возвращаемого слова с записью на границе BFFF.
            initial=fixture(pointer,flags)
            if pointer==0xBFFF:
                initial[SP]=0x5FFE;memory[0x5FFE],memory[0x5FFF]=255,63
                memory[pointer]=flags
            expected=[bytearray(b) for b in memory.banks];writes=[]
            for address,value in ((pointer+1,128),(pointer,0),(pointer+24,255)):
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                expected[bank][address&0x3FFF]=value;writes.append((bank,address&0x3FFF,value))
            wanted=list(initial);wanted[15]=refresh(initial[15],7);wanted[SP]=initial[SP]+2;wanted[PC]=0x3FFF
            run(initial,wanted,expected,writes,entry)
            cases+=1;counts['standalone']+=1
    # Проверка протокола с настоящим FindReusableRecord, запись пропускается только при её достижении поиском.
    for position in range(26):
        pointer=0xA100+64*position;initial=fixture(pointer,position)
        for index in range(27):
            row=0xA100+64*index
            memory[row],memory[row+1],memory[row+24]=(128,128,0) if index==26 else (17,1,0)
        expected=[bytearray(b) for b in memory.banks];writes=[]
        for address,value in ((pointer+1,128),(pointer,0),(pointer+24,255)):
            expected[2][address&0x3FFF]=value;writes.append((2,address&0x3FFF,value))
        wanted=list(initial);wanted[15]=refresh(initial[15],7);wanted[SP],wanted[PC]=0xC000,0x3FFF
        run(initial,wanted,expected,writes,entry)
        for scan in (0,1):
            previous=list(simulator.registers);previous[SP],previous[PC]=0xBFFE,0xE9A1
            wanted=list(previous);wanted[4:6]=[0,64];wanted[SP],wanted[PC]=0xC000,0x3FFF
            if scan==0:
                wanted[0:2]=[128,0x42];wanted[10:12]=[0xA7,0x80]
                wanted[15]=refresh(previous[15],179)
            else:
                wanted[0:2]=[1,1];wanted[10:12]=[pointer>>8,pointer&255]
                wanted[15]=refresh(previous[15],20+6*position)
            expected[2][(pointer+24)&0x3FFF]=0
            run(previous,wanted,expected,[(2,(pointer+24)&0x3FFF,0)],0xE9A1)
        cases+=1;counts['release_then_two_real_searches']+=1
    report=dict(passed=True,total_cases=cases,cases_by_kind=dict(counts),entry=entry,index_register=index_register,
        physical_records=26,all_initial_flags_values=True,three_extra_boundary_pointers=True,
        preserved_all_registers_including_R=True,setter_refresh_m1=7,
        component0_word_written=32768,reuse_byte_written=255,
        exact_store_order=['Component0.High','Component0.Low','ReuseByte'],
        cpu_stack_written=False,all_physical_ram_bytes_proved=True,
        write_order_and_multiplicity_proved=True,real_FindReusableRecord_executed=True,
        first_reaching_search_skips_and_clears=True,next_reaching_search_accepts=True,
        independent_numeric_oracle=True,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/('Tools/Disasm/Reports/'+report_tag+'Verification.json')).write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
