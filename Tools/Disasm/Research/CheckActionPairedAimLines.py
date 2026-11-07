"""63B6, все фазовые пары и режимы точки, две настоящие прямые растеризации включая равные концы."""
from collections import Counter
import json
from CheckIntro import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers
from ReferenceActionPairedAimLines import PairedAimMachine


def profiles():
    for phase in range(256):
        for step in range(256):yield phase,step,(phase^step)&255,119,43,phase*17&255,'all_phase_step_pairs'
    for x in range(256):
        for r in range(32):yield 255,1,255,x,(0,43,87,88)[x%4],r*7&255,'aim_X_and_R_modes'
    for charge in range(256):
        for r in range(16):yield 255,1,charge,(55,183)[r&1],88,r*17&255,'charge_and_equal_endpoint_modes'


def main():
    flat=flat_action();banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);baseline=[bytearray(b) for b in banks];simulator=Simulator(memory)
    counts=Counter();paths=Counter();r_cases=0;depth=0
    for phase,step,charge,x,y,r,profile in profiles():
        serial=counts.total();memory.recording=False
        for page in (0,2,5):memory.banks[page][:]=baseline[page]
        memory.banks[2][:3072]=bytes((i*37+serial*11)&255 for i in range(3072))
        memory[0x63B7],memory[0x63B9],memory[0xA8BC],memory[0x9B19],memory[0x9B1A]=phase,step,charge,x,y
        stack=0xBFFE;memory[stack],memory[stack+1]=255,63
        initial=get_registers({'PC':0x63B6,'SP':stack,'AF':serial&65535,'HL':0x1357,'DE':0x2468,'BC':0x369C,
            '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xA100,'IY':0xA140},None,False)
        initial[14],initial[15],initial[26],initial[27]=serial&255,r,serial&1,serial%3
        model=PairedAimMachine(memory.banks,initial);model.paired_aim()
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        simulator.run(start=0x63B6,stop=0x3FFF);memory.recording=False
        drawn='two_aim_lines' in model.path;compared=[i for i in (*range(25),26,27) if i!=15 or not drawn]
        assert all(model.r[i]==simulator.registers[i] for i in compared),(serial,phase,step,charge,x,y,r,model.path,[(i,model.r[i],simulator.registers[i]) for i in compared if model.r[i]!=simulator.registers[i]])
        assert memory.banks==model.banks and Counter(memory.writes)==Counter(model.writes),(serial,'RAM',model.path)
        for page,offset,_ in memory.writes:
            if page==2 and stack-8<=offset+0x8000<stack:depth=max(depth,stack-offset-0x8000)
        counts[profile]+=1;paths.update(model.path);r_cases+=int(not drawn)
        if counts.total()%16384==0:print(str(counts.total())+' paired aim cases passed',flush=True)
    assert counts.total()==77824 and depth==4 and paths['packed_equal_runs_256'],(counts,paths,depth)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),paths=dict(paths),
        all_256_phase_by_256_increment_values=True,all_256_ThirdValue_values=True,all_256_aim_X_values=True,
        aim_Y_profile=[0,43,87,88],actual_two_packed_entry_rasters_executed=True,
        packed_equal_endpoint_runs_256_preserved=True,exact_registers_except_R_on_raster=True,
        exact_R_on_nondrawing_cases=r_cases,full_eight_bank_ram_and_write_multiplicity_compared=True,
        maximum_additional_stack_bytes=depth,raster_R_proved=False,aim_Y_above_88_proved=False,
        complete_input_product_exhausted=False,assembly_executed=False,irq_executed=False,native_execution=False)
    path=ROOT/'Tools/Disasm/Reports/ActionPairedAimLinesVerification.json'
    temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,indent=2)+'\n','utf-8');temporary.replace(path)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
