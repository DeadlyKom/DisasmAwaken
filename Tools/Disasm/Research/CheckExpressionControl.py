"""Полный числовой путь выражения и скобок на исходных инструкциях языка."""
from pathlib import Path
from itertools import product
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'Tools/Disasm/Research/vendor/skoolkit-10.1'),str(ROOT/'Tools/Disasm/Research')]
from skoolkit.simulator import Simulator
from skoolkit.pagingtracer import SliceableMemory
from skoolkit.simutils import get_registers,A,F,D,E,SP,PC
from CheckMultiplyBranches import reference as multiply
from CheckGlyphRenderer import compare_flags


EXPRESSION_START = 0xCA67
ASSIGNMENT_START = 0xCA7B
PREFIX_START = 0xCA81
PREFIX_PROVEN_END = 0xCA85
SCRIPT_START = 0xCA8F
WATCH_END = 0xCA95


class LangWorkspaceMemory(SliceableMemory):
    """Учитывает обращения только к физическим байтам LANG в банке 6."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reads = set()
        self.writes = set()
        self.registers = None
        self.prefix_reads = []
        self.prefix_writes = []

    def __getitem__(self, address):
        value = super().__getitem__(address)
        if isinstance(address, int) and EXPRESSION_START <= address < SCRIPT_START and self.o7ffd & 7 == 6:
            self.reads.add(address)
            if address >= PREFIX_START and self.registers is not None:
                self.prefix_reads.append((self.registers[PC], address, value))
        return value

    def __setitem__(self, address, value):
        if EXPRESSION_START <= address < WATCH_END and self.o7ffd & 7 == 6:
            self.writes.add(address)
            if PREFIX_START <= address < SCRIPT_START and self.registers is not None:
                self.prefix_writes.append((self.registers[PC], address, value))
        super().__setitem__(address, value)

    def check_nested_assignment(self, right):
        values = (0xDF, 0xC3, right & 0xFF, right >> 8)
        addresses = range(PREFIX_START, PREFIX_PROVEN_END)
        assert self.prefix_writes == list(zip((0xC7B0, 0xC7B2, 0xC1BC, 0xC1BE), addresses, values))
        assert self.prefix_reads == list(zip((0xC836, 0xC838, 0xC83E, 0xC840), addresses, values))


def check_nested_storage(source, initial):
    profiles = []
    for depth in range(11):
        banks = [bytearray(0x4000) for _ in range(8)]
        banks[6][:len(source)] = source
        text = (('1+(' * depth) + '1+2' + (')' * depth) + ':').encode()
        banks[2][0x3000:0x3000 + len(text)] = text
        memory = LangWorkspaceMemory(banks=banks, out7ffd=0x16)
        simulator = Simulator(memory)
        simulator.registers[:] = initial
        memory.registers = simulator.registers
        simulator.run(0xC039, 0xC00C)
        high = EXPRESSION_START + 4 * depth + 6
        assert memory.writes == set(range(EXPRESSION_START, high))
        assert bytes(memory[EXPRESSION_START:EXPRESSION_START + 2]) == (depth + 3).to_bytes(2, 'little')
        assert simulator.registers[SP] == initial[SP]
        if high > SCRIPT_START:
            assert bytes(memory[SCRIPT_START:high]) != source[SCRIPT_START - 0xC000:high - 0xC000]
        tail_addresses = set(range(PREFIX_PROVEN_END, min(high, SCRIPT_START)))
        tail_writes = {address for _, address, _ in memory.prefix_writes if address >= PREFIX_PROVEN_END}
        tail_reads = {address for _, address, _ in memory.prefix_reads if address >= PREFIX_PROVEN_END}
        assert tail_reads == tail_writes == tail_addresses
        profiles.append(dict(right_nested_groups=depth, result=depth + 3, highest_written_address=high - 1,
                             assignment_bytes_written=len({a for a in memory.writes if ASSIGNMENT_START <= a < PREFIX_START}),
                             prefix_bytes_written=len({a for a in memory.writes if PREFIX_START <= a < SCRIPT_START}),
                             additional_buffer_tail_bytes_read=len(tail_reads),
                             additional_buffer_tail_bytes_written=len(tail_writes),
                             script_bytes_overwritten=high > SCRIPT_START))
    return profiles


def main():
 manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'));e=next(e for e in manifest['entries'] if e['slot']==5)
 source=(ROOT/(e['path']+'.sectors.bin')).read_bytes();memory=bytearray(65536);memory[0xC000:0xC000+len(source)]=source;sim=Simulator(memory)
 initial=get_registers({'SP':0x7FF0,'HL':0x1357,'DE':0x247A,'BC':0x36C9,'AF':0x5A5C,'IX':0xB000,'IY':0x5C3A,
  '^HL':0xB800,'^DE':0x47AD,'^BC':0x58BE,'^AF':0x69CF},None,False)
 ops={'=':lambda x,y:int(x==y),'*':lambda x,y:multiply(x,y)[0],'+':lambda x,y:min(x+y,65535),
  '-':lambda x,y:max(x-y,0),'<':lambda x,y:int(x<y),'>':lambda x,y:int(x>y),
  '[':lambda x,y:int(x<=y),']':lambda x,y:int(x>=y),'&':lambda x,y:x&y,'!':lambda x,y:x|y,':':lambda x,y:y}
 count=nested=0
 def check(body,value,kind):
  sim.registers[:]=initial;r=sim.registers;end=')' if kind=='parenthesis' else ':' if kind=='condition' else '@'
  text=(body+end).encode();memory[0xB000:0xB000+len(text)]=text;memory[0x7FF0:0x7FF2]=bytes([255,63])
  entry,stop,base=(0xC32C,0x3FFF,0xB800) if kind=='parenthesis' else (0xC039,0xC00C,0xCA67)
  r[PC]=entry
  for _ in range(10000):
   if r[PC]==stop:break
   sim.opcodes[memory[r[PC]]]()
  else:raise AssertionError(('limit',body,kind,hex(r[PC])))
  assert memory[base:base+2]==value.to_bytes(2,'little'),(body,kind,value,memory[base:base+2])
  assert r[22]*256+r[23]==base+2 and r[20]*256+r[21]==value and r[D]*256+r[E]==value
  assert r[8]*256+r[9]==0xB000+len(body)+(kind=='parenthesis')
  assert (r[A],r[F])==(ord(end),compare_flags(ord(end),ord(end)))
  assert r[SP]==0x7FF0+(2 if kind=='parenthesis' else 0) and r[10:12]==initial[10:12] and r[16:20]==initial[16:20]
 # Проверка всех операторов для предельных чисел во всех трёх видах завершения.
 for left,right,(symbol,formula),kind in product((0,1,127,255,256,32767,65535),(0,1,127,255,256,32767,65535),ops.items(),('parenthesis','condition','inverse')):
  check(str(left)+symbol+str(right),formula(left,right),kind);count+=1
 # Проверка последовательности вычисления и влияния только явных скобок.
 cases=[('1+2*3',9),('1+(2*3)',7),('(1+2)*3',9),('(1+(2*3))+4',11),
  ('(65535+1)-1',65534),('1:2',2),('258*255+1',255),('(1=1)&(2>1)',1)]
 for body,result in cases:
  for kind in ('parenthesis','condition','inverse'):check(body,result,kind);nested+=1
 check('1:2:3',3,'parenthesis');nested+=1
 report=dict(passed=True,operator_cases=count,nested_and_chain_cases=nested,
  nested_storage_profiles=check_nested_storage(source,initial),
  method='original_numeric_readers_dispatch_operators_expression_call_and_control',all_eleven_operators=True,
  evaluation_left_to_right=True,explicit_nested_parentheses=True,calls_stubbed=False,
  irq_executed=False,native_execution=False,assembly_executed=False)
 (ROOT/'Tools/Disasm/Reports/ExpressionControlVerification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
