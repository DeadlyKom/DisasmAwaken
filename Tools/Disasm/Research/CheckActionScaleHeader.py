"""E1B9..E1D0, масштаб из заголовка и три смещения JR, отдельная граница без исполнения соседнего обхода."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh


def main():
    baseline=flat_action();memory=Memory(baseline);simulator=Simulator(memory);counts=Counter()
    def check(mantissa,exponent,flags=255):
        assert 1<=exponent<=6
        memory.recording=False
        for address in (0xE1C8,0xE232,0xE26B):memory[address]=0xFE
        memory[0xE2C5:0xE2C7]=[0x34,0x12]
        initial=get_registers({'AF':0xA500|flags,'HL':(exponent<<8)|mantissa,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xE1B9},None,False)
        serial=counts.total();initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);shift=exponent-1;scaled=mantissa<<shift
        f=sub8_flags(6,exponent)
        if shift:
            previous=mantissa<<(shift-1)
            f=(f&0xC4)|((scaled>>8)&0x28)|(16 if (previous&4095)*2>4095 else 0)
        writes=[(0xE1C8,6-exponent),(0xE232,6-exponent),(0xE26B,6-exponent),(0xE2C5,scaled&255),(0xE2C6,scaled>>8)]
        for address,value in writes:expected[address]=value
        wanted[0:2]=[6-exponent,f];wanted[6:8]=[scaled>>8,scaled&255]
        wanted[PC],wanted[15]=0xE1D1,refresh(initial[15],7+exponent)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(0xE1B9,0xE1D1);memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(mantissa,exponent,flags,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and memory.writes==writes,(mantissa,exponent,memory.writes,writes)
        counts['exponent_'+str(exponent)]+=1
    # Проверка всех допустимых сочетаний мантиссы и показателя, исходные флаги меняются отдельно.
    for exponent in range(1,7):
        for mantissa in range(256):check(mantissa,exponent,flags=mantissa^exponent)
    for flags in range(256):check(flags^165,1+flags%6,flags)
    # Проверка области применимости по всем 128 исходным чётным указателям OBJECT3D, без объявления игрового диапазона индексов.
    action=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes()
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();headers=[]
    for index in range(0,256,2):
        pointer=action[0x3E00+index]+256*action[0x3E01+index];offset=pointer-0xC000
        assert 0<=offset<len(objects)-1
        mantissa,exponent=objects[offset:offset+2];assert 1<=exponent<=6
        headers.append((mantissa,exponent));check(mantissa,exponent)
    report=dict(passed=True,total_cases=counts.total(),cases_by_exponent=dict(counts),
        method='independent_integer_scaling_flags_and_patch_oracle',
        all_valid_header_words=True,valid_exponents=[1,2,3,4,5,6],original_even_table_headers_checked=128,
        original_header_exponents=sorted({h for _,h in headers}),
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_checked=True,
        execution_boundary='E1B9..E1D1, no continuation executed',maximum_additional_stack_bytes=0,
        invalid_exponents_executed=False,whole_projection_scan_proved=False,
        all_joint_inputs_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionScaleHeaderVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
