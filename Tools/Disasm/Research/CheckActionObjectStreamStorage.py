"""9F1C, отсутствие чтений прежнего буфера при копировании всех исходных моделей."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action,RecordedBanks
from CheckActionObjectCopy import packet
from CheckMusic import Simulator,get_registers
from CheckScreenUpdate import PortTrace


class TrackedStorage(RecordedBanks):
    targets=set()
    written=set()
    old_reads=[]
    def __getitem__(self,index):
        if self.recording and isinstance(index,int) and index in self.targets and index not in self.written:
            self.old_reads.append(index)
        return super().__getitem__(index)
    def __setitem__(self,index,value):
        if self.recording and isinstance(index,int) and index in self.targets:self.written.add(index)
        super().__setitem__(index,value)


def main():
    previous=json.loads((ROOT/'Tools/Disasm/Reports/ActionObjectCopyVerification.json').read_text('utf-8'))
    assert previous['passed']
    flat=flat_action();objects=(ROOT/'Tools/Disasm/Extracted/Active/24_OBJECT3D.C.bin').read_bytes()
    banks=[bytearray([160+i]*16384) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    banks[4][:len(objects)]=objects
    memory=TrackedStorage(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks]
    simulator=Simulator(memory);counts=Counter();union=set();lengths={}
    for index in range(0,256,2):
        pointer=flat[0x9E00+index]+256*flat[0x9E01+index]
        data,_,_=packet(objects,pointer-0xC000);lengths[index]=len(data)
        for pattern in (None,0,255,165):
            memory.recording=False
            for bank in range(8):memory.banks[bank][:]=baseline[bank]
            memory.out7ffd(16)
            if pattern is not None:
                for address in range(0x9F1C,0xA00A):memory[address]=pattern
            memory[0xBFFE],memory[0xBFFF]=255,63
            initial=get_registers({'PC':0xAAE2,'SP':0xBFFE,'AF':0xA55A,'HL':0x1300|index,'DE':0x2468,'BC':0x369C,
                '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A},None,False)
            memory.targets=set(range(0x9F1C,0x9F1C+len(data)));memory.written=set();memory.old_reads=[]
            simulator.registers[:]=initial;trace=PortTrace(simulator);simulator.set_tracer(trace)
            memory.writes=[];memory.recording=True
            simulator.run(start=0xAAE2,stop=0x3FFF);memory.recording=False
            assert not memory.old_reads,(index,pattern,memory.old_reads)
            assert memory.written==memory.targets,(index,pattern)
            assert bytes(memory[0x9F1C:0x9F1C+len(data)])==data
            assert trace.writes==[(0x7FFD,20),(0x7FFD,16)] and memory.o7ffd==16
            union.update(memory.written);counts[str(pattern)]+=1
    assert union==set(range(0x9F1C,0xA00A)) and max(lengths.values())==238
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),all_128_original_even_pointer_entries=True,
        actual_original_copy_and_bank_switching_executed=True,buffer_start=0x9F1C,maximum_original_copy_bytes=238,
        maximum_original_end_exclusive=0xA00A,read_of_initial_byte_before_first_write=False,
        generated_or_copied_values_not_serialized=True,original_buffer_bytes_preserved=True,
        storage_capacity_for_arbitrary_streams_proved=False,first_reads_in_arbitrary_other_phases_proved=False,
        subsequent_render_consumers_executed_in_this_test=False,assembly_executed=False,irq_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionObjectStreamStorageVerification.json'
    temporary=target.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(target)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
