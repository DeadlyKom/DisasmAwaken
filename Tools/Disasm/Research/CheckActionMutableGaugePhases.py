"""Два фазовых накопителя UpdateFrame после настоящего применения параметров."""
from collections import Counter
import json,os,tempfile
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckIntro import ROOT
from CheckMusic import PC,SP,Simulator,get_registers
from CheckScreenUpdate import PortTrace


def main():
    flat=flat_action();banks=[bytearray(0x4000) for _ in range(8)]
    for bank,start in ((5,0x4000),(2,0x8000),(0,0xC000)):banks[bank][:]=bytes(flat[start:start+0x4000])
    memory=RecordedBanks(banks=banks,out7ffd=16);sim=Simulator(memory);trace=PortTrace(sim);sim.set_tracer(trace)
    initial=get_registers({'SP':0xBFFE,'IX':0xA100,'IY':0x5C3A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        'AF':0xA55A,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0},None,False)
    parameters=bytes(flat[0x9BA4:0x9BB3]);counts=Counter();outcomes=Counter()
    for step in range(256):
        memory.recording=False
        for index,value in enumerate(parameters):memory[0x9BA4+index]=value
        memory[0x9BA7],memory[0x9BA9]=step,step
        memory[0xBFFE],memory[0xBFFF]=255,63
        sim.registers[:]=initial;sim.run(start=0xAC5D,stop=0x3FFF)
        assert memory[0xA968]==memory[0xA8B5]==step
        for name,start,stop,phase_address,gauge_address,request_address in (
            ('third',0xA8B2,0xA8C8,0xA8B3,0xA8BC,0x666B),
            ('regen',0xA965,0xA97E,0xA966,0xA794,0x664A)):
            for phase in range(256):
                for gauge in (0,45,46,255):
                    memory.recording=False
                    memory[phase_address],memory[gauge_address],memory[request_address]=phase,gauge,173
                    sim.registers[:]=initial;memory.writes=[];memory.recording=True;trace.writes=[]
                    sim.run(start=start,stop=stop)
                    expected=[(phase_address,(phase+step)&255)]
                    increment=phase+step>255 and gauge<46
                    if increment:expected.extend(((gauge_address,gauge+1),(request_address,gauge+1 if name=='third' else 1)))
                    expected=[(5 if address<0x8000 else 2,address&0x3FFF,value) for address,value in expected]
                    context=(name,step,phase,gauge)
                    assert memory.writes==expected,context
                    assert sim.registers[PC]==stop and sim.registers[SP]==0xBFFE,context
                    assert sim.registers[2:12]==initial[2:12] and sim.registers[16:24]==initial[16:24],context
                    assert sim.registers[14]==initial[14] and sim.registers[26:28]==initial[26:28],context
                    assert memory.o7ffd==16 and not trace.writes,context
                    counts[name]+=1;outcomes['increment' if increment else 'unchanged']+=1
        if step%64==63:print('Checked gauge steps through '+str(step),flush=True)
    result=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),outcomes=dict(outcomes),
        actual_apply_parameter_set_executed=True,both_actual_phase_consumers_executed=True,
        all_step_phase_pairs=True,gauge_profiles=[0,45,46,255],all_gauge_values_exhausted=False,
        exact_order_and_values_of_all_memory_writes=True,sp_and_preserved_registers_checked=True,
        zero_step_never_increments=True,all_joint_inputs_exhausted=False,whole_frame_executed=False,
        af_and_refresh_proved=False,irq_executed=False,assembly_executed=False,native_execution=False)
    target=ROOT/'Tools/Disasm/Reports/ActionMutableGaugePhasesVerification.json'
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='gauge-phases-',suffix='.tmp',delete=False) as output:
        temporary=output.name;output.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    os.replace(temporary,target);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
