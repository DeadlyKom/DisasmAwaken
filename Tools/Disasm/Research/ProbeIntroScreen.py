"""Исходный экранный распаковщик с тремя настоящими инструкциями локальной 48K ROM."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from CheckIntro import ROOT
from Analyze import payload
from CheckMusic import Simulator,get_registers,PC,SP


def physical(address):
    if address>=0x5800:return address
    high,low=address>>8,address&255
    b=(high&0xF8)|(low&7)
    value=(low&0xF8)^(high&7)
    c=((value<<2)|(value>>6))&255
    return b*256+c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.read_bytes()
    assert len(rom)==16384 and rom[0x1FC6:0x1FC9]==bytes((0xE1,0xC8,0xE9))
    source=payload(3);memory=[0xA5]*65536;memory[:16384]=rom
    memory[0x6300:0x6300+len(source)]=source
    memory[0x6E31:0x8931]=memory[0x8931:0xA431]
    memory[0xBFFE:0xC000]=[255,63]
    simulator=Simulator(memory);r=simulator.registers
    r[:]=get_registers({'AF':0xA55A,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        '^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC,'^AF':0xDEF0,
        'IX':0xABCD,'IY':0x5C3A,'SP':0xBFFE,'PC':0x6E31},None,False)
    output=[];writes=[];counts=collections.Counter();stream=[];references=[]
    for steps in range(2000000):
        pc=r[PC]
        if pc==0x3FFF:break
        if pc in (0x1FC6,0x1FC7,0x1FC8):counts['rom_instructions']+=1
        if pc==0x6E3D:
            counts['literals']+=1;stream.append(r[6]*256+r[7])
        if pc==0x6E82:
            counts['matches']+=1;stream.append(r[6]*256+r[7])
        if pc==0x6E9E:references.append((r[6]*256+r[7],r[2]*256+r[3]))
        if pc==0x6EB0:
            logical=r[4]*256+r[5];destination=r[2]*256+r[3]
            assert logical==0x4000+len(output) and destination==physical(logical)
            output.append(r[16]);writes.append(destination)
        simulator.run()
    else:raise AssertionError(('instruction_limit',hex(r[PC])))
    assert r[SP]==0xC000 and len(output)==6912 and len(set(writes))==6912
    assert set(writes)==set(range(0x4000,0x5B00))
    assert bytes(memory[physical(0x4000+i)] for i in range(6912))==bytes(output)
    assert max(stream)<0x6E31+len(source[0x2631:])
    report=dict(passed=True,partial_algorithm_analysis=True,whole_contract_proved=False,
        instructions_executed=steps,counts=dict(counts),rom_name=args.rom.name,
        rom_sha256=hashlib.sha256(rom).hexdigest(),rom_bytes_1FC6='E1C8E9',
        rom_call_stubbed=False,screen_bytes=6912,physical_bitmap_permutation_bijective=True,
        output_sha256=hashlib.sha256(bytes(memory[0x4000:0x5B00])).hexdigest(),
        logical_output_sha256=hashlib.sha256(bytes(output)).hexdigest(),
        maximum_stream_address=max(stream),original_packed_block_bytes=len(source[0x2631:]),
        reference_reads=len(references),registers=list(r),
        independent_bitstream_decoder=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/IntroScreenProbe.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='registers'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
