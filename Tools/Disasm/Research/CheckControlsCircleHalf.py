"""D1DF/D1F4, каноническое внутреннее сечение с произвольным допустимым начальным Y и AF."""
from collections import Counter
import json,math,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsCircleInteriorFull import evaluate_half


def profiles():
    for direction in (-1,1):
        for x in range(128):
            for y in range(256):
                if x*x+y*y>255*255:continue
                yield direction,x,y,127+(y&1),(x*73+y)%96,0xFFAA,(x*109+y)&65535,y,'all_valid_x_y_pairs'
        for af in range(65536):yield direction,1,min(af>>8,254),128,af%96,0x6055,af,af&255,'all_input_AF'
        for x in (0,1,4,9,32,64,119,127):
            for phase in range(8):
                cx=128+phase
                if cx+x>255:continue
                for cy in (0,1,48,94,95):yield direction,x,0,cx,cy,0xA55A,0x1357,phase*31,'horizontal_phases_and_vertical_edges'
        for value in range(256):yield direction,9,value%31,128+value%8,value%96,((value*73)&255)*256+value,0xA55A,value,'all_patterns_and_modes'
    randomizer=random.Random(0xD1DF)
    for _ in range(4096):
        x=randomizer.randrange(128);y=randomizer.randrange(math.isqrt(65025-x*x)+1)
        yield (-1,1)[randomizer.randrange(2)],x,y,randomizer.randrange(x,256-x),randomizer.randrange(96),randomizer.randrange(65536),randomizer.randrange(65536),randomizer.randrange(256),'mixed_arcs'


def pixel_half(memory,cx,row,x,y,direction,fill,toggle):
    error=0;rows=0
    while 0<=row<96:
        left,right=cx-x,cx+x
        if left//8>=right//8:break
        for pixel in range(left+1,right):
            index=32*row+pixel//8;bit=128>>(pixel&7)
            memory[index]=(memory[index]&(~bit&255))|(fill&bit)
        fill^=toggle;rows+=1;row+=direction
        if not 0<=row<96:break
        previous=y;y=(y+1)&255;error+=previous+y
        while error>=0:
            x-=1
            if (cx-x)//8>=(cx+x)//8:return fill,rows
            error-=2*x+1
    return fill,rows


def main():
    original=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(original[0x4000:0x8000]),bytearray(original[0x8000:0xC000]),bytearray(original[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);touched=set();counts=Counter();by_entry=Counter();paths=Counter();total_rows=0
    for direction,x,y,cx,cy,pattern,af,background,kind in profiles():
        serial=counts.total();entry=0xD1F4 if direction<0 else 0xD1DF;memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        memory.banks[2][:3072]=bytes([background])*3072;stack=(0x9008,0x9FF0,0xB000,0xBFFE)[serial%4]
        for address,value in ((0xD18C,(serial*73)&255),(stack,255),(stack+1,63)):memory[address]=value
        left,right=cx-x,cx+x;left_address=0x8000+32*cy+left//8;right_address=0x8000+32*cy+right//8
        b=(255<<(7-(left&7)))&255;c=255>>(right&7)
        initial=get_registers({'AF':af,'HL':right_address,'DE':(((serial*13)&255)<<8)|(left_address&255),'BC':b*256+c,
            '^HL':0x1357,'^DE':0xBB00|y,'^BC':0xAA00|((-x)&255),'^AF':(serial*109)&65535,
            'IX':pattern,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate_half(initial,cx,cy,x,y,direction);wanted=local['registers'];expected_banks=[bytearray(bank) for bank in memory.banks]
        raster=[background]*3072;fill,rows=pixel_half(raster,cx,cy,x,y,direction,pattern&255,pattern>>8)
        assert wanted[9]==fill and local['paths'][0]['rows']==rows,(serial,'geometry',local['paths'],rows)
        expected_banks[2][:3072]=bytes(raster)
        for address,value in local['writes']:expected_banks[5 if address<0x8000 else 2 if address<0xC000 else 1][address&0x3FFF]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=entry,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,hex(entry),x,y,cx,cy,local['paths'],
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        nonpixel=[]
        for bank,offset,value in memory.writes:
            if bank==2 and offset<3072:continue
            assert bank in (1,2,5),(serial,'unexpected_bank',bank)
            nonpixel.append((offset+{1:0xC000,2:0x8000,5:0x4000}[bank],value))
        assert Counter(nonpixel)==Counter(local['writes']),(serial,'nonpixel_writes',Counter(nonpixel)-Counter(local['writes']),Counter(local['writes'])-Counter(nonpixel))
        assert all(a==b for a,b in zip(memory.banks,expected_banks)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17,(serial,'ports')
        touched={(bank,offset) for bank,offset,_ in memory.writes};counts[kind]+=1;by_entry[hex(entry)]+=1;paths[local['paths'][0]['reason']]+=1;total_rows+=rows
        if counts.total()%16384==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(by_entry),paths=dict(paths),modeled_rows=total_rows,
        all_valid_x_y_pairs_both_directions=True,initial_norm_upper_bound=65025,initial_x_range=[0,127],initial_y_range=[0,255],
        all_input_AF_both_directions=True,exact_registers_except_R=True,refresh_R_proved=False,
        all_physical_ram_bytes_proved=True,all_nonpixel_values_and_write_multiplicity_proved=True,
        independent_pixel_intervals_and_second_order_error=True,pixel_write_multiplicity_proved=False,
        initial_same_byte_exit_preserved=True,maximum_additional_stack_bytes=6,no_port_or_page_writes=True,
        complete_coordinate_pattern_product_exhausted=False,noncanonical_spans_proved=False,
        horizontal_clipping_kernels_proved=False,assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleHalfVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
