"""CEA4, исходный JR с изменяемым смещением и обратное заполнение 2*A байтов."""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Disasm/Research'))
from CheckControlsTextQueue import base_memory
from CheckMusic import Simulator, get_registers, PC, SP
from CheckMusicGateTicks import Memory
from ReferenceControlsPointRespawn import refresh


def and_flags(value):
    return (value & 0xA8) | (0x40 if value == 0 else 0) | (4 if value.bit_count() % 2 == 0 else 0) | 0x10


def main():
    memory = Memory(base_memory())
    assert bytes(memory[0xCEF4:0xCEF7]) == bytes.fromhex('3A 8B D1')
    simulator = Simulator(memory)
    counts, targets = Counter(), Counter()
    last_changed = set()

    def check(entry, count, end, page, mode, fill):
        nonlocal last_changed
        memory.recording = False
        # Восстановление только байтов предыдущего опыта до задания новой оснастки.
        for address in last_changed:
            memory[address] = 0xA5 if address < 0xC000 else original[address]
        memory[0xCEB4] = 0xFE
        memory[0xD18B] = mode
        # Различаем Direction по D18B и отдельный Mode по D18C, соседний байт не должен подменить результат.
        memory[0xD18C] = mode ^ 255
        start_sp = 0xBFFE if entry == 0xCEA4 else 0xBFFC
        memory[0xBFFC:0xC000] = [0x57, 0x13, 0xFF, 0x3F]
        initial = get_registers({'AF':count*256+((fill*7)&255), 'HL':page*256+0x39,
            'DE':end*256+0x68, 'BC':0x369C, '^HL':0x1234, '^DE':0x5678, '^BC':0x9ABC,
            '^AF':0xDEF0, 'IX':0xAB00+fill, 'IY':0x5C3A, 'SP':start_sp, 'PC':entry}, None, False)
        if entry != 0xCEA4:
            initial[0] = fill
            initial[7] = end
        initial[14], initial[15], initial[26], initial[27] = fill, (mode+fill)&255, mode&1, mode%3
        simulator.registers[:] = initial
        expected = list(memory)
        writes = []
        if entry == 0xCEA4:
            length = 2*count if count not in (0,128) else 0
            returned_hl = page*256+end
            m1 = 16+4*count if length else 6
            if length:
                displacement = (62-4*count)&255
                writes += [(0xBFFD,page),(0xBFFC,end),(0xCEB4,displacement)]
                targets[0xCEF3-4*count] += 1
        else:
            length = {0xCEB5: 31, 0xCEB7: 30, 0xCECF: 18}[entry]
            returned_hl = 0x1357
            m1 = length*2+4
        # Вычисление адресов в пределах одной страницы, DEC L не переносит заём в H.
        writes += [(page*256+((end-index)&255),fill) for index in range(1,length+1)]
        for address,value in writes:
            expected[address] = value
        memory.writes = []
        memory.recording = True
        for steps in range(160):
            if simulator.registers[PC] == 0x3FFF:
                break
            simulator.run()
        else:
            raise AssertionError(('возврат',entry,count,end,page))
        memory.recording = False
        wanted = list(initial)
        wanted[0:2] = [mode,and_flags(mode)]
        wanted[6:8] = [returned_hl>>8,returned_hl&255]
        wanted[SP],wanted[15] = 0xC000,refresh(initial[15],m1)
        compared = (*range(13),14,15,*range(16,24),26,27)
        assert all(wanted[i] == simulator.registers[i] for i in compared), (entry,count,[(i,wanted[i],simulator.registers[i]) for i in compared if wanted[i]!=simulator.registers[i]])
        assert memory == expected and Counter(memory.writes) == Counter(writes), (entry,count,end,page)
        last_changed = {a for a,_ in writes}
        counts[format(entry,'04X')] += 1

    original = list(memory)
    # Проверка каждой допустимой длины и каждого младшего байта правой границы в четырёх страницах.
    for page in (0x40,0x58,0x80,0x8B):
        for count in range(16):
            for end in range(256):
                check(0xCEA4,count,end,page,(count*31+end)&255,(end*73+count)&255)
    # Проверка всех значений байта режима, заливки и специального нулевого результата ADD при A=80.
    for mode in range(256):
        for count in (*range(16),128):
            check(0xCEA4,count,(mode*17+count)&255,0x80,mode,mode)
    # Проверка физических входов двух частей развёрнутой цепочки с собственной рамкой стека.
    assert bytes(original[0xCEB5:0xCEB7]) == bytes.fromhex('2D 77')
    for entry in (0xCEB5,0xCEB7,0xCECF):
        for end in range(256):
            for fill in (0,1,0x55,0x80,0xFF):
                check(entry,fill,end,0x80,(fill+end)&255,fill)
    # Проверка исходного непродвижения при A=16, смещение JR остаётся FE.
    memory.recording = False
    memory[:] = original
    memory[0xBFFE:0xC000] = [0xFF,0x3F]
    simulator.registers[:] = get_registers({'AF':0x1000,'HL':0x8000,'DE':0x2000,'IX':0xAB55,'SP':0xBFFE,'PC':0xCEA4},None,False)
    for _ in range(40):
        simulator.run()
    assert simulator.registers[PC] == 0xCEB3 and memory[0xCEB4] == 0xFE and simulator.registers[SP] == 0xBFFC
    # Проверка всех знаковых смещений без исполнения путей за договором заполнителя.
    possible_targets = {0xCEB5 + int.from_bytes(bytes(((62 - 4*count) & 255,)), 'little', signed=True)
                        for count in range(256) if count not in (0, 128)}
    assert 0xCEB5 not in possible_targets and 0xCEB6 not in possible_targets
    report = dict(passed=True,total_cases=sum(counts.values())+1,cases_by_entry=dict(counts),
        dynamic_targets={format(a,'04X'):n for a,n in sorted(targets.items())},
        all_valid_half_lengths=True,all_endpoint_low_bytes=True,all_fill_and_mode_bytes=True,
        page_local_wrap_preserved=True,every_ram_byte_and_write_checked=True,exact_registers_flags_and_r=True,
        count_128_skips=True,count_16_nonprogress=True,other_counts_outside_contract=True,
        direct_prefix_entry='CEB5',direct_prefix_writes=31,
        computed_jump_never_selects_CEB5_or_CEB6=True,direct_prefix_game_caller_proved=False,
        direction_address=0xD18B,separate_mode_address=0xD18C,
        direction_and_separate_mode_differ_in_every_fill_case=True,
        irq_executed=False,native_execution=False,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsEvenSpanVerification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
