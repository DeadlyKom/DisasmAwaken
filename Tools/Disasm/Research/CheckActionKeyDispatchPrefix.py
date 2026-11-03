"""Частичный 6F1D до выбранного обработчика и отдельный исходный хвост 6F4E, без подмен обработчиков."""
from collections import Counter
import json
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckMusicGateTicks import Memory
from CheckControlsEvenSpan import and_flags
from CheckActionNearZeroWord import cost
from ReferenceControlsPointRespawn import refresh


class Inputs:
    def __init__(self,selected,value):
        self.selected,self.value,self.reads=selected,value,[]
    def read_port(self,registers,port,offset=0):
        value=self.value if len(self.reads)==self.selected else 255
        self.reads.append((port,value))
        return value


def main():
    original=flat_action()
    assert original[0x6F4E:0x6F55]==list(bytes.fromhex('dd e1 c1 d1 e1 18 d3'))
    rows=[tuple(original[0x9D4C+2*i:0x9D4E+2*i]) for i in range(27)]
    targets=[original[0x7017+2*i]|original[0x7018+2*i]<<8 for i in range(27)]
    assert rows[0]==rows[26] and targets[26]==0xC0C9
    memory=Memory(original);simulator=Simulator(memory);counts=Counter();touched=set()

    def execute(initial,wanted,expected,writes,limit):
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(limit):
            if simulator.registers[PC]==wanted[PC]:break
            simulator.run()
        else:raise AssertionError(('граница',initial[PC],wanted[PC]))
        memory.recording=False
        compared=(*range(13),14,15,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]]
        assert memory==expected and Counter(memory.writes)==Counter(writes)

    def prefix(selected,value,mode):
        nonlocal touched
        serial=counts.total();memory.recording=False
        for address in touched:memory[address]=original[address]
        memory[0xA85F]=mode;memory[0xBFFE:0xC000]=[0xFF,0x3F]
        initial=get_registers({'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6F1D},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        match=selected>=0 and not value&rows[selected][1]
        wanted=list(initial);writes=[]
        if match:
            index=selected;target=targets[index];next_ix=0x9D4E+2*index;pointer=0x7017+2*index
            words=(0x1300|27-index,pointer,(rows[index][0]<<8)|0xFE,next_ix,0x6F4E)
            for i,word in enumerate(words):writes.extend([(0xBFFD-2*i,word>>8),(0xBFFC-2*i,word&255)])
            wanted[0:8]=[mode,and_flags(mode),rows[index][0],0xFE,0x6F,0x4E,target>>8,target&255]
            wanted[8:10]=[next_ix>>8,next_ix&255]
            wanted[SP],wanted[PC]=0xBFF4,target
            m1=cost(0x6F1D,0x6F28)+(index+1)*cost(0x6F28,0x6F3B)+cost(0x6F3B,0x6F4E)
            count=index+1
        else:
            wanted[0:8]=[rows[26][1],0x42,rows[26][0],0xFE,0x70,0x4B,0x13,0]
            wanted[8:10]=[0x9D,0x82];wanted[PC]=0x6F55
            m1=cost(0x6F1D,0x6F28)+27*cost(0x6F28,0x6F3B)+cost(0x6F28,0x6F2B)
            count=27
        wanted[15]=refresh(initial[15],m1)
        expected=list(memory)
        for address,data in writes:expected[address]=data
        inputs=Inputs(selected,value);simulator.set_tracer(inputs)
        execute(initial,wanted,expected,writes,500)
        assert inputs.reads==[((rows[i][0]<<8)|0xFE,value if i==selected else 255) for i in range(count)]
        touched={address for address,_ in writes}
        counts['dispatch' if match else 'scan_exhausted']+=1

    # Проверка каждого байта IN на каждом шаге с остановкой до первой команды выбранного обработчика.
    for index in range(27):
        for value in range(256):prefix(index,value,(value*73+index)&255)
    # Проверка всех значений передаваемого режима на каждом из 27 выбранных адресов.
    for index in range(27):
        for mode in range(256):prefix(index,0,mode)
    for mode in range(256):prefix(-1,255,mode)
    # Проверка отдельного хвоста восстановления, ни один обработчик клавиши здесь не исполняется.
    for value in range(65536):
        memory.recording=False
        words=(value,value^0xA55A,(value*73)&65535,(value+0x1357)&65535)
        for i,word in enumerate(words):memory[0xBFF6+2*i:0xBFF8+2*i]=[word&255,word>>8]
        initial=get_registers({'AF':value,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,
            'IX':0xABCD,'IY':0x5C3A,'SP':0xBFF6,'PC':0x6F4E},None,False)
        initial[14],initial[15],initial[26],initial[27]=value&255,value&255,value&1,value%3
        wanted=list(initial)
        wanted[8:10]=[words[0]>>8,words[0]&255]
        wanted[2:4]=[words[1]>>8,words[1]&255]
        wanted[4:6]=[words[2]>>8,words[2]&255]
        wanted[6:8]=[words[3]>>8,words[3]&255]
        wanted[SP],wanted[PC],wanted[15]=0xBFFE,0x6F28,refresh(initial[15],6)
        execute(initial,wanted,list(memory),[],8);counts['restore_frame']+=1
    report=dict(passed=True,total_cases=counts.total(),cases_by_kind=dict(counts),
        every_in_byte_each_scan_position=True,every_mode_byte_each_dispatch_position=True,
        stopped_before_handler=True,handlers_executed=False,full_dispatcher_proved=False,
        exact_registers_flags_refresh_sp_and_targets=True,every_ram_byte_and_write_checked=True,
        maximum_prefix_stack_bytes=10,raw_return_epilogue_bytes='DDE1C1D1E118D3',
        raw_return_epilogue_separate_cases=65536,restore_m1=6,
        scan_positions=27,last_target='C0C9',last_pointer_overlaps_bytes_at=['704B','704C'],
        last_key_record_duplicates_first=True,consistent_static_keyboard_state_not_assumed=True,
        upper_bank_for_last_handler_unproved=True,unknown_6f1d_status_preserved=True,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionKeyDispatchPrefixVerification.json').write_bytes(
        (json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
