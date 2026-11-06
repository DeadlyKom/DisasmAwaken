"""D236 до фактического RET либо входа D314/D340, без подмены ReadByteSquare."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckControlsCircleSpan import add_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import cp_flags

BOUNDARIES={0x3FFF,0xD314,0xD340,0xD34A,0xD38C,0xD396,0xD3DA,0xD3E4,0xD404,0xD40E,0xD485}


def evaluate(initial,x,y,radius,bits,pattern=0):
    r=list(initial);writes=[];stack=r[12];a=0;f=0;hl=(r[6]<<8)|r[7];de=(radius<<8)|bits
    def put(address,value):writes.append((address,value))
    def word(address,value):put(address,value&255);put(address+1,value>>8)
    def sub(left,right):return (left-right)&255,sub8_flags(left,right)
    def square(return_address):
        nonlocal de,f
        word(stack-2,return_address);word(stack-4,hl);de=a*a;f=0x80|(f&1)
    def difference():
        nonlocal hl,f
        borrow=f&1;wide=hl-de-borrow;result=wide&65535
        f=((result>>8)&0xA8)|(64 if not result else 0)|2|int(wide<0)
        f|=16 if (hl&4095)<(de&4095)+borrow else 0
        f|=4 if (hl^de)&(hl^result)&32768 else 0
        hl=result
    def restore_square():
        nonlocal hl,f
        wide=hl+de;result=wide&65535
        f=(f&0xC4)|((result>>8)&0x28)|int(wide>65535)
        f|=16 if (hl&4095)+(de&4095)>4095 else 0;hl=result
    def bit_flags(mask,carry):return (bits&0x28)|16|carry|(0 if bits&mask else 68)
    def finish(target,kind):
        r[0:8]=[a,f,x,y,de>>8,de&255,hl>>8,hl&255]
        r[8:10]=[pattern>>8,pattern&255];r[12]=stack+2 if target==0x3FFF else stack;r[24]=target
        return r,writes,kind

    # Вычисление исходного рабочего смещения и центров по знакам, сложение идёт по модулю байта.
    word(0xD181,(x<<8)|y);put(0xD183,(48+(-y if bits&2 else y))&255);put(0xD184,(128+(x if bits&1 else -x))&255)
    x_valid=bool(bits&4);y_valid=bool(bits&8);x_small=x<120;y_small=y<48
    a,f=x,bit_flags(4,int(x_small));r[16:18]=[y,bit_flags(8,int(y_small))]
    if not x_valid and not x_small:return finish(0x3FFF,'reject_horizontal_gate')
    # Ветви после второго EX AF используют проверку Y, горизонтальная проверка остаётся в AFprime.
    a,r[16]=r[16],a;f,r[17]=r[17],f
    if not y_valid and not y_small:return finish(0x3FFF,'reject_vertical_gate')
    if x_valid and x_small and y_valid and y_small:
        # Разделение полного внутреннего круга и горизонтальных отсечений по двум исходным сравнениям.
        if x+radius<120:
            a=x+radius;f=cp_flags(a,120);return finish(0xD314,'whole_interior')
        a,f=sub(radius,x)
        if not f&1:f=cp_flags(a,120)
        return finish(0xD3E4,'single_horizontal_edge') if f&1 else finish(0xD34A,'both_horizontal_edges')
    if not (x_valid and x_small) and y_valid and y_small:
        # Горизонтальная ветвь с изменённым рабочим X, нулевая ширина отбрасывается.
        x=(x-120)&255;put(0xD182,x);a,f=sub(radius,x)
        if f&0x41:return finish(0x3FFF,'reject_outside_x_extent')
        a,f=sub(a,240)
        return finish(0xD340,'outside_x_full_width') if not f&1 else finish(0xD3DA,'outside_x_one_edge')
    if x_valid and x_small:
        # Вертикальная ветвь вычисляет остаток R²−Y² и сравнивает его с квадратами двух горизонтальных границ.
        y=(y-48)&255;put(0xD181,y);a,f=sub(radius,y)
        if f&1:return finish(0x3FFF,'reject_outside_y_extent')
        a=radius;square(0xD2B8);hl=de;a=y;square(0xD2BE);difference()
        a,f=sub(120,x);square(0xD2C6);difference()
        if f&1:return finish(0xD485,'vertical_unclipped_slice')
        restore_square();a=(120+x)&255;f=add_flags(120,x);square(0xD2D2);difference()
        return finish(0xD396,'vertical_full_width') if not f&1 else finish(0xD40E,'vertical_single_edge')
    # Угловая ветвь оставляет Carry вычитания Y−48 для первого SBC квадратов.
    x=(x-120)&255;y,f=sub(y,48);word(0xD181,(x<<8)|y)
    a=radius;square(0xD2EA);hl=de;a=y;square(0xD2F0);difference()
    if f&1:return finish(0x3FFF,'reject_corner_vertical_square')
    a=x;square(0xD2F7);difference()
    if f&1:return finish(0x3FFF,'reject_corner_horizontal_square')
    restore_square();a=(x+248)&255;f=add_flags(x,248)
    if not f&1:
        square(0xD303);difference()
        if not f&1:return finish(0xD38C,'corner_full_width')
    return finish(0xD404,'corner_single_edge')


def profiles():
    # Проверка всех байтов X/Y и четырёх сочетаний флагов допуска отношения.
    for bits in (0,4,8,12):
        for x in range(256):
            for y in range(256):yield x,y,(x*73+y*109)&255,bits|((x^y)&3),'all_coordinates_and_validity_bits'
    # Проверка всех радиусов на порогах байтовой геометрии, включая обе стороны центра.
    for bits in range(16):
        for x,y in ((0,0),(119,47),(120,48),(121,49),(127,95),(128,96),(247,254),(248,255),(255,255)):
            for radius in range(256):yield x,y,radius,bits,'all_radii_on_geometry_edges'
    randomizer=random.Random(0xD236)
    for _ in range(8192):yield *(randomizer.randrange(256) for _ in range(4)),'mixed_full_flag_bytes'


def main():
    flat=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(bank) for bank in memory.banks]
    simulator=Simulator(memory);touched=set();counts=Counter();paths=Counter();targets=set()
    for x,y,radius,bits,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        stack=(0x9008,0xBFFE)[serial&1];setup={0xD17D:y,0xD17E:x,0xD17F:bits,0xD180:radius,stack:255,stack+1:63}
        for address,value in setup.items():memory[address]=value
        touched={(1 if address>=0xC000 else 2,address&0x3FFF) for address in setup}
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':0xABCD,'IY':0x5C3A,'SP':stack,'PC':0xD236},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted,writes,path=evaluate(initial,x,y,radius,bits)
        expected=[(1 if address>=0xC000 else 2,address&0x3FFF,value) for address,value in writes]
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(150):
            if simulator.registers[24] in BOUNDARIES:break
            simulator.run()
        else:raise AssertionError(('no_boundary',serial,x,y,radius,bits))
        memory.recording=False;compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,x,y,radius,bits,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert Counter(memory.writes)==Counter(expected),(serial,'write_multiplicity',writes,memory.writes)
        final=dict(setup);final.update(writes)
        assert all(memory[address]==value for address,value in final.items()),(serial,'RAM_values')
        assert not trace.writes and memory.o7ffd==17
        touched.update((bank,offset) for bank,offset,_ in expected);counts[kind]+=1;paths[path]+=1;targets.add(wanted[24])
        if counts.total()%65536==0:print(str(counts.total())+' cases passed',flush=True)
    assert targets==BOUNDARIES,(targets,BOUNDARIES-targets)
    for address,value in final.items():baseline[1 if address>=0xC000 else 2][address&0x3FFF]=value
    assert all(a==b for a,b in zip(baseline,memory.banks))
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),
        all_original_branch_destinations_observed=True,targets=[format(target,'04X') for target in sorted(targets)],
        exact_registers_except_R=True,all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,
        actual_read_byte_square_without_stubs=True,maximum_additional_stack_bytes=4,stopped_before_raster_children=True,
        whole_renderer_proved=False,complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsCircleDispatchVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
