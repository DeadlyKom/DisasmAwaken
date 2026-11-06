"""Три кодированных слова, инвертированная компонента 1, отрицательный ноль и предел 8000."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def encode(word,inverted=False):
    if inverted:return (-word)&65535 if word&32768 else word|32768
    return ((-word)&65535)|32768 if word&32768 else word


def evaluate_encoding(values,initial_a,carry):
    encoded=[encode(value,index==1) for index,value in enumerate(values)]
    a=initial_a
    for value in values:
        if value&32768:a=(value>>8)^255
    high=values[2]>>8
    flags=(0x92|((high^255)&0x28) if high&128 else 0x54|(high&0x28))|(carry&1)
    m1=19+9*int(values[0]&32768!=0)+7*int(values[1]&32768!=0)+9*int(values[2]&32768!=0)
    return dict(words=encoded,af=(a,flags),hl=encoded[2],refresh_m1=m1)


def main():
    flat=flat_action();base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    for serial in range(65792):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        values=(serial&65535,(serial*73+17)&65535,(serial*109+0xA55A)&65535)
        for address,value in zip((0xD9B6,0xD7C4,0xD7A2),values):memory[address],memory[address+1]=value&255,value>>8
        for index in range(3):memory[0x9B1E+3*index]=(serial+index*73)&255
        memory[0xBFFE],memory[0xBFFF]=255,63
        flags=(serial&255)&251 if serial<65536 else serial&255
        initial=get_registers({'AF':((serial*37)&255)*256+flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6C43},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        expected=[bytearray(b) for b in memory.banks];wanted=list(initial);writes=[]
        m1=1
        if not flags&4:
            result=evaluate_encoding(values,initial[0],flags&1);encoded=result['words']
            for address,value in zip((0x9B1F,0x9B22,0x9B25),encoded):
                for offset,byte in enumerate((value&255,value>>8)):
                    expected[2][(address+offset)&0x3FFF]=byte;writes.append((2,(address+offset)&0x3FFF,byte))
            wanted[6:8]=[encoded[2]>>8,encoded[2]&255]
            wanted[0:2]=result['af'];m1=result['refresh_m1']
        wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],m1),0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x6C43,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),(serial,values,
            [(i,wanted[i],simulator.registers[i]) for i in (*range(25),26,27) if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes,serial
    report=dict(passed=True,total_cases=65792,all_words_in_each_component=True,all_input_F=True,
        full_word_product_exhausted=False,inverted_second_component_preserved=True,
        second_zero_encodes_8000=True,input_8000_edge_preserved=True,
        lower_bytes_of_three_components_preserved=True,exact_registers_including_R=True,
        publish_refresh_m1_base=19,negative_component_m1_additions=[9,7,9],overflow_gate_refresh_m1=1,
        all_physical_ram_bytes_proved=True,write_order_and_multiplicity_proved=True,
        hardware_bus_word_write_order_proved=False,cpu_stack_written=False,independent_numeric_oracle=True,
        irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionComponentEncodingVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
