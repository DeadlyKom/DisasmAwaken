"""AFF5, независимое отрицание шести физических слов базиса, точные флаги и R."""
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckSignedMultiply import sbc16_flags
from ReferenceControlsPointRespawn import refresh

ADDRESSES=(0x9B04,0x9B0A,0x9B10,0x9B00,0x9B06,0x9B0C)


def main():
    memory=Memory(flat_action());memory[0xBFFE:0xC000]=[255,63];simulator=Simulator(memory);cases=0
    def check(values,af):
        nonlocal cases
        memory.recording=False
        for address,value in zip(ADDRESSES,values):memory[address:address+2]=[value&255,value>>8]
        for i,address in enumerate((0x9B02,0x9B08,0x9B0E)):memory[address:address+2]=[(cases+73*i)&255,(cases*3+i)&255]
        expected=list(memory);writes=[]
        # Расчёт отрицания по модулю 65536, шесть независимых слов без перестановки, средняя строка неизменна.
        for address,value in zip(ADDRESSES,values):
            result=(-value)&65535;expected[address:address+2]=[result&255,result>>8];writes.extend(((address,result&255),(address+1,result>>8)))
        initial=get_registers({'PC':0xAFF5,'SP':0xBFFE,'AF':af,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
        initial[14]=cases&255;initial[15]=cases&255;initial[26]=cases&1;initial[27]=cases%3
        wanted=list(initial);last=values[-1];result=(-last)&65535
        wanted[1]=sbc16_flags(0,last,0);wanted[4:8]=[last>>8,last&255,result>>8,result&255]
        wanted[PC]=0x3FFF;wanted[SP]=0xC000;wanted[15]=refresh(initial[15],43)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(33):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('нет возврата')
        memory.recording=False
        assert all(simulator.registers[i]==wanted[i] for i in (*range(13),14,15,*range(16,24),PC,26,27))
        assert memory==expected and memory.writes==writes;cases+=1
    # Проверка полного домена каждого из шести слов, смешанных наборов и всех входных A/F.
    for value in range(65536):check((value,)*6,((value*73)&65535))
    for seed in range(512):check(tuple((seed*257+i*10923)&65535 for i in range(6)),(seed*109)&65535)
    for value in range(256):check((0,1,32767,32768,65535,value*257),(value<<8)|(value^0xA5))
    assert cases==66304
    result=dict(passed=True,total_cases=cases,all_word_values_at_each_target=True,mixed_words_cases=512,
        all_input_A_and_F_values=True,exact_registers_flags_R_and_SP=True,
        all_ram_and_ordered_writes_checked=True,refresh_M1=43,no_stack_writes=True,
        target_words=6,middle_row_words_unchanged=3,full_six_word_product_exhausted=False,
        assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionReverseViewBasisVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
