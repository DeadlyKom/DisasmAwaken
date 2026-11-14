"""D314, все выходные регистры кроме R, полный растр и все непиксельные записи оригинальных детей."""
from collections import Counter
import json,random
from CheckIntro import ROOT
from CheckControlsTextQueue import base_memory
from CheckActionParameterActivation import RecordedBanks
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace
from CheckControlsCircleInterior import half as pixels
from ReferenceControlsCircleInteriorFull import evaluate


def profiles():
    for radius in range(9,120):
        for cy in (0,48,95):yield radius,128,cy,0x6055,0xA5,0,'all_radii'
    for radius in (9,32,96):
        for phase in range(8):
            for cy in range(96):yield radius,128+phase,cy,0xFFAA,phase*31,cy,'all_rows_and_horizontal_phases'
    for value in range(256):
        radius=9+value%15;low=8+radius;cx=low+value%(249-radius-low)
        yield radius,cx,value%96,((value*73)&255)*256+value,value,value,'all_patterns_and_mode_bytes'
    randomizer=random.Random(0xD314)
    for _ in range(2048):
        radius=randomizer.randrange(9,120)
        yield radius,randomizer.randrange(8+radius,249-radius),randomizer.randrange(96),randomizer.randrange(65536),randomizer.randrange(256),randomizer.randrange(256),'mixed_geometry'


def main():
    original=base_memory();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[1]=bytearray(original[0x4000:0x8000]),bytearray(original[0x8000:0xC000]),bytearray(original[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=17);baseline=[bytearray(b) for b in memory.banks]
    simulator=Simulator(memory);touched=set();counts=Counter();paths=Counter();rows=0
    for radius,cx,cy,pattern,background,mode,kind in profiles():
        serial=counts.total();memory.recording=False
        for bank,offset in touched:memory.banks[bank][offset]=baseline[bank][offset]
        for address in range(0x8000,0x8C00):memory[address]=background
        stack=(0x9008,0x9FF0,0xB000,0xBFFE)[serial%4]
        for address,value in ((0xD17F,serial&15),(0xD180,radius),(0xD183,cy),(0xD184,cx),(0xD18C,mode),(stack,255),(stack+1,63)):
            memory[address]=value
        initial=get_registers({'AF':(serial*73)&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,'IX':pattern,'IY':0x5C3A,'SP':stack,'PC':0xD314},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        local=evaluate(initial,cx,cy,radius);wanted=local['registers'];expected=list(original)
        expected[0x8000:0x8C00]=[background]*3072;expected_banks=[bytearray(b) for b in memory.banks]
        fill,up=pixels(expected,cx,cy,radius,-1,pattern&255,pattern>>8)
        fill,down=pixels(expected,cx,cy,radius,1,fill,pattern>>8)
        assert wanted[9]==fill and [p['rows'] for p in local['paths']]==[up,down],(serial,'independent_geometry',local['paths'],up,down)
        expected_banks[2][:3072]=bytes(expected[0x8000:0x8C00])
        for address,value in local['writes']:
            bank=5 if address<0x8000 else 2 if address<0xC000 else 1;expected_banks[bank][address&0x3FFF]=value
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(100000):
            if simulator.registers[24]==0x3FFF:break
            simulator.run()
        else:raise AssertionError(('возврат',serial,radius,cx,cy))
        memory.recording=False
        compared=(*range(15),*range(16,25),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(serial,radius,cx,cy,local['paths'],
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        # Проверка физических Direction и Mode, только направление меняется последней нижней половиной.
        assert memory[0xD18B]==1 and memory[0xD18C]==mode
        left_mask=(255<<(7-((cx-radius)&7)))&255
        assert simulator.registers[0:2]==[left_mask,0x42]
        assert simulator.registers[16:18]==initial[16:18]
        assert simulator.registers[18]==255 and simulator.registers[20]==0
        assert simulator.registers[9]==(initial[9]^(initial[8] if (up+down)&1 else 0))
        actual_nonpixel=[]
        for bank,offset,value in memory.writes:
            if bank==2 and offset<3072:continue
            assert bank in (1,2,5),(serial,'unexpected_bank',bank)
            actual_nonpixel.append((offset+{1:0xC000,2:0x8000,5:0x4000}[bank],value))
        assert Counter(actual_nonpixel)==Counter(local['writes']),(serial,'nonpixel_writes',Counter(actual_nonpixel)-Counter(local['writes']),Counter(local['writes'])-Counter(actual_nonpixel))
        assert all(a==b for a,b in zip(memory.banks,expected_banks)),(serial,'physical_RAM')
        assert not trace.writes and memory.o7ffd==17,(serial,'ports_or_page')
        touched={(b,o) for b,o,_ in memory.writes};counts[kind]+=1;paths.update(p['reason'] for p in local['paths']);rows+=up+down
        if counts.total()%512==0:print(str(counts.total())+' cases passed',flush=True)
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),paths=dict(paths),modeled_rows=rows,
        exact_registers_except_R=True,refresh_R_proved=False,all_physical_ram_bytes_proved=True,no_port_or_page_writes=True,
        all_nonpixel_values_and_write_multiplicity_proved=True,pixel_write_multiplicity_proved=False,
        independent_pixel_interval_oracle=True,independent_second_order_state_oracle=True,
        actual_all_children_executed=True,horizontal_unclipped_domain=True,vertical_clipping_proved=True,
        direct_Direction_one_Mode_preserved_and_saved_AF_checked=True,
        maximum_additional_stack_bytes=8,stack_positions=[0x9008,0x9FF0,0xB000,0xBFFE],complete_domain_product_exhausted=False,
        generic_clipped_kernel_entries_proved=False,whole_large_renderer_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False,timing_proved=False)
    assert counts.total()==4941
    (ROOT/'Tools/Disasm/Reports/ControlsCircleInteriorFullVerification.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
