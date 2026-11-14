"""Пиксели и физические записи DDF0, режимы AND/OR/XOR, настоящий временный SP=32."""
from collections import Counter
import json,random
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckActionVertexCodes import logic_flags
from ReferenceControlsBufferPoints import sub8_flags
from ReferenceControlsPointRespawn import refresh
from PreviewModelMatrixOracle import arithmetic
from CheckMarketAccess import add16_flags

MODES=((0xA1,0x30,0x18,'and'),(0xB1,0x38,0x10,'or'),(0xA9,0x38,0x10,'xor'))


def raster(first,second,opcode,branch,table,memory,packed_entry=False):
    writes=[]
    if first==second and not packed_entry:return dict(writes=writes,degenerate=True,refresh_m1=7)
    x,y=first;end_x,end_y=second
    swapped=end_y<y
    if swapped:x,y,end_x,end_y=end_x,end_y,x,y
    dx=abs(end_x-x);dy=end_y-y;direction=1 if end_x>x else -1
    steep=dx<dy;major,minor=(dy,dx) if steep else (dx,dy)
    error=major//2;address=0x8000+y*32+x//8;mask=table[x&7]
    error_flags=logic_flags(error)|(major&1)
    pixel_flags=0;accumulator=0;row_steps=0;byte_steps=0;last_row=False;last_cross=False
    def value(a):return memory[a-0x8000]
    def write(a,v):memory[a-0x8000]=v;writes.append((2,a-0x8000,v))
    def apply(a):return a&mask if opcode==0xA1 else a|mask if opcode==0xB1 else a^mask
    def advance(mask):
        carry=(mask>>7)&1 if direction<0 else mask&1
        new=((mask<<1)|(mask>>7))&255 if direction<0 else ((mask>>1)|(mask<<7))&255
        return new,bool(carry) if branch==0x38 else not carry,logic_flags(new)|carry
    def move_byte_flags(address,flags):
        old=address&255;new=(old+direction)&255
        half=(old&15)==(15 if direction>0 else 0)
        overflow=old==(127 if direction>0 else 128)
        return (new&0xA8)|(64 if new==0 else 0)|(16 if half else 0)|(4 if overflow else 0)|(2 if direction<0 else 0)|(flags&1)
    if steep:
        for _ in range(major):
            last_cross=False
            accumulator=apply(value(address));pixel_flags=logic_flags(accumulator)|(16 if opcode==0xA1 else 0)
            write(address,accumulator);pixel_flags=add16_flags(address,32,pixel_flags);address+=32
            error_flags=sub8_flags(error,minor);error-=minor
            if error<0:
                _,error_flags=arithmetic(error&255,major);error+=major;mask,cross,error_flags=advance(mask)
                row_steps+=1
                if cross:
                    error_flags=move_byte_flags(address,error_flags);address+=direction;byte_steps+=1;last_cross=True
    else:
        accumulator=value(address)
        iterations=major if major else 256
        for i in range(iterations):
            last_row=False
            accumulator=apply(accumulator);mask,cross,pixel_flags=advance(mask)
            if cross:
                byte_steps+=1
                write(address,accumulator);pixel_flags=move_byte_flags(address,pixel_flags);address+=direction;accumulator=value(address)
            error_flags=sub8_flags(error,minor);error-=minor
            if error<0:
                row_steps+=1;last_row=True
                _,error_flags=arithmetic(error&255,major);error+=major;write(address,accumulator)
                pixel_flags=add16_flags(address,32,pixel_flags);address+=32;accumulator=value(address)
            elif i==iterations-1:write(address,accumulator)
    # Расчёт M1 по геометрии, нормализации, числу коррекций ошибки и переносов маски.
    # Префикс включает две M1 для ED/CB, но не стоимость тактов T.
    prefix=(0 if packed_entry else 8)+3+3+3*swapped+26+(2 if direction<0 else 4)+(10 if steep else 11)
    if steep:
        m1=prefix+9*major+4*row_steps+byte_steps+2+(0 if direction>0 and last_cross else 1)
    else:
        m1=prefix+9*iterations+4*row_steps+4*byte_steps+2+(1 if last_row else 2)
    patch=(0xDE72,0xDE7C) if steep and direction<0 else (0xDED6,0xDEE0) if steep else (0xDE3F,0xDE42) if direction<0 else (0xDEA3,0xDEA6)
    return dict(writes=writes,degenerate=False,hl=address,bc=mask,de=major*256+minor,patch=patch,steep=steep,direction=direction,
        af=(accumulator,pixel_flags),alt_af=(error,error_flags),refresh_m1=m1)


def main():
    flat=flat_action();assert bytes(flat[0xE010:0xE020])==bytes((128,64,32,16,8,4,2,1,127,191,223,239,247,251,253,254))
    base=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    base[5],base[2],base[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    for i in range(3072):base[2][i]=(i*73+(i>>5)*19+0x5A)&255
    memory=RecordedBanks(banks=[bytearray(b) for b in base],out7ffd=16);simulator=Simulator(memory);touched=set();counts=Counter();paths=Counter();m1_counts=Counter();initial_refresh_values=set()
    def check(first,second,mode):
        nonlocal touched
        memory.recording=False
        for bank,index in touched:memory.banks[bank][index]=base[bank][index]
        opcode,branch,offset,name=mode
        for address,(x,y) in ((0x8D2A,first),(0x8D2C,second)):memory[address],memory[address+1]=x,y
        memory[0x8D4E],memory[0x8D4F],memory[0xDE0F]=opcode,branch,offset
        memory[0xBFFE],memory[0xBFFF]=255,63
        initial=get_registers({'AF':counts.total()&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,'IX':0xABCD,'IY':0x5C3A,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xDDF0},None,False)
        initial[14],initial[15],initial[26],initial[27]=counts.total()&255,(counts.total()*73)&255,counts.total()&1,counts.total()%3
        initial_refresh_values.add(initial[15])
        expected=[bytearray(b) for b in memory.banks]
        result=raster(first,second,opcode,branch,flat[0xE000+offset:0xE008+offset],expected[2]);writes=list(result['writes'])
        if not result['degenerate']:
            for address,value in ((0xDEED,0xFE),(0xDEEE,0xBF),(result['patch'][0],opcode),(result['patch'][1],branch)):
                expected[0][address-0xC000]=value;writes.append((0,address-0xC000,value))
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;measured_m1=0
        for _ in range(8000):
            if simulator.registers[PC]==0x3FFF:break
            before_r=simulator.registers[15]
            simulator.run()
            increment=(simulator.registers[15]-before_r)&127
            assert increment in (1,2),(hex(simulator.registers[PC]),increment)
            measured_m1+=increment
        else:raise AssertionError('возврат рисователя')
        memory.recording=False
        assert all(a==b for a,b in zip(expected,memory.banks)),(first,second,name,'RAM')
        assert Counter(writes)==Counter(memory.writes),(first,second,name,'writes',Counter(writes)-Counter(memory.writes),Counter(memory.writes)-Counter(writes))
        registers=simulator.registers
        assert measured_m1==result['refresh_m1'],(first,second,name,'full M1',measured_m1,result['refresh_m1'])
        assert registers[15]==refresh(initial[15],result['refresh_m1']),(first,second,name,'R')
        m1_counts[measured_m1]+=1
        assert registers[SP]==0xC000 and registers[8:12]==initial[8:12] and registers[18:24]==initial[18:24]
        assert all(registers[i]==initial[i] for i in (14,26,27))
        if result['degenerate']:
            assert registers[0:2]==[initial[0],0x42] and registers[6:8]==[0,0] and registers[2:4]==initial[2:4]
            assert registers[4:6]==[second[1],second[0]] and registers[16:18]==initial[16:18]
            paths['equal_no_pixels']+=1
        else:
            for position,key in ((2,'bc'),(4,'de'),(6,'hl')):assert registers[position]*256+registers[position+1]==result[key],(first,second,name,key,result[key],registers[position:position+2])
            assert tuple(registers[0:2])==result['af'] and tuple(registers[16:18])==result['alt_af'],(first,second,name,'AF',result['af'],registers[0:2],result['alt_af'],registers[16:18])
            paths[('steep' if result['steep'] else 'shallow')+('_right' if result['direction']>0 else '_left')]+=1
        touched={(bank,index) for bank,index,value in memory.writes};counts[name]+=1
    # Проверка границ байтов, обоих направлений и равенства при разных исходных фазах пикселя.
    points=[(x,y) for x in (0,1,7,8,127,128,254,255) for y in (0,1,47,48,94,95)]
    for mode in MODES:
        for first in points:
            for second in points:check(first,second,mode)
        # Полные пары вертикальных координат и все горизонтальные длины против крайних концов.
        for first_y in range(96):
            for second_y in range(96):check((127,first_y),(127,second_y),mode)
        for first_x in range(256):
            for last_x in (0,255):
                for y in (0,95):check((first_x,y),(last_x,y),mode)
        rng=random.Random(0xDDF0+mode[0])
        for _ in range(4096):check((rng.randrange(256),rng.randrange(96)),(rng.randrange(256),rng.randrange(96)),mode)
    viewport_cases=counts.total()
    # Проверка обнаруженного соседнего профиля, фактический код не ограничивает First высотой 96.
    # Здесь пиксели могут изменить рабочие поля 8D и таблицы 8E/8F, их байты также сравниваются.
    for mode in MODES:
        rng=random.Random(0x8D00+mode[0])
        for _ in range(2048):check((rng.randrange(256),rng.randrange(256)),(rng.randrange(256),rng.randrange(256)),mode)
    assert initial_refresh_values==set(range(256))
    report=dict(passed=True,total_cases=counts.total(),modes=dict(counts),paths=dict(paths),
        viewport_0_to_95_cases=viewport_cases,extended_0_to_255_cases=counts.total()-viewport_cases,
        extended_profile_game_admissibility_proved=False,extended_profile_workspace_pixel_writes_preserved=True,
        all_physical_ram_bytes_proved=True,write_multiplicity_proved=True,patched_instruction_bytes_checked=True,
        linear_buffer_32_byte_rows=True,final_endpoint_excluded=True,equal_points_write_no_pixels=True,
        BC_DE_HL_SP_and_preserved_registers_checked=True,all_AF_and_alternate_AF_proved=True,
        refresh_and_timing_independently_checked=False,exact_refresh_R_checked=True,
        full_M1_count_compared_not_only_R_modulo_128=True,all_256_initial_R_values=True,
        observed_M1_min=min(m1_counts),observed_M1_max=max(m1_counts),
        exact_T_checked=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionLineRasterVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
