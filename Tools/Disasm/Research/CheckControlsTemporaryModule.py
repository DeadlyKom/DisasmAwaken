"""Первые три копирования DADE и достижимый предел при исходном нулевом BC."""
import json
from hashlib import sha256
from CheckBank4Index import WriteMemory

from CheckActionParameterActivation import RecordedBanks, flat_action
from CheckControlsTextQueue import base_memory
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from CheckScreenUpdate import PortTrace, put
from PackedResourceCodec import decode


def main():
    flat = flat_action()
    baseline = [bytearray(0x4000) for _ in range(8)]
    for bank, start in ((5, 0x4000), (2, 0x8000), (0, 0xC000)):
        baseline[bank][:] = bytes(flat[start:start + 0x4000])
    baseline[1][:] = bytes(base_memory()[0xC000:])
    sentinel = bytes((index * 37 + 33) & 255 for index in range(0x3400))
    baseline[2][0x0C00:] = sentinel
    panel = decode((ROOT / 'Tools/Disasm/Extracted/Active/25_PANEL.C.bin').read_bytes())['data']
    baseline[6][:len(panel)] = panel
    direct = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=17)
    direct_sim = Simulator(direct)
    direct_trace = PortTrace(direct_sim)
    direct_sim.set_tracer(direct_trace)
    direct_sim.registers[:] = get_registers({'PC': 0xDADE, 'SP': 0x5FF0}, None, False)
    direct_sim.run(0xDADE, 0xDAEB)
    assert direct_trace.writes == [(0x7FFD, 22)]
    assert direct.banks[1][0x1AEB] == 0xD9 and direct[0xDAEB] == 0x04
    # Проверка физического происхождения префикса CONTROL.
    manifest=json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_bytes())
    disk=(ROOT/'Tools/Disasm/Disk/original.trd').read_bytes()
    assert sha256(disk).hexdigest()==manifest['sha256']
    item=next(row for row in manifest['entries'] if row['slot']==23)
    source=(ROOT/(item['path']+'.bin')).read_bytes()
    assert source==disk[item['offset']:item['offset']+item['length']]
    assert bytes(baseline[1][0x1ADE:0x1AEB])==source[:13]==bytes.fromhex('DDE5ED73335E3E1601FD7FED79')
    # Проверка наблюдателя отдельной инструкцией CPU.
    probe=WriteMemory(banks=[bytearray(0x4000) for _ in range(8)],out7ffd=0x11)
    put(probe,0x4000,bytes.fromhex('320070'));probe_cpu=Simulator(probe)
    probe_cpu.registers[24]=0x4000;probe.recording=True;probe_cpu.run()
    assert probe.cpu_writes==[(0x7000,0)]
    prefix_memory=WriteMemory(banks=[bank.copy() for bank in baseline],out7ffd=0x11)
    prefix_cpu=Simulator(prefix_memory);prefix_trace=PortTrace(prefix_cpu);prefix_cpu.set_tracer(prefix_trace)
    prefix_initial=get_registers({'SP':0x7FFE,'HL':0x1357,'DE':0x2468,'BC':0x369C,
        'AF':0xA55A,'IY':0x5C3A,'^HL':0x47AD,'^DE':0x58BE,'^BC':0x69CF,'^AF':0x7AD0},None,False)
    prefix_cases=0
    for page in (0x01,0x09,0x11,0x19):
        for ix in range(65536):
            prefix_memory.out7ffd(page);prefix_memory[0x6306]=page
            prefix_cpu.registers[:]=prefix_initial;r=prefix_cpu.registers
            r[8],r[9]=ix>>8,ix&255;r[1]=ix&255;r[15]=ix&255
            r[14]=ix>>8;r[26]=ix&1;r[27]=ix%3
            before=list(r);prefix_trace.writes.clear()
            prefix_memory.cpu_writes.clear();prefix_memory.recording=True
            prefix_cpu.run(start=0xDADE,stop=0xDAEB);prefix_memory.recording=False
            # Проверка двух байтов IX и двух байтов сохранённого SP, прочих записей нет.
            assert prefix_memory.cpu_writes==[(0x7FFC,ix&255),(0x7FFD,ix>>8),(0x5E33,0xFC),(0x5E34,0x7F)]
            expected=list(before);expected[0]=0x16;expected[2:4]=[0x7F,0xFD]
            expected[12]=0x7FFC;expected[15]=(before[15]&128)|((before[15]+8)&127);expected[24]=0xDAEB
            assert all(r[i]==expected[i] for i in range(len(r)) if i!=25),(page,ix,list(r),expected)
            assert prefix_trace.writes==[(0x7FFD,0x16)] and prefix_memory.o7ffd==0x16
            assert prefix_memory[0x6306]==page and page!=0x16
            assert prefix_memory[0xDAEB]==4
            prefix_cases+=1
    def check_prefix_stack(stack, ix=0xA55A):
        prefix_memory.recording=False
        for page in range(8):prefix_memory.banks[page][:]=baseline[page]
        prefix_memory.out7ffd(0x11);prefix_memory[0x6306]=0x11
        initial=list(prefix_initial);initial[8:10]=[ix>>8,ix&255]
        initial[SP]=stack;initial[15]=0xFD
        expected=[bytearray(page) for page in prefix_memory.banks]
        writes=[(stack-2,ix&255),(stack-1,ix>>8),(0x5E33,(stack-2)&255),(0x5E34,(stack-2)>>8)]
        for address,value in writes:
            page=5 if address<0x8000 else 2 if address<0xC000 else 1
            expected[page][address&0x3FFF]=value
        wanted=list(initial);wanted[0]=0x16;wanted[2:4]=[0x7F,0xFD]
        wanted[SP]=stack-2;wanted[15]=0x85;wanted[PC]=0xDAEB
        prefix_cpu.registers[:]=initial;prefix_trace.writes.clear()
        prefix_memory.cpu_writes.clear();prefix_memory.recording=True
        prefix_cpu.run(start=0xDADE,stop=0xDAEB);prefix_memory.recording=False
        assert all(prefix_cpu.registers[i]==wanted[i] for i in range(len(wanted)) if i!=25)
        assert prefix_memory.cpu_writes==writes and prefix_memory.banks==expected
        assert prefix_trace.writes==[(0x7FFD,0x16)] and prefix_memory.o7ffd==0x16
        return prefix_memory[stack-2]|prefix_memory[stack-1]<<8, prefix_memory[0x6306]

    stack_profiles=(0x4002,0x5E32,0x5E33,0x5E37,0x6306,0x6309,0x7FFF,0x8000,0xBFFE,0xC000)
    # Проверка фиксированных слов стека, не накладывающихся на сохраняемый SP и тень страницы.
    for stack in stack_profiles:
        word=set((stack-2,stack-1))
        assert not word.intersection((0x5E33,0x5E34,0x6306))
        assert check_prefix_stack(stack)==(0xA55A,0x11)
    # Отрицательные контроли показывают, зачем нужны условия неперекрытия и фиксированной RAM.
    assert check_prefix_stack(0x5E35)[0]==0x5E33
    assert check_prefix_stack(0x6308)[1]==0x5A
    panel_word=baseline[6][0x1AEE]|baseline[6][0x1AEF]<<8
    assert check_prefix_stack(0xDAF0,panel_word^65535)[0]==panel_word
    template = baseline[1][0x1ADE:0x1B5D]
    fixture = 0x5000

    def relocated(original_pc):
        return fixture + original_pc - 0xDADE

    cases = []
    for length in (0, 1, 12, 0x600, 0x1C00, 0x2000):
        memory = RecordedBanks(banks=[bank.copy() for bank in baseline], out7ffd=17)
        put(memory, fixture, template)
        if length:
            put(memory, relocated(0xDB01), length.to_bytes(2, 'little'))
        sim = Simulator(memory)
        sim.registers[:] = get_registers({'PC': fixture, 'SP': 0x5FF0, 'IX': 0x1234}, None, False)
        trace = PortTrace(sim)
        sim.set_tracer(trace)
        limit = 0x4001 if not length else 40000
        steps = 0
        for _ in range(50000):
            pc = sim.registers[PC]
            if pc == relocated(0xDB20):
                break
            if pc == relocated(0xDB08):
                steps += 1
            sim.run()
            if steps == limit:
                break
        assert trace.writes == [(0x7FFD, 22), (0x7FFD, 17)], (length, trace.writes, sim.registers[PC], steps)
        assert bytes(memory.banks[6][:0x3400]) == sentinel
        assert bytes(memory[0x5E33:0x5E35]) == bytes((0xEE, 0x5F))
        assert bytes(memory[0x5FEE:0x5FF0]) == bytes((0x34, 0x12))
        if length:
            assert sim.registers[PC] == relocated(0xDB20) and sim.registers[SP] == 0x5FEE, length
            assert steps == length
            assert bytes(memory[0xE000:0x10000]) == bytes(baseline[5][0x2000:])
            assert bytes(memory[0x6400:0x6400 + length]) == bytes(baseline[1][0x600:0x600 + length])
            assert sim.registers[4:8] == [0x64, 0, 0x64, 0]
        else:
            assert sim.registers[PC] == relocated(0xDB08) and sim.registers[SP] == 0x5FEA
            assert steps == 0x4001 and memory[0xC000] == memory[0x0600]
        cases.append(dict(length=length, ldir_iterations=steps, stop_address=sim.registers[PC]))
    report = dict(passed=True, total_cases=len(cases), cases=cases,
                  entry_prefix_cases=prefix_cases,entry_prefix_all_IX_words=True,
                  entry_prefix_initial_pages=[1,9,17,25],entry_prefix_exact_R_M1=8,
                  entry_prefix_all_registers_except_T_checked=True,entry_prefix_exact_RAM_writes_checked=True,
                  entry_prefix_physical_bytes_checked=True,CPU_write_watch_positive_control=True,
                  entry_prefix_CurrentPage_not_updated=True,entry_prefix_stack_address=0x7FFE,
                  entry_prefix_additional_valid_stack_addresses=list(stack_profiles),
                  entry_prefix_additional_stack_exact_RAM_and_registers=True,
                  entry_prefix_negative_stack_aliases=dict(saved_IX_overwritten_by_saved_SP=0x5E35,
                      CurrentPage_overwritten_by_PUSH_IX=0x6308,banked_stack_switches_physical_word=0xDAF0),
                  entry_prefix_full_input_cartesian_product_checked=False,
                  entry_prefix_hardware_bus_order_verified=False,
                  direct_switch_changes_next_opcode=True, stored_opcode=0xD9, bank6_panel_opcode=0x04,
                  zero_count_reaches_destination_bank1=True, relocated_cases_are_hypothetical=True,
                  unpack_and_temporary_code_executed=False, assembly_executed=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ControlsTemporaryModuleVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
