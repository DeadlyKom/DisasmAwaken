"""Реальный поиск LF/CR на исходных таблицах, включая общие ограничители ресурсов."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers,A,F,B,C,D,E,H,L,PC,SP
from CheckRowHighlight import make_context
from StationPanelTextResources import escaped

TABLES=(('CaptionLabels',0xE399,22,10),('CenteredItemTexts',0xE4AA,42,10),
    ('LegalStatusLabels',0xEA3B,5,10),('StatusFieldLabels',0xEA89,3,10),
    ('GovernmentLabels',0xEB8D,5,10),('EconomyLabels',0xEBC2,4,10),
    ('PoliticalAreaLabels',0xF0B2,4,10),('QueuedMessages',0xCE19,17,10),
    ('EquipmentDescriptions',0xD1BA,34,10),('DecodedMessages',0xE262,2,10),
    ('EnvironmentLabels',0xDECB,13,13),('GameSettingsLabels',0xDF3C,43,13),
    ('TradeGoodsLabels',0xEC4C,30,13),('EquipmentNames',0xEE57,33,13))


def main():
    _,_,banks=make_context();base=bytearray(65536)
    base[0x4000:0x8000]=bytes(banks[5]);base[0x8000:0xC000]=bytes(banks[2]);base[0xC000:]=bytes(banks[0])
    initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5D,
        'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
    tables=[];cases=0
    for name,address,count,delimiter in TABLES:
        rows=[];cursor=address
        for index in range(count):
            # Расчёт независимого адреса после очередного физического ограничителя.
            start=base.index(delimiter,cursor)+1;cursor=start
            finish=start
            while base[finish] not in (10,13):finish+=1
            rows.append(dict(index=index,address=start,text_escaped=escaped(base[start:finish])))
            for flags in (0,1,0xFE,0xFF):
                for low in (0,255):
                    m=bytearray(base);m[0x7FFE:0x8000]=bytes([255,63]);before=bytes(m)
                    s=Simulator(m);s.registers[:]=initial;r=s.registers
                    r[A]=index;r[F]=flags;r[H]=address>>8;r[L]=address&255;r[C]=low
                    entry=0xA380 if delimiter==13 else 0xA390;r[PC]=entry
                    for _ in range(100000):
                        if r[PC]==0x3FFF:break
                        s.run()
                    else:raise AssertionError(('instruction_limit',name,index,hex(r[PC])))
                    assert r[H]*256+r[L]==start and r[A]==10 and r[F]==(0x42|(flags&1))
                    assert r[D:E+1]==initial[D:E+1] and r[B]==initial[B] and r[C]==low
                    assert r[8:12]==initial[8:12] and r[16:24]==initial[16:24] and r[SP]==0x8000
                    assert m[:0x7FF0]==before[:0x7FF0] and m[0x8000:]==before[0x8000:]
                    cases+=1
        tables.append(dict(name=name,base=address,delimiter=delimiter,physical_indices_checked=rows))
    assert tables[0]['physical_indices_checked'][0]['text_escaped']==''
    assert tables[0]['physical_indices_checked'][21]['address']==0xE499
    result=dict(passed=True,cases=cases,tables=tables,real_original_skip_code=True,
        independent_delimiter_scan=True,shared_delimiters_and_empty_caption_zero_checked=True,
        memory_outside_stack_unchanged=True,registers_and_carry_checked=True,
        arbitrary_indices_beyond_physical_tables_verified=False,graphics_verified=False,
        r_and_timing_verified=False,irq_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/StationPhysicalTextSelectorsVerification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='tables'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
