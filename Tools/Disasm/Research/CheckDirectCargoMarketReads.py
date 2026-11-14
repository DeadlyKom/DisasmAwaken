"""Прямые внутренние входы груза и рынка, все словные индексы без суффиксов.

Документация: ../../../Docs/CargoField.md#внутренний-прямой-вход
Документация: ../../../Docs/MarketField.md#внутренний-прямой-вход
"""
from pathlib import Path
from hashlib import sha256
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'))
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers
from CheckGeometryReturnEntries import Memory
from CheckMarketAccess import add16_flags
from CheckWorldSignature import logical_flags


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    entry=next(e for e in manifest['entries'] if e['slot']==5)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    # Проверка физического происхождения всего LANG и двух целых внутренних фрагментов.
    assert sha256(disk).hexdigest()==manifest['sha256']
    assert source==disk[entry['offset']:entry['offset']+entry['allocated_length']]
    assert sha256(source).hexdigest()==entry['sectors_sha256']
    assert source[0x31A:0x323]==bytes.fromhex('29115298195e1600c9')
    assert source[0x27D:0x289]==bytes.fromhex('29115595197ee67f5f1600c9')
    probe=Memory(65536)
    probe[0x4000:0x4003]=bytes.fromhex('320070')
    cpu=Simulator(probe)
    cpu.registers[24]=0x4000
    probe.recording=True
    cpu.run()
    assert probe.writes==[(0x7000,0)]
    memory=Memory(65536)
    # Создание различающихся синтетических байтов цели, с сохранением исходного кода LANG.
    memory[:]=bytes((i*73+(i>>8)*19)&255 for i in range(65536))
    memory[0xC000:0xC000+len(source)]=source
    memory[0x7FFE:0x8000]=bytes((255,63))
    cpu=Simulator(memory)
    initial=get_registers({'SP':0x7FFE,'DE':0x2468,'BC':0x369C,
        'IX':0x47AD,'IY':0x58BE,'^HL':0x69CF,'^DE':0x7AD0,
        '^BC':0x8BE1,'^AF':0x9CF2},None,False)
    counts={}
    for address,name,base,cost in ((0xC31A,'cargo',0x9852,6),(0xC27D,'market',0x9555,8)):
        count=0
        for index in range(65536):
            r=cpu.registers
            r[:]=initial
            r[6],r[7],r[0],r[1],r[15]=index>>8,index&255,index&255,(index>>8)^(index&255),index&255
            expected=list(r)
            target=(base+2*index)&65535
            value=memory[target]
            # Расчёт оборачиваемого адреса и выходных флагов независимо от исполнения.
            if name=='cargo':
                f1=add16_flags(index,index,r[1])
                flags=add16_flags((2*index)&65535,base,f1)
            else:
                value&=127
                flags=logical_flags(value)|16
                expected[0]=value
            expected[4],expected[5],expected[6],expected[7]=0,value,target>>8,target&255
            expected[1],expected[12],expected[24]=flags,0x8000,0x3FFF
            expected[15]=(r[15]&128)|((r[15]+cost)&127)
            memory.writes.clear()
            memory.recording=True
            cpu.run(address,0x3FFF)
            memory.recording=False
            assert not memory.writes
            assert all(r[i]==expected[i] for i in range(len(expected)) if i!=25),(name,index,list(r),expected)
            assert memory[0x7FFE:0x8000]==bytes((255,63))
            count+=1
        counts[name]=count
    report=dict(passed=True,method='original_direct_cargo_and_market_entry_all_word_indices',
        cases=counts,total_cases=sum(counts.values()),exact_registers_except_T_checked=True,
        no_own_CPU_RAM_writes=True,CPU_write_watch_positive_control=True,
        physical_disk_and_sector_hashes_checked=True,M1_cargo=6,M1_market=8,
        full_reader_or_suffix_executed=False,target_memory_is_synthetic_with_original_LANG=True,
        logical_row_bounds_enforced=False,full_index_AF_R_cartesian_product_checked=False,
        arbitrary_stack_addresses_checked=False,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/DirectCargoMarketReadsVerification.json').write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()

