"""Оригинальный нулевой операнд F573 и шесть записей в базовые слова, весь входной AF."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();assert flat[0xF572:0xF575]==[0x21,0,0]
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory)
    for af in range(65536):
        memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=base[page]
        memory[0xBFFE],memory[0xBFFF]=255,63
        for address,value in zip((0xE5B0,0xE5CF,0xE5EA),(af,(73*af+17)&65535,af^65535)):
            memory[address],memory[address+1]=value&255,value>>8
        initial=get_registers({'AF':af,'HL':af^0xA55A,'DE':0x2468,'BC':0x369C,
            '^HL':0xFEDC,'^DE':0xBA98,'^BC':0x7654,'^AF':0x3210,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xF572},None,False)
        initial[14],initial[15],initial[26],initial[27]=af&255,af&255,af&1,af%3
        wanted=list(initial);wanted[6:8]=[0,0];wanted[15],wanted[SP],wanted[PC]=refresh(initial[15],5),0xC000,0x3FFF
        expected=[bytearray(b) for b in memory.banks];writes=[]
        for address in (0xE5B0,0xE5CF,0xE5EA):
            for delta in (0,1):expected[0][(address+delta)&0x3FFF]=0;writes.append((0,(address+delta)&0x3FFF,0))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0xF572,stop=0x3FFF);memory.recording=False
        assert all(wanted[i]==simulator.registers[i] for i in (*range(25),26,27)),af
        assert all(a==b for a,b in zip(expected,memory.banks)) and memory.writes==writes,af
    report=dict(passed=True,total_cases=65536,all_input_AF=True,all_prior_words_in_each_field=True,
        full_three_word_product_exhausted=False,original_zero_immediate_required=True,
        exact_registers_including_R=True,refresh_m1=5,all_physical_ram_bytes_proved=True,
        write_order_and_multiplicity_proved=True,hardware_bus_write_order_proved=False,cpu_stack_written=False,
        independent_numeric_oracle=True,irq_executed=False,native_execution=False,assembly_executed=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ActionRecordBaseResetVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
