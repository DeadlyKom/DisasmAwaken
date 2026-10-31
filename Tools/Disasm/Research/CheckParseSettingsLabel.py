"""Обратное преобразование подписи, все ненулевые символы и все исходные дискриминаторы."""
from pathlib import Path
import json,sys,random
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,SP
from CheckRowHighlight import make_context


def main():
    _,_,banks=make_context();m=bytearray(65536);m[0x4000:0x8000]=bytes(banks[5]);m[0x8000:0xC000]=bytes(banks[2]);m[0xC000:]=bytes(banks[0]);s=Simulator(m)
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0xB400,'BC':0xB000,'AF':0x5A5D,'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    table=bytes(m);cases=words=numeric=markers=0
    def execute(text,records):
        nonlocal cases,words,numeric,markers
        expected=bytearray(records)
        for i,code in enumerate(text):
            old=records[2*i]
            if old==127 or old>=130:
                # Индекс удваивается в одном байте, перенос первого удвоения не доходит до H.
                offset=(2*((code-29)&255))&255;address=0x96AC+offset
                expected[2*i:2*i+2]=table[address:address+2];words+=1
            elif 128<=old<=129 and code in (ord('N'),ord('Y')):
                expected[2*i]=128 if code==ord('N') else 129;markers+=1
            else:expected[2*i]=(code-48)&255;numeric+=1
        n=len(text);m[0xB000:0xB001+n]=bytes(text)+bytes([0]);m[0xB3FF:0xB401+2*n]=bytes([0xA5])+bytes(records)+bytes([0x5A]);m[0x7FFE:0x8000]=bytes([255,63]);s.registers[:]=initial;s.run(start=0xA191,stop=0x3FFF);r=s.registers
        assert m[0xB400:0xB400+2*n]==expected,(text,records,expected,m[0xB400:0xB400+2*n])
        assert m[0xB3FF]==0xA5 and m[0xB400+2*n]==0x5A and m[0xB000:0xB001+n]==bytes(text)+bytes([0])
        assert (r[6]*256+r[7],r[2]*256+r[3],r[4]*256+r[5],r[A],r[F],r[SP])==(0x1357,0xB000+n,0xB400+2*n,0,0x54,0x8000)
        assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24];cases+=1
    # Проверка полного декартова произведения входного символа и прежнего типа записи.
    for code in range(1,256):
        for old in range(256):execute([code],[old,(code*73+old)&255])
    execute([],[]);rng=random.Random(0xA191)
    # Проверка неоднородных последовательностей и точного двухбайтового шага назначения.
    for length in range(1,65):
        for _ in range(4):execute([rng.randrange(1,256) for _ in range(length)],[rng.randrange(256) for _ in range(2*length)])
    report=dict(passed=True,cases=cases,all_nonzero_characters_and_old_discriminators=255*256,matrix_word_writes=words,numeric_byte_writes=numeric,ny_marker_writes=markers,
                low_byte_lookup_doubling_checked=True,old_second_byte_preserved_on_byte_writes=True,mixed_lengths_0_64=True,
                source_and_destination_guards_compared=True,all_return_registers_checked=True,
                irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/ParseSettingsLabelVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
