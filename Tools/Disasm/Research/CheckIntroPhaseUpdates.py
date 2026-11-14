"""Фазовые слова, точные флаги, IFF и физические записи двух уровней обновления.

Документация: ../../../Docs/IntroGeneratedEffects.md#полные-договоры-обновления-фаз
"""
from collections import Counter
from itertools import product
from struct import pack
import json

from CheckIntro import ROOT, original_memory
from CheckActionParameterActivation import RecordedBanks
from CheckScreenUpdate import PortTrace
from skoolkit.simulator import Simulator
from skoolkit.simutils import PC, SP, R, get_registers


def advance(words):
    phase,step,delta = words
    effective = (-delta if phase&0x8000 else delta)&65535
    step = (step+effective)&65535
    value = (phase+step)&65535
    # Расчёт ADD HL,BC, S/Z/PV сохраняют результат BIT 7,B прежнего Phase.
    flags = (0x80 if phase&0x8000 else 0x44)|((value>>8)&0x28)
    flags |= 0x10 if (phase&4095)+(step&4095)>4095 else 0
    flags |= int(phase+step>65535)
    return (value,step,delta),effective,flags


def fixture(flat,stack,seed):
    banks = [bytearray([0xA0+i]*0x4000) for i in range(8)]
    banks[5][:] = bytes(flat[0x4000:0x8000])
    memory = RecordedBanks(banks=banks,out7ffd=0x16)
    memory[stack],memory[stack+1] = 255,63
    initial = get_registers(dict(PC=0x6A2C,SP=stack,HL=0x7000,DE=0x2468,BC=0x369C,
        AF=0xA55A,IX=0xABCD,IY=0x5C3A,I=seed&255,R=seed&255,
        **{'^AF':0xDEF0,'^HL':0x1234,'^DE':0x5678,'^BC':0x9ABC}),
        {'im':seed%3,'iff':seed&1},False)
    return memory,initial


def execute(memory,initial,wanted,expected,writes,entry,m1):
    wanted[PC],wanted[SP] = 0x3FFF,initial[SP]+2
    wanted[R] = (initial[R]&128)|((initial[R]+m1)&127)
    wanted[26] = 1
    cpu = Simulator(memory)
    cpu.registers[:] = initial
    ports = PortTrace(cpu)
    cpu.set_tracer(ports)
    memory.writes = []
    memory.recording = True
    cpu.run(entry,0x3FFF)
    memory.recording = False
    # Проверка всех регистров кроме времени, всех банков и физических повторных записей.
    assert all(cpu.registers[i]==wanted[i] for i in (*range(25),26,27)),(entry,[(i,wanted[i],cpu.registers[i]) for i in range(28) if i!=25 and wanted[i]!=cpu.registers[i]])
    assert memory.banks==expected,(entry,'RAM')
    assert Counter(memory.writes)==writes,(entry,'writes')
    assert not ports.writes and memory.o7ffd==0x16


def main():
    flat = original_memory()
    # Проверка физического выделения BASIC выполняется по секторам, код лежит за логической длиной.
    manifest = json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text(encoding='utf-8'))
    entry = next(row for row in manifest['entries'] if row['slot']==3)
    original_disk = (ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    disk = original_disk[entry['offset']:entry['offset']+entry['allocated_length']]
    for start,end in ((0x6A2C,0x6A4B),(0x6BF6,0x6C21)):
        assert bytes(flat[start:end])==disk[start-0x6300:end-0x6300]
    counts = Counter()
    values = (0,1,255,256,32767,32768,32769,65534,65535)
    for seed,words in enumerate(product(values,repeat=3)):
        memory,initial = fixture(flat,0x5FFE,seed)
        for i,value in enumerate(pack('<HHH',*words)):
            memory[0x7000+i] = value
        expected = [bank.copy() for bank in memory.banks]
        updated,effective,flags = advance(words)
        output = pack('<HHH',*updated)
        expected[5][0x3000:0x3006] = output
        expected[5][0x2A47:0x2A49] = pack('<H',initial[SP])
        writes = Counter((5,0x3000+i,value) for i,value in enumerate(output))
        writes.update((5,0x2A47+i,value) for i,value in enumerate(pack('<H',initial[SP])))
        assert sum(writes.values())==8
        wanted = list(initial)
        wanted[:8] = [updated[0]>>8,flags,words[0]>>8,words[0]&255,effective>>8,effective&255,updated[0]>>8,updated[0]&255]
        execute(memory,initial,wanted,expected,writes,0x6A2C,19+7*int(bool(words[0]&0x8000)))
        counts['AdvanceParameters'] += 1
    for seed,signs,stack in product(range(256),range(8),(0x5FFE,0xBFFE)):
        memory,initial = fixture(flat,stack,seed)
        initial[PC] = 0x6BF6
        memory[0x6C12],memory[0x6C13] = seed,0x64
        cursor = (seed+3)&255
        memory[0x6400+cursor] = seed
        words_list = []
        for index in range(3):
            phase = ((seed*257+index*0x111)&0x7FFF)|(0x8000 if signs&(1<<index) else 0)
            words = phase,(seed*0x1F1F+index*0x1111)&65535,(seed*0x7F03+index*0x3333)&65535
            words_list.append(words)
            address = 0x6C8A+6*index
            for i,value in enumerate(pack('<HHH',*words)):
                memory[address+i] = value
        expected = [bank.copy() for bank in memory.banks]
        writes = Counter()
        for index,(words,target) in enumerate(zip(words_list,(0x6BA2,0x6BA6,0x6BA9))):
            updated,effective,_ = advance(words)
            address = 0x6C8A+6*index
            data = pack('<HHH',*updated)
            expected[5][address-0x4000:address-0x4000+6] = data
            writes.update((5,address-0x4000+i,value) for i,value in enumerate(data))
            expected[5][target-0x4000] = updated[0]>>8
            writes[5,target-0x4000,updated[0]>>8] += 1
        # Расчёт последнего сохранённого SP и трёх возвратов CALL в одних и тех же двух байтах.
        saved = pack('<H',stack-2)
        expected[5][0x2A47:0x2A49] = saved
        writes.update({(5,0x2A47+i,value):3 for i,value in enumerate(saved)})
        for return_address in (0x6BFC,0x6C05,0x6C0E):
            data = pack('<H',return_address)
            bank = 5 if stack<0x8000 else 2
            offset = (stack-2)&0x3FFF
            expected[bank][offset:offset+2] = data
            writes.update((bank,offset+i,value) for i,value in enumerate(data))
        for address,data in ((0x6C12,bytes((cursor,0x64))),(0x6BAC,bytes((seed>>1,)))):
            expected[5][address-0x4000:address-0x4000+len(data)] = data
            writes.update((5,address-0x4000+i,value) for i,value in enumerate(data))
        value = seed>>1
        flags = (value&0xA8)|(0x40 if value==0 else 0)|(4 if value.bit_count()%2==0 else 0)|(seed&1)
        wanted = list(initial)
        wanted[:8] = [value,flags,words_list[-1][0]>>8,words_list[-1][0]&255,effective>>8,effective&255,0x64,cursor]
        assert sum(writes.values())==36
        execute(memory,initial,wanted,expected,writes,0x6BF6,76+7*signs.bit_count())
        counts['AdvanceTexturePhases'] += 1
    report = dict(passed=True,cases=dict(counts),total_cases=sum(counts.values()),
        all_phase_sign_combinations=True,all_sample_bytes_and_cursor_values=True,
        parent_stack_fixtures=[0x5FFE,0xBFFE],exact_registers_except_T=True,
        all_physical_banks_and_write_counts_compared=True,final_IFF=1,
        child_M1='19+7*old_phase_sign',parent_M1='76+7*negative_phase_count',
        child_byte_writes=8,parent_byte_writes=36,parent_CPU_stack_byte_writes=6,
        all_joint_word_inputs_exhausted=False,IRQ_executed=False,assembly_executed=False,native_execution=False)
    (ROOT/'Tools/Disasm/Reports/IntroPhaseUpdatesVerification.json').write_text(
        json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
