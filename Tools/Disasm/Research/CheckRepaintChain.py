"""Исходная цепочка возвратов, вызовы подменены явно указанными договорами без графики и IRQ."""
from pathlib import Path
from itertools import product
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1')]
from InspectZ80 import decoder
from skoolkit.simulator import Simulator
from skoolkit.simutils import get_registers, A, F, H, L, D, E, B, C, PC, SP
from CheckGlyphRenderer import and_flags


def main():
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))
    entry = next(e for e in manifest['entries'] if e['slot']==4)
    source = (ROOT/(entry['path']+'.sectors.bin')).read_bytes()
    memory = [0]*65536
    memory[0x6000:] = source
    dis = decoder(memory[:])
    simulator = Simulator(memory)
    initial = get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x247A,'BC':0x36C9,
                             'IX':0x2468,'IY':0x5C3A,'^HL':0x369C,'^DE':0x47AD,
                             '^BC':0x58BE,'^AF':0x69CF},None,False)
    observed = {}
    counts = {'early':0,'last':0,'draw':0,'tracker':0,'committed':0}
    cases = 0

    def ret():
        r = simulator.registers
        sp = r[SP]
        r[PC] = memory[sp]+256*memory[sp+1]
        r[SP] = (sp+2)&65535

    # Проверка трёх входов, включая сохранение бита 7 при выборе AND A по CBE2.
    for start,selector,flags,last,tracked in product((0xCBE0,0xCBE2,0xCBEB),range(256),(0,1,0x40,0xFF),(False,True),(False,True)):
        memory[0xCC17] = source[0x6C17]
        memory[0x7FFE:0x8000] = [0xFF,0x3F]
        simulator.registers[:] = initial
        r = simulator.registers
        r[A],r[F],r[PC] = selector,flags,start
        effective = selector & 127 if start==0xCBE0 else selector
        early = bool(effective & 128)
        calls = []
        for step in range(150):
            pc = r[PC]
            if pc==0x3FFF:break
            if pc==0x9E77:
                calls.append('close')
                # Выход callback намеренно меняет разрешённый договором BC и IY.
                r[B],r[C] = 0xAB,0xCD
                r[8],r[9],r[10],r[11] = 0xAC,0xBD,0xCE,0xDF
                r[A],r[F] = 0xA5,0x81
                ret()
            elif pc==0xBE38:
                calls.append('move')
                r[H],r[L] = 0x70,0
                r[A],r[F] = (0,0x42) if last else (1,2)
                ret()
            elif pc==0xA49F:
                calls.append('begin')
                assert memory[r[SP]:r[SP]+4]==[0,0x70,0x0C,0xCC]
                r[A],r[F] = 0x18,0x28
                ret()
            elif pc==0x7000:
                calls.append('draw')
                # Рисователь может менять AF, DE и IX, сохранённые внешним кадром.
                r[A],r[F],r[D],r[E] = 0xDE,0xAD,0xBE,0xEF
                r[8],r[9] = 0x12,0x34
                ret()
            elif pc==0xA496:
                calls.append('end')
                r[A] = 0x10
                ret()
            elif pc==0xC87C:
                calls.append('track')
                assert r[A]==effective and r[D]*256+r[E]==0x247A
                assert r[F]==(and_flags(effective)&~0x10)
                r[F] = ((and_flags(effective)&0xC4)|(effective&0x28)|1) if tracked else and_flags(effective)
                ret()
            else:
                assert 0xCBE0<=pc<0xCC21,hex(pc)
                instruction = dis.disassemble(pc,pc+1,'h')[0]
                raw = bytes(memory[pc:pc+len(instruction.bytes)])
                original = source[pc-0x6000:pc-0x6000+len(raw)]
                if raw==original:observed[f'{pc:04X}']=raw.hex()
                else:assert pc==0xCC17 and raw==b'\xA7'
                simulator.run()
        else:raise AssertionError('Цепочка возвратов не завершилась')
        assert r[SP]==0x8000
        assert r[D]*256+r[E]==0x247A
        assert r[8:10]==initial[8:10]
        assert memory[0xCC17]==(0x37 if start==0xCBEB else 0xA7)
        if early:
            assert not calls and r[A]==effective and r[F]&1 and not r[F]&0x40
            assert r[10:12]==initial[10:12]
            counts['early']+=1
        else:
            expected = ['close','move']+([] if last else ['begin','draw','end'])+(['track'] if effective else [])
            assert calls==expected,(calls,expected)
            assert r[A]==effective and r[H]*256+r[L]==0x7000
            assert r[B]*256+r[C]==0xABCD
            assert r[10:12]==[0xCE,0xDF]
            result = and_flags(effective)&~0x10
            if effective:
                result = ((and_flags(effective)&0xC4)|(effective&0x28)|1) if tracked else and_flags(effective)
            if not last and not result&1:
                result = (result&0xC4)|(effective&0x28)|1 if start==0xCBEB else and_flags(effective)
            assert r[F]==result,(start,selector,last,tracked,r[F],result)
            counts['last' if last else 'draw']+=1
            counts['tracker']+=bool(effective)
            counts['committed']+=bool(effective and tracked)
        cases+=1
    # Проверка непрерывного покрытия всех 65 исходных байтов независимо от изменённого AND A.
    assert sum(len(bytes.fromhex(v)) for v in observed.values())==65
    report = dict(method='original_repaint_chain_with_explicit_callee_contract_stubs',passed=True,cases=cases,
                  entries_checked=[0xCBE0,0xCBE2,0xCBEB],preserved_selector_AND_entry_checked=True,
                  source_sha256=hashlib.sha256(source).hexdigest(),counts=counts,original_visited=observed,
                  stubs=['CloseActiveItem','MoveItemToTail','BeginScreenUpdate','SelectedDrawHandler','EndScreenUpdate','TrackItemGeometry'],
                  graphics_executed=False,irq_executed=False,native_run=False,assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/RepaintChainVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='original_visited'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
