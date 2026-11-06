"""Самостоятельная проверка ACTION C6F4, перенос доказательства карты ограничен сверкой всех инструкций."""
from collections import Counter
import json
import re
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckSignedMultiply import signed,sbc16_flags
from CheckActionVertexCodes import logic_flags
from Analyze import payload
from InspectZ80 import decoder


def main():
    flat=flat_action()
    action=decoder(flat).disassemble(0xC6F4,0xC88C,'h')
    reference=[0]*65536;raw=payload(7);reference[0xC000:0xC000+len(raw)]=raw
    mapped=decoder(reference).disassemble(0xDB63,0xDCFB,'h')
    delta=0xC6F4-0xDB63
    def relocate(operation):
        return re.sub(r'#([0-9A-F]{4})',lambda m:'#'+format(int(m[1],16)+delta,'04X') if 0xDB63<=int(m[1],16)<0xDCFB else m[0],operation)
    assert len(action)==len(mapped)==245
    assert all(a.address==b.address+delta and len(a.bytes)==len(b.bytes) and a.operation==relocate(b.operation) for a,b in zip(action,mapped))
    baseline=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    baseline[5],baseline[2],baseline[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=[bytearray(b) for b in baseline],out7ffd=16)
    simulator=Simulator(memory)
    counts=Counter();defects=0
    for fixed in (0,1,255,256,32767,32768,65535):
        for variable in range(65536):
            for left,right in ((variable,fixed),(fixed,variable)):
                memory.recording=False
                memory[0xBFFE],memory[0xBFFF]=255,63
                serial=counts.total()
                initial=get_registers({'AF':serial&65535,'HL':left,'DE':right,'BC':0x36C9,
                    '^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0xC6F4},None,False)
                initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
                x,y=signed(left),signed(right);mx,my=abs(x),abs(y)
                large=mx>=256 and my>=256;small=mx<256 and my<256
                defect=large and right==32768
                magnitude=mx*256 if defect else mx*my
                negative=bool((left^right)&32768)
                result=(-magnitude if negative else magnitude)&0xFFFFFFFF
                a=(left>>8)^(right>>8)
                flags=sbc16_flags(0,magnitude>>16,int(bool(magnitude&65535))) if negative else logic_flags(a)
                bc=magnitude>>16 if negative else 0 if large else 0x3600 if not small else 0x36C9
                ix=magnitude&65535 if large else 0xABCD
                wanted=list(initial);wanted[0:2]=[a,flags]
                for position,value in ((2,bc),(4,result&65535),(6,result>>16),(8,ix)):wanted[position:position+2]=[value>>8,value&255]
                wanted[SP],wanted[PC]=0xC000,0x3FFF
                expected=[bytearray(b) for b in memory.banks]
                expected[2][0x3FFC:0x3FFE]=bytes((logic_flags(a),a))
                writes=[(2,0x3FFC,logic_flags(a)),(2,0x3FFD,a)]
                simulator.registers[:]=initial;memory.writes=[];memory.recording=True
                for _ in range(260):
                    if simulator.registers[PC]==0x3FFF:break
                    simulator.run()
                else:raise AssertionError('возврат умножения')
                memory.recording=False
                compared=(*range(13),14,*range(16,24),PC,26,27)
                assert all(wanted[i]==simulator.registers[i] for i in compared),(left,right,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
                assert all(a==b for a,b in zip(expected,memory.banks)) and Counter(writes)==Counter(memory.writes),'RAM'
                counts['16x16' if large else '8x8' if small else '8x16']+=1
                defects+=defect
    report=dict(passed=True,total_cases=counts.total(),paths=dict(counts),second_operand_8000_full_kernel_cases=defects,
        original_action_instructions_executed=True,all_245_instructions_relocation_checked_against_map=True,
        exact_registers_and_flags_except_R=True,every_physical_ram_byte_and_write_multiplicity_checked=True,
        all_words_against_seven_boundaries_both_orders=True,extreme_operand_asymmetry_preserved=True,
        refresh_and_timing_independently_checked=False,all_joint_inputs_exhausted=False,
        assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSignedMultiplyVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
