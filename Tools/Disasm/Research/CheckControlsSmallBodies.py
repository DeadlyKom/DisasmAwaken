"""Полный D9DE, независимые симметричные маски, отсечение трёх байтов и точная рамка."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh,cp_flags
from ReferenceControlsPointMotion import block_cost


def rotate(value,count):
    return ((value>>count)|(value<<(8-count)))&255


def reference(memory,radius,mode,mx,my,flags,pattern,initial):
    writes=[]
    def write(address,value):
        address&=65535
        memory[address]=value
        writes.append((address,value))
    wanted=list(initial)
    wanted[SP]=0xC000
    wanted[16:18]=[0xAF,initial[1]]
    m1=block_cost(0xD9DE,0xD9EA)
    if mode>=4:
        wanted[0:2]=[radius,cp_flags(mode,4)]
        return wanted,m1,writes,'mode'
    m1+=block_cost(0xD9EA,0xD9ED)
    if radius>=9:
        wanted[0:2]=[radius,cp_flags(radius,9)]
        return wanted,m1,writes,'large'
    m1+=block_cost(0xD9ED,0xD9F0)
    if radius<2:
        wanted[0:2]=[radius,cp_flags(radius,2)]
        return wanted,m1,writes,'tiny'
    # Получение масок из числовых сдвигов альтернативной затравки, первый байт записывается дважды.
    packed=memory[0xD987+radius]
    transitions=packed&7
    signed=(packed&0xF8)-256
    masks=[(signed>>i)&255 for i in range(transitions)]+[((signed>>transitions)&255)]*radius
    write(0xBFFD,0xD9)
    write(0xBFFC,0xF3)
    for index,value in enumerate(masks):
        write(0xD990+index,value)
    masks[0]=packed&0xF8
    write(0xD990,masks[0])
    m1+=1+21+5*transitions+3*radius
    wanted[16:18]=[radius,cp_flags(radius,2)]
    wanted[4:6]=[0,radius]
    wanted[6:8]=[mx,my]
    wanted[2]=flags
    m1+=block_cost(0xD9F3,0xD9FF)
    if mx>127:
        wanted[0:2]=[0,0x44]
        return wanted,m1+block_cost(0xDA17,0xDA19),writes,'x_reject'
    cx=127+mx if flags&1 else 127-mx
    m1+=block_cost(0xD9FF,0xDA04)+(0 if flags&1 else block_cost(0xDA04,0xDA06))
    clip=int(cx<8)+2*int(cx>=248)
    m1+=block_cost(0xDA06,0xDA0B)+int(cx<8)+block_cost(0xDA0C,0xDA10)+2*int(cx>=248)
    wanted[4]=clip
    wanted[2:4]=[rotate(flags,1),cx]
    m1+=block_cost(0xDA12,0xDA17)
    if my>72:
        wanted[0:2]=[0,0x44]
        return wanted,m1+block_cost(0xDA17,0xDA19),writes,'y_reject'
    cy=48-my if flags&2 else 48+my
    m1+=block_cost(0xDA19,0xDA20)+(block_cost(0xDA20,0xDA22) if flags&2 else 0)
    m1+=block_cost(0xDA22,0xDA43)
    phase=cx&7
    pointer=(0x8000+32*((cy+radius)&255)+cx//8)&65535
    write(0xBFFD,initial[8])
    write(0xBFFC,initial[9])
    fill,toggle=pattern&255,pattern>>8
    last_b=0
    for row in range(2*radius-1):
        ascending=row<radius
        index=row if ascending else 2*radius-2-row
        counter=row if ascending else 2*radius-1-row
        row_flags=0x44 if row==0 else cp_flags(counter,radius) if ascending else 2
        write(0xBFFB,counter)
        write(0xBFFA,row_flags)
        fill^=toggle
        wrapped=(pointer&255)<32
        pointer=(pointer-32)&65535
        h=pointer>>8
        m1+=block_cost(0xDA43,0xDA50)+int(wrapped)+block_cost(0xDA51,0xDA56)
        visible=h<0x60
        if not visible:
            m1+=block_cost(0xDA56,0xDA5A)
            if h<0x8C:
                m1+=block_cost(0xDA5A,0xDA5E)
                visible=h>=0x80
        current_d=clip|(0 if ascending else 0x80)
        if visible:
            write(0xBFF9,h)
            write(0xBFF8,pointer&255)
            # Симметричная 15-битовая фигура и её сдвиг в три соседних пиксельных байта.
            mask=masks[index]
            reverse=int(format(mask,'08b')[::-1],2)
            expanded=((reverse<<8)|((mask<<1)&255))<<(8-phase)
            parts=((expanded>>16)&255,(expanded>>8)&255,expanded&255)
            write(0xBFF8,radius)
            write(0xBFF9,current_d)
            m1+=block_cost(0xDA5E,0xDA64)+8*block_cost(0xDA64,0xDA69)+block_cost(0xDA69,0xDA70)
            m1+=(8-phase)*block_cost(0xDA70,0xDA74)+block_cost(0xDA74,0xDA7B)
            if not clip&1:
                write(0xDA83,parts[0])
                address=pointer-1
                write(address,memory[address]&(~parts[0]&255))
                write(address,memory[address]|(parts[0]&fill))
                m1+=block_cost(0xDA7B,0xDA89)
            write(pointer,memory[pointer]&(~parts[1]&255))
            write(pointer,memory[pointer]|(parts[1]&fill))
            m1+=block_cost(0xDA89,0xDA96)
            if not clip&2:
                address=pointer+1
                write(address,memory[address]&(~parts[2]&255))
                write(address,memory[address]|(parts[2]&fill))
                m1+=block_cost(0xDA96,0xDAA1)
            m1+=block_cost(0xDAA1,0xDAA2)
            last_b=rotate(current_d,2)
        m1+=block_cost(0xDAA2,0xDAA7)
        if ascending:
            m1+=block_cost(0xDAA7,0xDAAD)
            if row==radius-1:
                m1+=block_cost(0xDAAD,0xDAB1)+block_cost(0xDAB1,0xDAB6)
        else:
            m1+=block_cost(0xDAB1,0xDAB6)
    m1+=block_cost(0xDAB6,0xDAB9)
    wanted[0:2]=[0,0x42]
    wanted[2:4]=[last_b,phase]
    wanted[4:6]=[clip|0x80,radius]
    wanted[6:8]=[pointer>>8,pointer&255]
    wanted[10:12]=[toggle,fill]
    return wanted,m1,writes,'draw'


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    touched=set()
    counts,outcomes=Counter(),Counter()
    def check(radius,mode,mx,my,flags,pattern,background,kind):
        nonlocal touched
        memory.recording=False
        for address in touched:
            memory[address]=original[address]
        memory[0x8000:0x8C00]=[background]*3072
        memory[0xD17D:0xD181]=[my,mx,flags,radius]
        memory[0xCEF9]=mode
        memory[0xD240:0xD242]=[pattern&255,pattern>>8]
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD9DE},None,False)
        initial[14],initial[15],initial[26],initial[27]=background,(radius+flags)&255,flags&1,mode%3
        expected=list(memory)
        wanted,m1,writes,outcome=reference(expected,radius,mode,mx,my,flags,pattern,initial)
        wanted[15]=refresh(initial[15],m1)
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for _ in range(2500):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',radius,mode,mx,my,flags))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (radius,mode,mx,my,flags,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (radius,mode,mx,my,flags,outcome)
        touched={a for a,_ in writes}
        counts[kind]+=1
        outcomes[outcome]+=1

    # Проверка совместного поля режима и размера, включая все ранние выходы.
    for mode in range(256):
        for radius in range(256):
            check(radius,mode,0,0,0,0x6055,0xA5,'mode_radius')
    print('Small bodies mode/radius',sum(counts.values()),flush=True)
    # Проверка каждого горизонтального и вертикального смещения во всех четырёх сочетаниях направлений.
    for radius in range(2,9):
        for value in range(256):
            for flags in range(4):
                check(radius,0,value,0,flags,0xFF55,value,'horizontal')
                check(radius,3,0,value,flags,0x60AA,value,'vertical')
    # Проверка сочетаний трёхбайтового отсечения и вертикальных границ.
    for radius in range(2,9):
        for mx in (0,1,6,7,8,120,121,126,127):
            for my in (0,39,40,41,47,48,49,55,56,71,72,73):
                for flags in range(4):
                    check(radius,1,mx,my,flags,0x81A5,(mx+my)&255,'combined_edges')
    # Проверка всех байтов рисунка и чередования на разных радиусах и фазах пикселя.
    for value in range(256):
        check(2+value%7,2,value%128,value%73,value,(value^255)*256+value,value,'patterns')
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),outcomes=dict(outcomes),
        all_mode_radius_pairs=True,all_raw_x_y_offsets=True,all_direction_bits=True,
        all_pattern_low_high_bytes=True,real_mask_builder_without_stubs=True,
        independent_symmetric_pixel_mask_formula=True,all_ram_and_write_multiplicity_checked=True,
        exact_main_alternate_index_flags_r_and_sp=True,whole_d9de_proved_in_original_template_domain=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsSmallBodiesVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
