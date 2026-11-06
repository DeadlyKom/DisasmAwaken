"""E299..E30E, три настоящих табличных отношения и частичные записи границ, без окружающего обхода."""
from collections import Counter
import json,sys
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory,xor_flags
from CheckControlsEvenSpan import and_flags
from CheckActionTypeDelta import cp_flags
from ReferenceControlsPointRespawn import refresh
from ReferenceActionLogRatio import LOG,EXP,evaluate
sys.path.insert(0,str(ROOT/'Tools/Disasm'))
from InspectZ80 import decoder


def main():
    baseline=flat_action();baseline[0x9100:0x9200]=[v&255 for v in LOG];baseline[0x9200:0x9300]=[v>>8 for v in LOG];baseline[0x9300:0x9400]=EXP
    memory=Memory(baseline);simulator=Simulator(memory);counts=Counter();touched=set()
    def cost(a,b):return sum(2 if i.bytes[0] in (0xCB,0xDD,0xED,0xFD) else 1 for i in decoder(baseline).disassemble(a,b,'h'))
    xfilter,yfilter=cost(0xE299,0xE2A7)-2,cost(0xE2A7,0xE2B5)-2
    def check(x=1,y=65535,z=256,bound=40,gate=0,marker=0):
        nonlocal touched
        memory.recording=False
        for address in touched:memory[address]=baseline[address]
        for address,value in ((0xD9B6,x),(0xD7C4,y),(0xD7A2,z),(0xE2C5,bound),(0xE331,0xAA55),(0xE33A,0xBB66),(0xE372,0xCC77),(0xE375,0xDD88)):
            memory[address:address+2]=[value&255,value>>8]
        memory[0xE310],memory[0xE021]=gate,marker;serial=counts.total()
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':(serial*73)&65535,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,
            'SP':0xBFFE,'PC':0xE299},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=list(memory);writes=[];m1=0
        def byte(a,v):expected[a]=v;writes.append((a,v))
        def word(a,v):byte(a,v&255);byte(a+1,v>>8)
        def pair(position,value):wanted[position:position+2]=[value>>8,value&255]
        def ratio(numerator,ret):
            nonlocal m1
            word(0xBFFC,ret);result=evaluate(numerator,z)
            for a,v in result['writes']:byte(a,v)
            for position,key in ((6,'hl'),(4,'de'),(2,'bc')):pair(position,result[key])
            wanted[0:2]=result['af'];wanted[16:18]=result['alternate_af'];m1+=result['refresh_m1']
            return result
        def absolute(value):
            high=value>>8
            if value&32768:
                wanted[0:2]=[(~high)&255,0x92|((~high)&0x28)]
                value=(-value)&65535
            else:wanted[1]=0x54|(high&0x28)
            pair(6,value);return value
        # Проверка старших байтов двух координат, это не сравнение полного модуля слова с 0A00.
        high=x>>8;absolute_high=high if high<128 else (-high)&255;m1+=xfilter+2*(high>=128)
        wanted[0:2]=[absolute_high,cp_flags(absolute_high,10)]
        if absolute_high>=10:path='x_high_rejected'
        else:
            high=y>>8;absolute_high=high if high<128 else (-high)&255;m1+=yfilter+2*(high>=128)
            wanted[0:2]=[absolute_high,cp_flags(absolute_high,10)]
            if absolute_high>=10:path='y_high_rejected'
            else:
                # Проверка пересечения полных масок, ненулевые байты без общего бита не запрещают расчёт.
                m1+=5;wanted[3]=gate;wanted[0:2]=[gate&marker,and_flags(gate&marker)]
                if gate&marker:path='mask_rejected'
                else:
                    m1+=5;radius=ratio(bound,0xE2CA)
                    if radius['path']=='overflow':path='bound_overflow'
                    else:
                        # Расчёт допуска арифметическим делением слова отношения на два, знак старшего бита сохраняется.
                        value=radius['hl'];signed=value if value<32768 else value-65536;half=(signed>>1)&65535
                        word(0xE331,half);pair(6,half);wanted[1]=xor_flags(half&255)|(value&1);m1+=5
                        m1+=5;rx=ratio(x,0xE2DE)
                        if rx['path']=='overflow':path='x_overflow'
                        else:
                            # Сохранение знакового X до отдельного вычисления его модуля.
                            word(0xE33A,rx['hl']);m1+=4+7*bool(rx['hl']&32768)
                            word(0xE372,absolute(rx['hl']));m1+=1
                            m1+=5;ry=ratio(y,0xE2FC)
                            if ry['path']=='overflow':path='y_overflow'
                            else:
                                pair(4,ry['hl']);m1+=5+7*bool(ry['hl']&32768)
                                word(0xE375,absolute(ry['hl']));m1+=1;path='prepared'
        wanted[PC]=0xE30F if path=='prepared' else 0xE40F;wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(550):
            if simulator.registers[PC] in (0xE30F,0xE40F):break
            simulator.run()
        else:raise AssertionError('выход за границу проверки')
        memory.recording=False;compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(x,y,z,bound,gate,marker,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(path,memory.writes,writes)
        touched={a for a,_ in writes};counts[path]+=1
    # Проверка переполнения каждого из трёх отношений отдельно, включая особый исходный случай 0/0.
    for options in (
        dict(bound=1,z=0,x=0,y=0),dict(bound=0,z=0,x=1,y=0),dict(bound=0,z=0,x=0,y=1),
        dict(bound=0,z=1,x=0,y=2304),dict(bound=1,z=1,x=1,y=2304)):
        check(**options)
    # Проверка всех сочетаний старших байтов координат и всех пересечений двух масок по отдельным сечениям.
    for a in range(256):
        for b in range(256):check(x=(a<<8)|37,y=(b<<8)|91);check(gate=a,marker=b)
    # Проверка каждого слова допуска, знаменателя и обеих координат по отдельным сечениям.
    for value in range(65536):
        check(bound=value);check(z=value);check(x=value);check(y=value)
    edges=(0,1,255,256,32767,32768,65535)
    for z in edges:
        for bound in edges:
            for x,y in ((0,0),(255,65535),(256,65280),(2304,63232)):check(z=z,bound=bound,x=x,y=y)
    assert set(counts)=={'prepared','y_high_rejected','mask_rejected','x_high_rejected','bound_overflow','x_overflow','y_overflow'}
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),
        method='parent_projection_state_oracle_composed_with_verified_log_ratio_reference',
        independent_complete_child_oracle=False,children_executed_without_stubs=True,
        exact_registers_flags_refresh_sp=True,every_ram_byte_and_write_multiplicity_checked=True,
        all_word_arguments_by_separate_slices=True,all_mask_pairs=True,partial_writes_preserved=True,
        arithmetic_half_of_scaled_ratio_preserved=True,maximum_additional_stack_bytes=2,
        execution_boundary='E299..E30F or E40F, no continuation executed',
        whole_projection_scan_proved=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionProjectedBoundsVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
