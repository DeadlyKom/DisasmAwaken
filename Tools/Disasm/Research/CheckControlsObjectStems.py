"""Вертикальные линии E553, отсечение и выбор продолжения, без самого значка."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC
from CheckMusicGateTicks import Memory, xor_flags
from ReferenceControlsPointRespawn import refresh, cp_flags
from ReferenceControlsBufferPoints import sub8_flags
from CheckControlsCircleSpan import add_flags
from ReferenceControlsPointMotion import block_cost
from CheckControlsRasterBackground import pixel_address


def advance(x, y, direction):
    address = pixel_address(x,y)
    high, low = address >> 8, address & 255
    if direction > 0:
        high = (high+1)&255
        if high & 7:
            return high&7, xor_flags(high&7)|0x10, 0
        if low+32 > 255:
            return (low+32)&255, add_flags(low,32), 4
        return (high-8)&255, sub8_flags(high,8), 7
    if high & 7:
        return high&7, xor_flags(high&7)|0x10, 0
    if low < 32:
        return (low-32)&255, sub8_flags(low,32), 4
    return (high+7)&255, add_flags((high-1)&255,8), 7


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    counts = Counter()

    def check(x,y,raw,serial):
        nonlocal touched
        memory.recording = False
        for address in touched:
            memory[address] = original[address]
        address, mask = pixel_address(x,y), 128 >> (x&7)
        initial = get_registers({'AF': 0xA55A, 'HL': 0x1357, 'DE': 0x4000|x,
            'BC': raw*256+y, '^AF': 0xDEF0, '^HL': 0xE685+(x&7), '^DE': address,
            '^BC': mask, 'IX': 0xA100, 'IY': 0x5C3A, 'SP': 0xBFFE, 'PC': 0xE553}, None, False)
        initial[14],initial[15],initial[26],initial[27] = serial&255,serial&255,serial&1,serial%3
        height = (raw if raw<128 else raw-256)//4
        wanted = list(initial)
        wanted[2:8] = [0,mask,address >> 8,address & 255,0xE6,0x85+(x&7)]
        wanted[18:24] = [raw,y,0x40,x,0x13,0x57]
        wanted[PC] = 0xE5E5
        writes=[]
        m1=block_cost(0xE553,0xE55C)
        if not height:
            path='zero'
            wanted[0:2]=[0,0x44|((raw>>1)&1)]
        else:
            direction=1 if height>0 else -1
            length=abs(height)
            m1+=block_cost(0xE55C,0xE55F)
            if height>0:
                m1+=block_cost(0xE5B5,0xE5BE)
                if y+length<181:
                    path='down_inside'
                    stored_a,stored_f=y+length,cp_flags(y+length,181)
                else:
                    path='down_clipped'
                    length=181-y
                    stored_a,stored_f=length,xor_flags(length)|0x10
                    wanted[PC]=0xE4B7
                    m1+=block_cost(0xE5BE,0xE5CA)
            else:
                m1+=block_cost(0xE55F,0xE56B)
                if y-length>=107:
                    path='up_inside'
                    stored_a=y-length
                    old_f=cp_flags(stored_a,107)
                    stored_f=(old_f&0xC4)|(stored_a&0x28)|1
                else:
                    path='up_clipped'
                    length=y-107
                    stored_a,stored_f=length,xor_flags(length)|0x10
                    m1+=block_cost(0xE56B,0xE576)
                    if length:
                        wanted[PC]=0xE4B7
            if length:
                m1+=1
                for offset in range(length):
                    row=y+direction*offset
                    location=pixel_address(x,row)
                    writes.append((location,memory[location]|mask))
                    a,f,extra=advance(x,row,direction)
                    m1+=8+extra
                final_y=y+direction*length
                if direction<0:
                    for _ in range(2):
                        a,f,extra=advance(x,final_y,-1)
                        final_y-=1
                        m1+=4+extra
                    a=pixel_address(x,final_y)>>8
                    m1+=2
                m1+=2
                final_address=pixel_address(x,final_y)
                wanted[4:6]=[final_address >> 8,final_address & 255]
                wanted[16:18]=[a,f]
            wanted[0:2]=[stored_a,stored_f]
        wanted[15]=refresh(initial[15],m1)
        expected=list(memory)
        for location,value in writes:
            expected[location]=value
        simulator.registers[:]=initial
        memory.writes=[]
        memory.recording=True
        for _ in range(650):
            if simulator.registers[PC]==wanted[PC]:
                break
            simulator.run()
        else:
            raise AssertionError(('граница',x,y,raw))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(x,y,raw,path,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes),(x,y,raw,path)
        touched={location for location,_ in writes}
        counts[path]+=1

    # Проверка всех высот и исходных Y с обеими крайними фазами пиксельной маски.
    for x in (64,71):
        for y in range(107,181):
            for raw in range(256):
                check(x,y,raw,counts.total())
    # Проверка остальных фаз на верхней, нижней границе и границах экранных знакомест.
    for x in range(65,71):
        for y in (107,111,112,127,128,175,180):
            for raw in range(256):
                check(x,y,raw,counts.total())
    report=dict(passed=True,total_cases=counts.total(),cases_by_path=dict(counts),
        all_height_bytes_and_allowed_y=True,all_pixel_phases=True,
        exact_registers_flags_refresh_sp_and_branch_target=True,every_ram_byte_and_write_checked=True,
        no_stack_writes=True,full_e291_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsObjectStemsVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
