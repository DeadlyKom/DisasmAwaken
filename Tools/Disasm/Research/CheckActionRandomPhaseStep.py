"""6201, все слова потока и все пары таймер/третья фаза, точные записи и R."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionRecordFilters import STREAM_POINTERS
from ReferenceActionRandomPhaseStep import RandomPhaseMachine


def profiles():
    for seed in range(65536):yield seed,seed&255,seed>>8,'all_stream_words'
    for timer in range(256):
        for phase in range(256):yield 0x1357,timer,phase,'all_timer_phase_pairs'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();depth=0
    for seed,timer,phase,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        ix=0xA100;memory[ix+23],memory[ix+9]=timer,phase;address=STREAM_POINTERS[0]
        memory[address],memory[address+1],memory[address+2]=seed&255,seed>>8,0
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x6201,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':ix,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,serial*17&255,serial&1,serial%3
        model=RandomPhaseMachine(memory.banks,initial);model.random_phase()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True;simulator.run(start=0x6201,stop=0x3FFF);memory.recording=False
        compared=(*range(25),26,27)
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,seed,timer,phase,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        for page,offset,_ in memory.writes:
            if page==2 and stack-8<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path)
        if counts.total()%32768==0:print(str(counts.total())+' random phase cases passed',flush=True)
    assert counts.total()==131072 and depth==4 and paths['random_timer_reset'] and paths['phase_idle'] and paths['phase_direction_flipped']
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),all_stream0_words=True,
        all_256_timers_by_256_phases=True,actual_stream0_executed=True,exact_registers_flags_r_sp=True,
        full_eight_bank_ram_and_write_multiplicity_compared=True,maximum_additional_stack_bytes=depth,
        low_7bit_zero_keeps_phase=True,phase_80_original_magnitude_preserved=True,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionRandomPhaseStepVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
