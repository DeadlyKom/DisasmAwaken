"""Самостоятельное исполнение делителя ACTION C88C, без переноса адресных предположений из KARTA."""
from collections import Counter
import json,random,re
from ClassifyControlsTextDisplay import ROOT
from CheckActionParameterActivation import RecordedBanks,flat_action
from CheckMusic import Simulator,get_registers,PC,SP
from CheckSignedDivision import expected
from Analyze import payload
from InspectZ80 import decoder


def main():
    flat=flat_action()
    original=[0]*65536;raw=payload(7);original[0xC000:0xC000+len(raw)]=raw
    left=decoder(flat).disassemble(0xC88C,0xC941,'h')
    right=decoder(original).disassemble(0xDCFB,0xDDB0,'h')
    delta=0xC88C-0xDCFB
    def relocate(operation):
        return re.sub(r'#([0-9A-F]{4})',lambda m:'#'+format(int(m[1],16)+delta,'04X') if 0xDCFB<=int(m[1],16)<0xDDB0 else m[0],operation)
    assert len(left)==len(right)
    assert all(a.address==b.address+delta and len(a.bytes)==len(b.bytes) and a.operation==relocate(b.operation) for a,b in zip(left,right))
    banks=[bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5],banks[2],banks[0]=bytearray(flat[0x4000:0x8000]),bytearray(flat[0x8000:0xC000]),bytearray(flat[0xC000:])
    memory=RecordedBanks(banks=banks,out7ffd=16);memory[0xBFFE],memory[0xBFFF]=255,63
    simulator=Simulator(memory);counts=Counter()
    def check(number,divisor,selector,profile):
        raw=number&0xFFFFFFFF;carry=selector&1;alt_carry=(selector>>1)&1
        initial=get_registers({'AF':((raw>>8)&255)*256+(128 if divisor<0 else 0)+carry,'HL':raw>>16,'DE':divisor&65535,
            'BC':0x36C9,'IX':0x2468,'IY':0x5C3A,'^AF':(raw&255)*256+0x5C+alt_carry,
            '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'SP':0xBFFE,'PC':0xC88C},None,False)
        serial=counts.total();initial[14],initial[15],initial[26],initial[27]=serial&255,serial&255,serial&1,serial%3
        result,flags,alt_flags,bc,denominator,ix=expected(number,divisor,carry,alt_carry,0x36C9)
        wanted=list(initial);wanted[0:2]=[result>>8,flags];wanted[16:18]=[result&255,alt_flags]
        for pos,value in ((2,bc),(4,denominator),(6,result),(8,ix)):wanted[pos:pos+2]=[value>>8,value&255]
        wanted[SP],wanted[PC]=0xC000,0x3FFF
        simulator.registers[:]=initial;memory.writes=[];memory.recording=True
        for _ in range(160):
            if simulator.registers[PC]==0x3FFF:break
            simulator.run()
        else:raise AssertionError('возврат делителя')
        memory.recording=False
        compared=(*range(13),14,*range(16,24),PC,26,27)
        assert all(wanted[i]==simulator.registers[i] for i in compared),(number,divisor,selector,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert not memory.writes
        counts[profile]+=1
    # Проверка всех младших слов числителя при четырёх знаковых сочетаниях и граничных делителях.
    divisors=(1,2,9,255,256,32767,-1,-9,-255,-32768)
    for divisor in divisors:
        for value in range(65536):
            check(value,divisor,value,'word');check(-value-1,divisor,value,'word')
    # Проверка широких числителей при допустимом 16-разрядном частном.
    rng=random.Random(0xC88C)
    for divisor in divisors:
        for _ in range(1024):
            value=rng.randrange(abs(divisor)*65536)
            check(value,divisor,value,'wide');check(-value-1,divisor,value,'wide')
    report=dict(passed=True,total_cases=counts.total(),profiles=dict(counts),relocated_instructions_checked=len(left),
        original_action_bytes_executed=True,exact_registers_and_flags_except_R=True,no_ram_writes=True,
        negative_numerator_and_quotient_ones_complement_preserved=True,input_F_sign_selects_denominator_sign=True,
        zero_divisor_and_quotient_overflow_outside_contract=True,all_joint_inputs_exhausted=False,
        refresh_and_timing_independently_checked=False,assembly_executed=False,irq_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/ActionSignedDivisionVerification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
