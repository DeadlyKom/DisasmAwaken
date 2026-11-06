"""D485, вертикальное сечение без горизонтального отсечения и исходный касательный выход."""
from collections import Counter
from math import isqrt
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckControlsCircleSpan import add_flags
from CheckControlsCircleHalf import pixel_half
from ReferenceControlsCircleInteriorFull import evaluate_half


def profiles():
    # Проверка всех центров и рабочих смещений на касании, обе вертикальные границы и оба знака X.
    for x in range(120):
        for y in range(9,256):
            for signs in range(4):yield x,y,y,0x0C|signs,0xA55A,'all_tangent_centers_and_offsets'
    # Проверка каждой допустимой пары радиуса и Y при ненулевой разности квадратов, X достигает границы допуска.
    for radius in range(9,256):
        for y in range(radius):
            difference=radius*radius-y*y
            if difference<14400:
                x=119-isqrt(difference);bits=0x0C|((radius+y)&3)
                yield x,y,radius,bits,(radius*109+y*73)&65535,'all_nonzero_slice_radius_offset_pairs'
    randomizer=random.Random(0xD485)
    for _ in range(4096):
        radius=randomizer.randrange(9,256);y=randomizer.randrange(radius+1);difference=radius*radius-y*y
        if difference>=14400:y=radius-1;difference=radius*radius-y*y
        x=randomizer.randrange(120-isqrt(difference))
        yield x,y,radius,randomizer.randrange(256),randomizer.randrange(65536),'mixed_slices'


def append_root_frame(word, stack, return_address, hl, de, bc, index, flags):
    radius = de >> 8
    difference = (radius * radius - index * index - (flags & 1)) & 65535
    word(stack - 2, return_address)
    word(stack - 4, bc)
    word(stack - 6, de)
    word(stack - 8, hl)
    word(stack - 10, (index << 8) | flags)
    word(stack - 12, 0xD611)
    word(stack - 14, hl)
    word(stack - 10, 0xD617)
    word(stack - 12, radius * radius)
    word(0xD188, difference)
    for _ in range(8):
        word(stack - 10, 0xD626)
        word(stack - 12, difference)
    return isqrt(difference)


def reference(initial,x,y,radius,bits,cx,background):
    r=list(initial);stack=r[12];writes=[]
    def put(address,value):writes.append((address,value))
    def word(address,value):put(address,value&255);put(address+1,value>>8)
    def pair(index):return (r[index]<<8)|r[index+1]
    root=append_root_frame(word,stack,0xD48D,pair(6),(radius<<8)|bits,pair(2),y,r[1])
    put(0xD185,root)
    direction=1 if bits&2 else -1;row=0 if direction>0 else 95;put(0xD183,row)
    left=(cx-root)&255;right=(cx+root)&255
    left_address=0x8000+32*row+left//8;right_address=0x8000+32*row+right//8
    left_mask=(255<<(7-(left&7)))&255;right_mask=255>>(right&7)
    # Два построителя масок, правый временно сохраняет AF и записывает левую маску в SavedB.
    word(stack-2,0xD4B0);word(stack-2,0xD4BF);word(stack-4,(right<<8)|add_flags(cx,root));put(0xD18A,left_mask)
    flags=16|(bits&0x28)|(0 if bits&2 else 68)
    r[0:8]=[bits,flags,left_mask,right_mask,radius,left_address&255,right_address>>8,right_address&255]
    r[19],r[21]=(-root)&255,y
    word(stack-2,0xD4C7 if direction>0 else 0xD4CA)
    r[12]=stack-2;raster=[background]*3072
    if root==255:
        # Касание даёт обёрнутый радиус FF, левый байт не меньше правого и ядро возвращается до SavedSP.
        assert radius==y and left_address>=right_address
        word(stack-4,(bits<<8)|flags);put(0xD18B,int(direction>0))
        r[18],r[20],r[22],r[23]=255,0,0,0;rows=0
    else:
        local=evaluate_half(r,cx,row,root,y,direction);r=local['registers'];writes.extend(local['writes'])
        fill,rows=pixel_half(raster,cx,row,root,y,direction,initial[9],initial[8])
        assert r[9]==fill and local['paths'][0]['rows']==rows
    r[12],r[24]=stack+2,0x3FFF
    return r,writes,raster,rows,root


def main():
    flat=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(bank) for bank in memory.banks]
    simulator=Simulator(memory);touched=set();counts=Counter();roots=Counter();total_rows=0
    for x,y,radius,bits,pattern,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        stack=(0x9008,0xBFFE)[serial&1];cx=128+(x if bits&1 else -x);background=serial&255
        memory.banks[2][:3072]=bytes([background])*3072
        for address,value in ((0xD17F,bits),(0xD180,radius),(0xD184,cx),(0xD18C,(serial*109)&255),(stack,255),(stack+1,63)):
            memory[address]=value
        initial=get_registers({'AF':((serial*73)&65535)|1,'HL':0x1357,'DE':0x2468,'BC':(x<<8)|y,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':pattern,'IY':0x5C3A,'SP':stack,'PC':0xD485},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,raster,rows,root=reference(initial,x,y,radius,bits,cx,background)
        expected=[bytearray(bank) for bank in memory.banks];expected[2][:3072]=bytes(raster)
        nonpixel=[]
        for address,value in writes:
            bank=1 if address>=0xC000 else 2;offset=address&0x3FFF
            expected[bank][offset]=value;nonpixel.append((bank,offset,value))
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        simulator.run(start=0xD485,stop=0x3FFF);memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,x,y,radius,bits,root,rows,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        actual=[item for item in memory.writes if item[0]!=2 or item[1]>=3072]
        assert Counter(actual)==Counter(nonpixel),(serial,'nonpixel',Counter(actual)-Counter(nonpixel),Counter(nonpixel)-Counter(actual))
        assert all(a==b for a,b in zip(expected,memory.banks)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17
        assert min(offset for bank,offset,_ in nonpixel if bank==2)==((stack-14)&0x3FFF)
        if root==255:assert len(actual)==len(memory.writes)
        touched={(bank,offset) for bank,offset,_ in memory.writes};counts[kind]+=1;roots[root]+=1;total_rows+=rows
        if counts.total()%32768==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),modeled_rows=total_rows,
        tangent_root_FF_cases=roots[255],tangent_draws_no_pixels=True,tangent_saved_SP_unchanged=True,
        exact_registers_except_R=True,all_physical_ram_bytes_proved=True,nonpixel_write_multiplicity_proved=True,
        actual_sqrt_masks_and_raster_children_without_stubs=True,maximum_additional_stack_bytes=14,
        full_D340_proved=False,complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsVerticalCircleSliceVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
