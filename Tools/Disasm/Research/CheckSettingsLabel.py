"""Исходное форматирование двухбайтовых настроек по длине существующей нультерминированной подписи."""
from pathlib import Path
import hashlib
import json
import random
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm'),str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP


def main():
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry=next(e for e in manifest['entries'] if e['slot']==4)
    source=(ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory=[0]*65536;memory[0x6000:]=source;original=memory[:]
    codes={}
    for index,address in enumerate(range(0x96AC,0x9728,2)):codes.setdefault(tuple(memory[address:address+2]),0x1D+index)
    keys=[pair for pair in codes if pair!=(0,0)]
    choices=[(value,0xA5) for value in range(127)]+[(0x80,0x3C),(0x81,0xC3)]+keys
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x7000,'BC':0x7100,'IX':0x2468,
                           'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    simulator=Simulator(memory);dis=decoder(original);cases=0

    def expected(pair):
        value,aux=pair
        if value<127:return value+0x30
        if value==0x80:return ord('N')
        if value==0x81:return ord('Y')
        return codes[pair]

    def execute(pairs,source_address=0x7000,target=0x7100,placeholder=0xA5):
        nonlocal cases
        data=[byte for pair in pairs for byte in pair]
        memory[source_address:source_address+len(data)]=data
        memory[target-1:target+len(pairs)+2]=[0xCA]+[placeholder]*len(pairs)+[0,0xFE]
        memory[0x7FFE:0x8000]=[255,63]
        simulator.registers[:]=initial;r=simulator.registers
        r[D],r[E],r[B],r[C]=source_address>>8,source_address&255,target>>8,target&255
        simulator.run(start=0xA163,stop=0x3FFF)
        assert memory[target-1:target+len(pairs)+2]==[0xCA]+[expected(p) for p in pairs]+[0,0xFE]
        assert memory[source_address:source_address+len(data)]==data
        assert r[H]*256+r[L]==0x1357 and r[B]*256+r[C]==target+len(pairs)
        assert r[D]*256+r[E]==source_address+2*len(pairs) and r[A]==0 and r[F]==0x54
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
        cases+=1

    # Проверка всех числовых маркеров, двух N/Y и всех 40 сигнатур независимо от исходного символа подписи.
    for pair in choices:
        for placeholder in (1,0x80,255):execute([pair],placeholder=placeholder)
    rng=random.Random(0xA163)
    # Проверка пустых и смешанных подписей с несколькими типами записей.
    for length in range(33):
        for repetition in range(8):execute([rng.choice(choices) for i in range(length)])
    bootstrap=[]
    # Проверка двух фактических пар указателей из StartStation на исходных секторных данных.
    for target,settings in ((0x9728,0x99AE),(0x9736,0x99C8)):
        length=original.index(0,target)-target
        pairs=[tuple(original[a:a+2]) for a in range(settings,settings+2*length,2)]
        memory[:]=original
        original_text=memory[target:target+length+1]
        simulator.registers[:]=initial;r=simulator.registers
        r[D],r[E],r[B],r[C]=settings>>8,settings&255,target>>8,target&255
        memory[0x7FFE:0x8000]=[255,63]
        simulator.run(start=0xA163,stop=0x3FFF)
        result=[expected(p) for p in pairs]+[0]
        assert memory[target:target+length+1]==result
        assert r[A]==0 and r[F]==0x54 and r[H]*256+r[L]==0x1357
        bootstrap.append(dict(target=f'{target:04X}',settings=f'{settings:04X}',length=length,
                              original_hex=bytes(original_text).hex(),formatted_hex=bytes(result).hex()))
        cases+=1
    report=dict(method='original_settings_label_formatter_all_tag_types_and_bootstrap_pointers',passed=True,cases=cases,
                source_sha256=hashlib.sha256(source).hexdigest(),numeric_tags=127,key_signatures=40,boolean_tags=2,
                bootstrap=bootstrap,irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/SettingsLabelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
