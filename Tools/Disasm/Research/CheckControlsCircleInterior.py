"""D314, обе половины большого контура без горизонтального отсечения, частичное доказательство."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory


def half(memory,cx,cy,radius,direction,fill,toggle):
    x,y,error=radius,0,0
    rows=0
    while 0<=cy+direction*y<96:
        left,right=cx-x,cx+x
        if left//8>=right//8:
            break
        # Пиксельная модель открытого интервала, не повторение байтовых масок и PUSH оригинала.
        row=cy+direction*y
        for pixel in range(left+1,right):
            address=0x8000+32*row+pixel//8
            bit=128>>(pixel&7)
            memory[address]=(memory[address]&(~bit&255))|(fill&bit)
        rows+=1
        fill^=toggle
        y+=1
        if not 0<=cy+direction*y<96:
            break
        # Независимый второй порядок разности квадратов после перехода на следующую строку.
        error+=2*y-1
        while error>=0:
            x-=1
            if (cx-x)//8>=(cx+x)//8:
                return fill,rows
            error-=2*x+1
    return fill,rows


def main():
    original=base_memory()
    memory=Memory(original)
    simulator=Simulator(memory)
    counts=Counter()
    total_rows=0
    touched=set()
    def check(radius,cx,cy,pattern,background,kind):
        nonlocal touched,total_rows
        assert 9<=radius<=119 and 8<=cx-radius and cx+radius<=248 and 0<=cy<96
        memory.recording=False
        for address in touched:
            memory[address]=original[address]
        memory[0x8000:0x8C00]=[background]*3072
        memory[0xD17F:0xD181]=[0,radius]
        memory[0xD183:0xD185]=[cy,cx]
        memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':pattern,'IY':0x5C3A,'SP':0xBFFE,'PC':0xD314},None,False)
        initial[14],initial[26],initial[27]=background,pattern&1,background%3
        expected=list(memory)
        fill,up_rows=half(expected,cx,cy,radius,-1,pattern&255,pattern>>8)
        fill,down_rows=half(expected,cx,cy,radius,1,fill,pattern>>8)
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for steps in range(100000):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',radius,cx,cy))
        memory.recording=False
        actual=memory[0x8000:0x8C00]
        wanted=expected[0x8000:0x8C00]
        assert actual==wanted, ('пиксели',radius,cx,cy,pattern,[(0x8000+i,a,b) for i,(a,b) in enumerate(zip(actual,wanted)) if a!=b][:12])
        r=simulator.registers
        assert r[0]==((255<<(7-((cx-radius)&7)))&255) and r[1]==0x42
        assert r[8:10]==[pattern>>8,fill] and r[10:12]==initial[10:12]
        assert r[16:18]==initial[16:18] and r[SP]==0xC000 and all(r[i]==initial[i] for i in (14,26,27))
        allowed={0xCEB4,0xD18A,0xD18B,0xD186,0xD187,0xD672,0xD705,0xD716,*range(0xBFF6,0xBFFE),*range(0x8000,0x8C00)}
        assert all(address in allowed for address,_ in memory.writes), sorted({a for a,_ in memory.writes if a not in allowed})
        touched={address for address,_ in memory.writes}
        counts[kind]+=1
        total_rows+=up_rows+down_rows
    # Проверка каждого радиуса в горизонтально помещающемся диапазоне и обоих вертикальных краёв.
    for radius in range(9,120):
        for cy in (0,48,95):
            check(radius,128,cy,0x6055,0xA5,'all_radii')
    print('Circle interior radii',sum(counts.values()),flush=True)
    # Проверка всех пиксельных фаз и смены байта границы на разных радиусах.
    for radius in (9,16,32,64,96,112,119):
        for phase in range(8):
            cx=128+phase
            if cx+radius>248:
                continue
            for cy in (1,47,48,49,94):
                check(radius,cx,cy,0xFFAA,phase*31,'phases')
    # Проверка каждого байта рисунка и XOR-чередования с разными центрами и фонами.
    for value in range(256):
        radius=9+value%15
        low=8+radius
        cx=low+value%(249-radius-low)
        check(radius,cx,value%96,((value*73)&255)*256+value,value,'patterns')
    result=dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),modeled_rows=total_rows,
        root='D314',horizontal_unclipped_domain=True,vertical_clipping_original_helpers=True,
        independent_pixel_intervals_and_second_order_error=True,every_viewport_pixel_checked=True,
        terminal_af_ix_iy_alternate_af_and_sp_checked=True,nonpixel_write_addresses_checked=True,
        nonpixel_values_and_all_output_registers_proved=False,whole_large_renderer_proved=False,
        unknown_status_preserved=True,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleInteriorVerification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
