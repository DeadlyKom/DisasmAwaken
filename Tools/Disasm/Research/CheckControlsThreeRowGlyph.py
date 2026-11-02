"""Три строки OR, независимая экранная адресация и все исходные фазы четырёх знаков."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh
from ReferenceControlsPointMotion import block_cost


def next_scanline(address):
    high,low = ((address>>8)+1)&255,address&255
    boundary = high&7==0
    carry = False
    if boundary:
        expanded = low+32
        low,carry = expanded&255,expanded>255
        if not carry:
            high = (high-8)&255
    return (high<<8)|low,boundary,carry


def main():
    original = base_memory()
    memory = Memory(original)
    simulator = Simulator(memory)
    touched = set()
    fixture_touched = set()
    counts = Counter()
    def check(base,y,x,kind,resource=None):
        nonlocal touched,fixture_touched
        memory.recording = False
        for address in touched|fixture_touched:
            memory[address] = original[address]
        phase = x&7
        source = (base+6*phase)&65535
        fixture_touched = set()
        if resource is not None:
            for i,value in enumerate(resource):
                address = (source+i)&65535
                memory[address] = value
                fixture_touched.add(address)
        address = 0x4000|((y&0xC0)<<5)|((y&7)<<8)|((y&0x38)<<2)|(x>>3)
        rows = [address]
        first,boundary0,carry0 = next_scanline(address)
        second,boundary1,carry1 = next_scanline(first)
        rows += [first,second]
        targets = [target for row in rows for target in (row,(row&0xFF00)|((row+1)&255))]
        sources = [(source+i)&65535 for i in range(6)]
        assert not set(targets)&set(sources)
        for target in targets:
            memory[target] = (73*y+17*x+31*target)&255
        memory[0xBFFE:0xC000] = [0xFF,0x3F]
        initial = get_registers({'AF':(x<<8)|y,'HL':0x1357,'DE':base,'BC':(y<<8)|x,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xE14E},None,False)
        initial[14],initial[15],initial[26],initial[27] = y,(x+y)&255,x&1,y%3
        writes = [(target,memory[target]|memory[src]) for target,src in zip(targets,sources)]
        expected = list(memory)
        for target,value in writes:
            expected[target] = value
        wanted = list(initial)
        final_value = writes[-1][1]
        flags = (final_value&0xA8)|(0x40 if final_value==0 else 0)|(4 if final_value.bit_count()%2==0 else 0)
        wanted[0:8] = [final_value,flags,y,2*phase,((source+5)&65535)>>8,(source+5)&255,
                        targets[-1]>>8,targets[-1]&255]
        cost = (block_cost(0xE14E,0xE17C)+block_cost(0xE17C,0xE183)
                +(block_cost(0xE183,0xE189)+(0 if carry0 else block_cost(0xE189,0xE18D)) if boundary0 else 0)
                +block_cost(0xE18D,0xE197)+block_cost(0xE197,0xE19E)
                +(block_cost(0xE19E,0xE1A4)+(0 if carry1 else block_cost(0xE1A4,0xE1A8)) if boundary1 else 0)
                +block_cost(0xE1A8,0xE1B1))
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],cost)
        simulator.registers[:] = initial
        memory.writes = []
        memory.recording = True
        for _ in range(100):
            if simulator.registers[PC]==0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',base,y,x))
        memory.recording = False
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared), (base,y,x,
            [(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory==expected and Counter(memory.writes)==Counter(writes), (base,y,x)
        touched = set(targets)
        counts[kind] += 1
    # Проверка каждой пары Y,X с четырьмя исходными таблицами восьми фаз.
    for base,name in ((0xE1B1,'plus'),(0xE1E1,'cross'),(0xE211,'solid'),(0xE241,'hollow')):
        for y in range(256):
            for x in range(256):
                check(base,y,x,'original_'+name)
        print('Three row glyph coordinates',hex(base),'complete',flush=True)
    # Проверка каждого значения каждого масочного байта в каждой фазе на меняющемся фоне.
    for byte_index in range(6):
        for value in range(256):
            for phase in range(8):
                resource = [(73*value+31*i+phase)&255 for i in range(6)]
                resource[byte_index] = value
                check(0xE1B1,(73*value+byte_index)&255,phase+8*((17*value+byte_index)&31),'all_mask_bytes',resource)
    # Проверка переноса источника через FFFF и краёв адресации экранных строк и столбцов.
    for base in (0xFFFF,0xFFFC,0xFFE0):
        for y in (0,6,7,62,63,190,191,254,255):
            for phase in range(8):
                for x in (phase,248+phase):
                    check(base,y,x,'source_wrap',[(i*73+y+x)&255 for i in range(6)])
    report = dict(passed=True,total_cases=sum(counts.values()),cases_by_kind=dict(counts),
        all_four_original_shapes_all_coordinates=True,all_six_mask_byte_values_and_phases=True,
        source_word_wrap_checked=True,right_byte_page_local_wrap_preserved=True,
        outside_192_row_bitmap_behavior_preserved=True,exact_registers_flags_r_and_sp=True,
        every_ram_byte_and_write_checked=True,arbitrary_overlapping_resources_proved=False,
        caller_e021_proved=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ControlsThreeRowGlyphVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
