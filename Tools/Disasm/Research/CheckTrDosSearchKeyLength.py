"""Числовая длина сравнения ключа по 5D06 в выбранном TR-DOS 5.04T.

Документация: ../../../Docs/ActionBootFileKeys.md#длина-сравнения-имени-и-типа
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from CheckBootBankFileReads import boot_memory,FileReadPorts,ROOT,DISK,run_with_rom,Simulator
from CheckMapRaster import ObservedMemory
from CheckGlyphRenderer import compare_flags
from skoolkit.simutils import PC,SP,A,F,B,C,D,E,H,L


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dos_rom',type=Path)
    args=parser.parse_args()
    dos=args.dos_rom.read_bytes()
    basic=(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/128-1.rom').read_bytes()
    assert sha256(dos).hexdigest()=='e21d37271d087eab5ef8f88d8f3a58c8c19da1fa857b9790eaa974b231db9e13'
    # Проверка передачи длины в B и исходного цикла, сравнивающего пары байтов DE и HL.
    assert dos[0x1CCD:0x1CE1]==bytes.fromhex('11dd5c3a065d47afbe2003c11809cd1327c12806')
    assert dos[0x2713:0x271B]==bytes.fromhex('1abec0132310f9c9')
    comparisons=[]
    for count in range(256):
        effective=count or 256
        for mismatch in (False,True):
            memory=ObservedMemory(list(dos)+[0]*49152)
            memory[0x9000:0x9100]=[0x5A]*256
            memory[0x9200:0x9300]=[0x5A]*256
            if mismatch:
                memory[0x9000+effective-1]=0x5B
            memory[0xBFFE:0xC000]=[255,127]
            baseline=list(memory)
            cpu=Simulator(memory,dict(PC=0x2713,SP=0xBFFE,BC=count*256+0x9C,HL=0x9000,DE=0x9200))
            memory.writes=[];memory.recording=True
            cpu.run(start=0x2713,stop=0x7FFF)
            memory.recording=False
            r=cpu.registers
            reached=effective-1 if mismatch else effective
            assert (r[H]*256+r[L],r[D]*256+r[E])==(0x9000+reached,0x9200+reached)
            assert r[B]==int(mismatch) and r[C]==0x9C
            assert r[A]==0x5A and r[F]==compare_flags(0x5A,0x5B if mismatch else 0x5A)
            assert r[SP]==0xC000 and not memory.writes and list(memory)==baseline
            comparisons.append(dict(initial_B=count,effective_length=effective,last_byte_mismatch=mismatch,
                advanced_bytes=reached,final_B=r[B],final_F=r[F]))
    searches=[]
    # Проверка имени из оригинального каталога, меняется только тип в ключе запроса.
    for length in (8,9):
        for extension in (0x43,0x58):
            for cylinder in (0,9):
                memory=boot_memory(basic,17)
                memory[0x5CDD:0x5CE6]=DISK[22*16:22*16+9]
                memory[0x5CE5]=extension
                memory[0x5D06]=length
                memory[0x7FFE:0x8000]=bytes.fromhex('ff7f')
                cpu=Simulator(memory,dict(PC=0x3D13,SP=0x7FFE,BC=0x0A,IY=0x5C3A))
                ports=FileReadPorts(cylinder)
                cpu.set_tracer(ports)
                run_with_rom(cpu,basic,dos,lambda image:memory.__setitem__(slice(0,16384),image),0x7FFF)
                expected=22 if length==8 or extension==0x43 else 255
                assert cpu.registers[C]==memory[0x5D0F]==expected and cpu.registers[SP]==0x8000
                searches.append(dict(length=length,requested_extension=extension,initial_cylinder=cylinder,
                    returned_C=expected,system_result=memory[0x5D0F],catalogue_reads=ports.attempts))
    result=dict(passed=True,dos_rom_sha256=sha256(dos).hexdigest(),
        original_disk_sha256=sha256(DISK).hexdigest(),
        length_reader_hex=dos[0x1CCD:0x1CE1].hex(),compare_loop_hex=dos[0x2713:0x271B].hex(),
        compare_cases=len(comparisons),all_B_values_checked=True,zero_B_compares_256_bytes=True,
        compare_RAM_and_stack_bytes_unchanged=True,real_DOS_search_cases=len(searches),
        length_8_ignores_extension=True,length_9_includes_extension=True,
        prepared_system_variables=True,controller_and_ROM_paging_modelled=True,
        all_search_lengths_or_DOS_versions_proved=False,IRQ_executed=False,native_execution=False,
        assembly_executed=False,comparisons=comparisons,searches=searches)
    result=json.loads(json.dumps(result))
    path=ROOT/'Tools/Disasm/Reports/TrDosSearchKeyLengthVerification.json'
    if path.exists():
        assert json.loads(path.read_bytes())==result
    else:
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('512 сравнений исходным циклом ROM и 8 полных поисков, 5D06 задаёт число байтов имени с типом')


if __name__=='__main__':
    main()
