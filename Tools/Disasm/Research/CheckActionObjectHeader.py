"""AACC, два реальных переключения страниц и чтение слова, включая переносы и нечётные индексы."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckScreenUpdate import PortTrace,put
from CheckMusic import Simulator,get_registers,PC,SP
from ReferenceControlsPointRespawn import refresh


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes();banks[4][:len(objects)]=objects
    memory=RecordedBanks(banks=[bytearray(b) for b in banks],out7ffd=16);simulator=Simulator(memory);counts=Counter();touched=set();fixture=set()
    def check(index,flags=0,old=16,forced_pointer=None):
        nonlocal touched,fixture
        memory.recording=False
        for bank,offset in touched|fixture:memory.banks[bank][offset]=banks[bank][offset]
        memory.out7ffd(old);fixture=set()
        if forced_pointer is not None:
            for address,value in ((0x9E00+index,forced_pointer&255),(0x9E00+((index+1)&255),forced_pointer>>8)):
                memory[address]=value;fixture.add((2,address&0x3FFF))
        put(memory,0xBFFE,[255,63]);serial=counts.total()
        initial=get_registers({'AF':(index<<8)|flags,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xAACC},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        wanted=list(initial);expected=[bytearray(b) for b in memory.banks];writes=[]
        def byte(address,value):bank=5 if address<0x8000 else 2;offset=address&0x3FFF;expected[bank][offset]=value;writes.append((bank,offset,value))
        def word(address,value):byte(address,value&255);byte(address+1,value>>8)
        pointer=expected[2][0x1E00+index]+256*expected[2][0x1E00+((index+1)&255)]
        # Создание эталона RAM-рамок первого CALL SelectMemoryPage, чтение данных выполняется после его возврата.
        word(0xBFFC,0xAAD8);word(0xBFFA,0x369C)
        def read_address(address):
            address&=65535
            if address<0x4000:return memory.roms[1][address]
            bank=5 if address<0x8000 else 2 if address<0xC000 else 4
            return expected[bank][address&0x3FFF]
        result=read_address(pointer)+256*read_address(pointer+1)
        word(0xBFFC,0xAAE1);word(0xBFFA,0x369C)
        value=(index+1)&255;f=(value&0xA8)|(64 if value==0 else 0)|(16 if index&15==15 else 0)|(4 if index==127 else 0)|(flags&1)
        wanted[0:2]=[16,f];wanted[6:8]=[result>>8,result&255]
        wanted[SP],wanted[PC],wanted[15]=0xC000,0x3FFF,refresh(initial[15],27)
        simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace);memory.writes=[];memory.recording=True
        for _ in range(40):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат')
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(index,forced_pointer,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(memory.writes)==Counter(writes),(index,forced_pointer,memory.writes,writes)
        assert trace.writes==[(0x7FFD,20),(0x7FFD,16)] and memory.o7ffd==16
        touched={(b,i) for b,i,_ in writes};counts['forced_pointer' if forced_pointer is not None else 'original_table']+=1
    # Проверка каждого исходного байтового индекса, входного Carry и всех незаблокированных конфигураций 7FFD.
    for index in range(256):
        for old in range(32):
            for flags in (0,255):check(index,flags,old)
    # Проверка каждого физического слова адреса при изменённой таблице в модели, без подмены дочерних процедур.
    for pointer in range(65536):check((pointer*73)&255,flags=pointer&255,forced_pointer=pointer)
    report=dict(passed=True,total_cases=counts.total(),cases_by_fixture=dict(counts),
        method='physical_banked_pointer_and_word_read_oracle_with_real_selector',
        original_bank4_file='Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin',bank4_unloaded_tail_fixture_fill=164,
        all_original_byte_indices=True,all_unlocked_7ffd_configurations=True,all_forced_pointer_words=True,
        pointer_index_wraps_within_9e_page=True,word_read_wraps_full_address_space=True,
        exact_registers_flags_refresh_sp=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        maximum_additional_stack_bytes=4,real_out_and_eight_banks=True,
        object_header_field_meanings_proved=False,valid_game_index_range_proved=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionObjectHeaderVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
