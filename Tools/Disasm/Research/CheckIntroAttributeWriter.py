"""Полные побочные эффекты построителя атрибутов, без сборки и аппаратных IRQ."""
from collections import Counter
import json
from CheckIntro import ROOT, original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator, get_registers, PC, SP


def main():
    flat=original_memory()
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5]=bytearray(flat[0x4000:0x8000])
    base[2]=bytearray(flat[0x8000:0xC000])
    base[0]=bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16)
    simulator=Simulator(memory)
    cases=0
    for origin in range(256):
        for step in (0,1,0xFFFF,0x0101,0x8000,0x7FFF):
            memory.recording=False
            for bank in (0,2,5):memory.banks[bank][:]=base[bank]
            stack=(0xBFFE,0xB0FC,0x5FFE)[cases%3]
            memory[stack],memory[stack+1]=255,63
            for i in range(16):memory[0x6993+i]=(i*47+origin*73+step)&255
            initial=get_registers({'AF':((origin*19)&255)*256+origin,'HL':0x1234,
                'DE':(origin*257+step*11)&65535,'BC':step,'IX':0xAB00+origin,
                'IY':0xCD73,'^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,
                '^AF':0x3210,'SP':stack,'PC':0x692D},None,False)
            initial[14],initial[26],initial[27]=origin,origin&1,origin%3
            expected=[bytearray(b) for b in memory.banks]
            writes=[]

            def put(address,value):
                bank=5 if address<0x8000 else 2 if address<0xC000 else 0
                expected[bank][address&0x3FFF]=value
                writes.append((bank,address&0x3FFF,value))

            def word(address,value):
                put(address,value&255);put(address+1,value>>8)

            # Создание 32 независимых команд, младшие адреса оборачиваются без переноса.
            for row in range(8):
                for column in range(4):
                    address=0x68A9+16*row+4*column
                    for offset,value in enumerate((0xE1,0x22,(origin+2*column)&255,(origin+row)&255)):
                        put(address+offset,value)
            # Создание двух одинаковых таблиц указателей и запись возврата первого CALL.
            word(stack-2,0x6954)
            pointer=initial[4]*256+initial[5]
            for index in range(38):
                word(0x6000+4*index,pointer)
                word(0x6100+4*index,pointer)
                pointer=(pointer+step)&65535
            word(stack-2,0x695F)
            # Объединение двух разных наборов восьми полубайтов, включая PUSH BC обеих фаз.
            source=list(memory[0x6993:0x69A3])
            for matrix in range(2):
                for row in range(8):
                    word(stack-(4 if matrix==0 else 2),0x6993+8*matrix)
                    for column in range(8):
                        put(0x60C0+0x100*matrix+8*row+column,
                            (source[8*matrix+column]&0xF0)|(source[8*matrix+row]&15))
            wanted=list(initial)
            wanted[0:8]=[source[-1],0x42,0x69,0x9B,0x61,0,0x69,0xA3]
            wanted[8:12]=[0,0,initial[10],source[-1]&15]
            wanted[18:24]=[0,0,(origin+8)&255,(origin+8)&255,0x69,0x29]
            wanted[SP],wanted[PC]=stack+2,0x3FFF
            simulator.registers[:]=initial;memory.writes=[];memory.recording=True
            simulator.run(start=0x692D,stop=0x3FFF)
            memory.recording=False
            # Проверка всех регистров кроме R, физической RAM и кратности каждой записи.
            compared=(*range(15),*range(16,25),26,27)
            assert all(wanted[i]==simulator.registers[i] for i in compared),(
                origin,step,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
            assert all(a==b for a,b in zip(expected,memory.banks)),(origin,step,'RAM')
            assert Counter(writes)==Counter(memory.writes),(origin,step,'writes')
            cases+=1
    report=dict(passed=True,total_cases=cases,all_IXL_values=True,pointer_steps=6,
        cpu_stack_locations=3,generated_bytes=128,paired_pointer_records=38,
        attribute_matrices=2,attribute_bytes=128,all_registers_except_R=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        actual_child_procedures_executed=True,independent_numeric_oracle=True,
        timing_proved=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroAttributeWriterVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
