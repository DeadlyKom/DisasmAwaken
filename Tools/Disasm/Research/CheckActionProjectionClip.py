"""E213..E298, три знаковых проверки и две оси с исходной симметричной квадратной таблицей."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from ReferenceControlsBufferPoints import sub16_flags
from ReferenceControlsPointRespawn import refresh
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def adc_flags(left,right):
    total=left+right;value=total&65535
    return ((value>>8)&0xA8)|(64 if value==0 else 0)|(16 if (left^right^value)&4096 else 0)|(4 if (~(left^right)&(left^value)&32768) else 0)|int(total>65535)


def asr(value,shift):return ((value if value<32768 else value-65536)>>shift)&65535


def main():
    baseline=flat_action();table=[min(i,255-i)**2//127 for i in range(256)]
    assert baseline[0x9800:0x9900]==table
    memory=Memory(baseline);simulator=Simulator(memory);counts=Counter()
    def cost(a,b):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(a,b,'h'))
    prefix=cost(0xE213,0xE21C);xp=cost(0xE21C,0xE238)-5;xc=cost(0xE238,0xE24F);xs=cost(0xE24F,0xE255)
    yp=cost(0xE255,0xE271)-5;yc=cost(0xE271,0xE28C);ys=cost(0xE28C,0xE292);ending=cost(0xE292,0xE299)
    def check(x=0,y=0,z=4096,bound=40,span=15,exponent=2,skip=0):
        memory.recording=False
        for address,value in ((0xD9B6,x),(0xD7C4,y),(0xD7A2,z)):memory[address:address+2]=[value&255,value>>8]
        memory[0xE232]=memory[0xE26B]=6-exponent;memory[0x6F59]=skip
        serial=counts.total();initial=get_registers({'AF':((serial*73)&65535),'HL':0x1357,'DE':bound,'BC':0x3600|span,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xE213},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);m1=prefix
        def pair(position,value):wanted[position:position+2]=[value>>8,value&255]
        value=(z+bound)&65535;pair(6,value);wanted[1]=adc_flags(z,bound)
        if value&32768:path='depth_rejected'
        else:
            wanted[9]=span
            # Расчёт двух байтовых индексов, SRA исходного C расширяет знак перед вычитанием, арифметика индексов оборачивается.
            half=(span if span<128 else span-256)>>1
            def extent(center):
                low=(center-half)&255;high=(center-half+span)&255
                difference=(table[high]-table[low])&255
                return difference,difference<<(exponent-1)
            difference,extent_x=extent(36);m1+=xp+exponent-1+xc
            pair(4,extent_x);pair(2,x);wanted[0]=difference
            before=asr((asr(z,1)+x)&65535,1);value=(before+extent_x)&65535
            pair(6,value);wanted[1]=adc_flags(before,extent_x)
            if value&32768:path='first_x_rejected'
            else:
                m1+=xs;wanted[1]=sub16_flags(value,x);value=(value-x)&65535;pair(6,value)
                if value&32768:path='second_x_rejected'
                else:
                    difference,extent_y=extent(33);m1+=yp+exponent-1+yc
                    pair(4,extent_y);pair(2,y);wanted[0]=difference
                    before=asr((asr(z,2)+y)&65535,1);value=(before+extent_y)&65535
                    pair(6,value);wanted[1]=adc_flags(before,extent_y)
                    if value&32768:path='first_y_rejected'
                    else:
                        m1+=ys;wanted[1]=sub16_flags(value,y);value=(value-y)&65535;pair(6,value)
                        if value&32768:path='second_y_rejected'
                        else:
                            m1+=ending;wanted[0:2]=[skip,and_flags(skip)];path='mode_rejected' if skip else 'passed'
        wanted[PC]=0xE299 if path=='passed' else 0xE40F if path=='mode_rejected' else 0xE0E2
        wanted[15]=refresh(initial[15],m1);simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(110):
            if simulator.registers[PC] in (0xE299,0xE40F,0xE0E2):break
            simulator.run()
        else:raise AssertionError('выход за границу проверки')
        memory.recording=False;compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(x,y,z,bound,span,exponent,skip,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and not memory.writes,(path,memory.writes)
        counts[path]+=1
    # Проверка каждого слова глубины, исходной границы и обеих координат в независимых сечениях.
    for value in range(65536):check(z=value);check(bound=value);check(x=value);check(y=value)
    # Проверка всех исходных байтов C и всех допустимых показателей настройки JR.
    for span in range(256):
        for exponent in range(1,7):
            for skip in (0,255):check(span=span,exponent=exponent,skip=skip)
    for skip in range(256):check(skip=skip)
    # Проверка граничных оборачиваний и равенств до принятия окончательных условий продолжения.
    edges=(0,1,255,256,32767,32768,65534,65535)
    for z in edges:
        for bound in edges:
            for x in edges:
                for y in (0,32768,65535):check(z=z,bound=bound,x=x,y=y,span=(x^y)&255,exponent=1+(x%6))
    assert set(counts)=={'depth_rejected','first_x_rejected','second_x_rejected','first_y_rejected','second_y_rejected','mode_rejected','passed'}
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),
        method='independent_byte_table_extents_and_signed_word_comparisons',
        exact_registers_flags_refresh_sp=True,every_ram_byte_checked=True,no_memory_writes=True,
        symmetric_square_table_formula_verified_for_all_256_bytes=True,
        all_word_arguments_by_separate_slices=True,all_span_bytes_and_valid_exponents=True,
        maximum_additional_stack_bytes=0,execution_boundary='E213..E299, E40F or E0E2, no continuation executed',
        all_joint_inputs_exhausted=False,whole_projection_scan_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectionClipVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
