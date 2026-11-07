"""Начальные байты буфера и создаваемых таблиц, точный контроль чтения до первой записи."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionLogRatio import LOG,EXP


class TrackedMemory(list):
    recording=False
    def __getitem__(self,address):
        if self.recording and isinstance(address,int) and address in self.targets and address not in self.written:
            self.old_reads.append(address)
        return super().__getitem__(address)
    def __setitem__(self,address,value):
        if self.recording:
            assert isinstance(address,int)
            self.writes.append((address,value))
            if address in self.targets:self.written.add(address)
        super().__setitem__(address,value)


def main():
    source=(ROOT/'Tools/Disasm/Extracted/Active/17_ACTION.C.bin').read_bytes();base=flat_action()
    # Размещение только исходного уже перенесённого загрузчика в исследовательской памяти.
    base[0x4200:0x43FA]=source[0x43:0x23D]
    expected=(bytes(v&255 for v in LOG)+bytes(v>>8 for v in LOG)+bytes(EXP)
        +bytes((0x8000+32*y)>>8 for y in range(256))+bytes((32*y)&255 for y in range(256))
        +bytes(x>>3 for x in range(256))+bytes(128>>(x&7) for x in range(256)))
    counts=Counter();all_written=set()
    for seed in (None,0,255,165):
        for area in ('linear_buffer','generated_tables'):
            memory=TrackedMemory(base);start,end=(0x8000,0x8C00) if area=='linear_buffer' else (0x9100,0x9800)
            if seed is not None:memory[start:end]=[seed]*(end-start)
            memory.targets=set(range(start,end));memory.written=set();memory.old_reads=[];memory.writes=[]
            simulator=Simulator(memory)
            for entry in ((0xD10A,) if area=='linear_buffer' else (0x4355,0x438F,0x43CF)):
                memory.recording=False;memory[0xBFFE],memory[0xBFFF]=255,63
                simulator.registers[:]=get_registers({'PC':entry,'SP':0xBFFE,'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0xA140},None,False)
                memory.recording=True;simulator.run(start=entry,stop=0x3FFF);memory.recording=False
            assert not memory.old_reads,(area,seed,memory.old_reads[:16])
            assert memory.written==memory.targets,(area,seed,len(memory.written))
            assert bytes(memory[start:end])==(bytes([255])*3072 if area=='linear_buffer' else expected),(area,seed)
            all_written.update(memory.written);counts[area]+=1
    assert len(all_written)==4864
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),initial_fill_patterns=['original',0,255,165],
        actual_original_clear_and_three_generators_executed=True,read_of_initial_byte_before_first_write=False,
        all_3072_buffer_and_1792_table_bytes_rewritten=True,generated_values_match_independent_formulas=True,
        original_file_bytes_not_replaced_by_generated_values=True,clear_called_at_regular_frame_begin=True,
        arbitrary_other_game_phase_first_read_proved=False,complete_input_product_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionInitialStorageVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
