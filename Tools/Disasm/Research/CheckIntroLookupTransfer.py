"""Полный RenderLookupTexture до входа продолжения, обе настоящие сгенерированные цепочки."""
from collections import Counter
import json
from CheckIntro import ROOT,original_memory,execute
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers,PC,SP


def main():
    flat=original_memory();generated=original_memory()
    execute(generated,{'PC':0x6C9C},stop=0x6CF9)
    sum_chain=flat[0x6D7E:0x6D8D]*256;sum_chain[-2]=0xC9
    assert generated[0x9900:0xA800]==sum_chain
    copy_chain=[]
    for row in range(38):
        for col in range(8):copy_chain.extend((0xE1,0x22,2*col,0xC0+row))
    copy_chain.extend((0xC3,0xBC,0x6B))
    assert generated[0xA800:0xACC3]==copy_chain
    flat[0x9900:0xA800]=sum_chain;flat[0xA800:0xACC3]=copy_chain
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=17)
    simulator=Simulator(memory);cases=0
    for phase in range(256):
        for stack in (0xBFFE,0x5FFE,0x8FFE):
            memory.recording=False
            for bank in (1,2,5):memory.banks[bank][:]=base[bank]
            phases=(phase,(phase*73+19)&255,(phase*37+11)&255,(phase*109+7)&255)
            for address,value in zip((0x6BA2,0x6BA6,0x6BA9,0x6BAC),phases):memory[address]=value
            pointer=0xF000+16*(39+phase%33)
            memory[0x6BB2],memory[0x6BB3]=pointer&255,pointer>>8
            memory[stack],memory[stack+1]=255,63
            tables=[]
            # Создание независимых фазовых таблиц, включая переполнение байтовой суммы.
            for page in range(0x94,0x99):
                table=[(index*37+phase*53+page*11)&255 for index in range(256)]
                tables.append(table)
                memory.banks[2][(page-0x80)*256:(page-0x7F)*256]=bytes(table)
            for index in range(608):memory[pointer+index]=(index*73+phase*19)&255
            initial=get_registers({'AF':((phase*73)&255)*256+phase,'HL':0x1234,
                'DE':0x2468,'BC':0x3600+((phase*19)&255),'IX':0xABCD,'IY':0x5C3A,
                '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,
                'SP':stack,'PC':0x6B9C},None,False)
            initial[14],initial[26],initial[27]=phase,phase&1,phase%3
            expected=[bytearray(b) for b in memory.banks];writes=[]

            def put(address,value):
                bank=5 if address<0x8000 else 2 if address<0xC000 else 1
                expected[bank][address&0x3FFF]=value
                writes.append((bank,address&0x3FFF,value))

            put(stack-1,0x6B);put(stack-2,0xB1)
            # Расчёт 256 сумм, индексы всех четырёх таблиц оборачиваются без переноса страницы.
            for index in range(256):
                values=[tables[n][(phases[n]+index)&255] for n in range(4)]
                total=sum(values)&255;value=tables[4][total]
                put(0x9300+index,value)
            carry=((sum(values[1:])&255)+values[0])>255
            final_f=(phase&0xA8)|(0x40 if phase==0 else 0)|(0x10 if phase&15==0 else 0)|(4 if phase==0x80 else 0)|carry
            put(0x6BBD,stack&255);put(0x6BBE,stack>>8)
            # Перенос 304 слов через POP, по восемь слов в начало каждой из 38 страниц.
            for row in range(38):
                for col in range(16):put(0xC000+256*row+col,memory[pointer+16*row+col])
            final_word=memory[pointer+606]+256*memory[pointer+607]
            wanted=list(initial)
            wanted[0:8]=[value,final_f,0x98,total,0x93,0xFF,final_word>>8,final_word&255]
            wanted[18:24]=[0x95,phases[1],0x97,phases[3],0x96,phases[2]]
            wanted[SP],wanted[PC]=pointer+608,0x6BBC
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            simulator.run(start=0x6B9C,stop=0x6BBC);memory.recording=False
            # Проверка временного SP на входе продолжения, CPU SP здесь ещё не восстановлен.
            compared=(*range(15),*range(16,25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(phase,hex(stack),
                [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)),(phase,hex(stack),'RAM')
            assert Counter(writes)==Counter(memory.writes),(phase,hex(stack),'writes')
            cases+=1
    report=dict(passed=True,total_cases=cases,all_four_phase_low_bytes_covered=True,
        cpu_stack_locations=3,actual_generated_chains_executed=True,
        sum_chain_bytes=3840,transfer_chain_bytes=1219,lookup_bytes_written=256,
        transferred_bytes=608,destination_pages=38,stop_PC=0x6BBC,
        cpu_SP_restored_at_stop=False,all_registers_except_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        independent_numeric_oracle=True,all_phase_combinations_exhausted=False,
        continuation_and_IRQ_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/IntroLookupTransferVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
