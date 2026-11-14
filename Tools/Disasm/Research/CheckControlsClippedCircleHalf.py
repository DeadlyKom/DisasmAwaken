"""Четыре входа отсечённых половин, переход к обычному ядру и исходные выходы с активным EXX."""
from collections import Counter
import json,math,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from ReferenceControlsCircleInteriorFull import evaluate_clipped_half


def profiles():
    for clip in ('left','right'):
        for direction in (-1,1):
            for af in range(65536):
                yield clip,direction,9,0,9 if clip=='left' else 246,0 if direction<0 else 95,0,0x6055,af,af&255,'all_input_AF_vertical_return'
            for threshold in range(256):
                for x in (9,63,255):
                    for curve in (8,127,247):
                        for cy in (0,48,95):yield clip,direction,x,0,curve,cy,threshold,0xFFAA,0xA55A,0xA5,'all_thresholds_at_geometry_edges'
            for x in range(1,256):
                maximum=math.isqrt(65025-x*x)
                for y in sorted({0,1,maximum//2,maximum}):
                    if y>maximum:continue
                    yield clip,direction,x,y,8+(x*73)%240,(x*109+y)%96,(x*13+y)&255,0xA55A,0x1357,y&255,'all_radius_codes_and_y_edges'
    randomizer=random.Random(0xD833)
    for _ in range(4096):
        x=randomizer.randrange(1,256);y=randomizer.randrange(math.isqrt(65025-x*x)+1)
        yield ('left','right')[randomizer.randrange(2)],(-1,1)[randomizer.randrange(2)],x,y,randomizer.randrange(8,248),randomizer.randrange(96),randomizer.randrange(256),randomizer.randrange(65536),randomizer.randrange(65536),randomizer.randrange(256),'mixed_clipped_spans'


def pixel_oracle(clip,direction,x,y,curve,row,threshold,pattern,background,initial_raster=None,end_state=None):
    raster=[background]*3072 if initial_raster is None else list(initial_raster)
    fill=pattern&255;toggle=pattern>>8
    left,right=(7,curve) if clip=='left' else (curve,248);counter=(-x)&255;error=0;rows=0;transitions=0
    def left_byte():return 1 if left==7 else left//8
    def draw():
        nonlocal fill,row,rows
        # Сохранение адреса последнего рисуемого правого края отдельно от последующего переноса строки.
        if end_state is not None:end_state['last_right_low']=(32*row+right//8)&255
        for pixel in range(left+1,right):
            index=row*32+pixel//8;bit=128>>(pixel&7)
            raster[index]=(raster[index]&(~bit&255))|(fill&bit)
        fill^=toggle;row+=direction;rows+=1
        return 0<=row<96
    def difference():
        nonlocal y,error
        previous=y;y=(y+1)&255;error=(error+previous+y)&65535
    def shrink(fast):
        nonlocal left,right,clip,counter,error,transitions
        if clip!='left':
            left+=1
            if left_byte()==right//8:return 'byte_convergence'
        if clip!='right':
            right-=1
            if right//8<1 if clip=='left' else right//8==left_byte():return 'byte_convergence'
        negative_word=counter-256;error=(error+negative_word)&65535;counter=(counter+1)&255
        if fast and counter==0:return 'counter_wrap_fast'
        if clip is not None and counter==threshold:
            previous=clip;clip=None;transitions+=1
            if previous=='left' and right//8==left_byte():return 'left_transition_same_byte'
        error=(error+counter-256)&65535
        return None
    if not draw():reason='vertical'
    else:
        fast=False
        for _ in range(2048):
            if not fast:
                difference()
                if error&32768:
                    if not draw():reason='vertical';break
                    continue
                reason=shrink(False)
                if reason:break
                if error&32768:
                    if not draw():reason='vertical';break
                    continue
                fast=True
            reason=shrink(True)
            if reason:break
            if not error&32768:continue
            difference()
            if not draw():reason='vertical';break
        else:raise AssertionError('скалярный проход не завершился')
    if end_state is not None:end_state.update(error=error,counter=counter,y=y)
    return raster,fill,rows,reason,transitions


def main():
    original=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(original[0x4000:0x8000]),bytearray(original[0x8000:0xC000]),bytearray(original[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(bank) for bank in memory.banks]
    simulator=Simulator(memory);counts=Counter();by_entry=Counter();paths=Counter();touched=set();total_rows=0;transitions=0
    for clip,direction,x,y,curve,cy,threshold,pattern,af,background,kind in profiles():
        serial=counts.total();entry=(0xD1B6 if direction>0 else 0xD1CB) if clip=='left' else (0xD18D if direction>0 else 0xD1A2)
        memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        memory.banks[2][:3072]=bytes([background])*3072;stack=(0x9008,0x9FF0,0xB000,0xBFFE)[serial%4]
        for address,value in ((0xD18C,(serial*73)&255),(stack,255),(stack+1,63)):memory[address]=value
        left,right=(8,curve) if clip=='left' else (curve,248)
        left_address=0x8000+32*cy+left//8;right_address=0x8000+32*cy+right//8
        b=0 if clip=='left' else (255<<(7-(left&7)))&255;c=255 if clip=='right' else 255>>(right&7)
        initial=get_registers({'AF':af,'HL':right_address,'DE':(((serial*13)&255)<<8)|(left_address&255),'BC':b*256+c,
            '^HL':0x1357,'^DE':0xBB00|y,'^BC':0xAA00|((-x)&255),'^AF':(threshold<<8)|((serial*109)&255),
            'IX':pattern,'IY':0x5C3A,'SP':stack,'PC':entry},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate_clipped_half(initial,curve,cy,x,y,direction,clip);wanted=local['registers'];expected=[bytearray(bank) for bank in memory.banks]
        scalar_state={}
        raster,fill,rows,reason,changed=pixel_oracle(clip,direction,x,y,curve,cy,threshold,pattern,background,end_state=scalar_state)
        path=local['paths'][0]
        assert wanted[9]==fill and path['rows']==rows and path['reason']==reason and path['transitions']==changed,(serial,'independent_scalar_geometry',path,rows,reason,changed)
        expected[2][:3072]=bytes(raster)
        for address,value in local['writes']:expected[5 if address<0x8000 else 2 if address<0xC000 else 1][address&0x3FFF]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(200000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('не завершён исходный проход',serial,clip,direction,x,y,curve,threshold))
        memory.recording=False;compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,hex(entry),x,y,curve,cy,threshold,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        # Проверка переставленного набора по независимой причине выхода и состоянию скалярной рекурсии.
        swapped=reason in ('counter_wrap_fast','left_transition_same_byte')
        bc,de,hl=(2,4,6) if swapped else (18,20,22)
        assert simulator.registers[bc:bc+2]==[255,scalar_state['counter']]
        assert simulator.registers[de:de+2]==[0,scalar_state['y']]
        error=scalar_state['error']&65535
        assert simulator.registers[hl:hl+2]==[error>>8,error&255]
        address_d=20 if swapped else 4
        assert simulator.registers[address_d]==scalar_state['last_right_low']
        assert simulator.registers[0:2]==initial[0:2] and simulator.registers[16]==threshold
        assert simulator.registers[9]==(initial[9]^(initial[8] if rows&1 else 0))
        nonpixel=[]
        for bank,offset,value in memory.writes:
            if bank==2 and offset<3072:continue
            assert bank in (1,2,5),(serial,'unexpected_bank',bank)
            nonpixel.append((offset+{1:0xC000,2:0x8000,5:0x4000}[bank],value))
        assert Counter(nonpixel)==Counter(local['writes']),(serial,'nonpixel_writes',Counter(nonpixel)-Counter(local['writes']),Counter(local['writes'])-Counter(nonpixel))
        assert all(a==b for a,b in zip(memory.banks,expected)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17,(serial,'ports')
        touched={(bank,offset) for bank,offset,_ in memory.writes};counts[kind]+=1;by_entry[hex(entry)]+=1;paths[reason]+=1
        total_rows+=rows;transitions+=changed
        if counts.total()%16384==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),cases_by_entry=dict(by_entry),paths=dict(paths),
        modeled_rows=total_rows,transitions_to_unclipped_kernel=transitions,all_256_AFprime_thresholds=True,
        all_input_AF_at_vertical_return_all_four_entries=True,all_radius_codes_and_y_edges=True,
        exact_registers_except_R=True,refresh_R_proved=False,all_physical_ram_bytes_proved=True,
        all_nonpixel_values_and_write_multiplicity_proved=True,independent_scalar_interval_oracle=True,
        original_EXX_active_exit_preserved=True,pixel_write_multiplicity_proved=False,maximum_additional_stack_bytes=6,
        direct_arithmetic_register_set_and_last_drawn_right_low_checked=True,
        no_port_or_page_writes=True,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    (ROOT/'Tools/Disasm/Reports/ControlsClippedCircleHalfVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
