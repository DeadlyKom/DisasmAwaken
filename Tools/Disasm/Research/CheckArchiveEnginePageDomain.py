"""Домен страниц ENGINE и промежуточные окна при переключении в трёх режимах."""
import json

from CheckArchiveEngineStartup import ENGINE, RETURN, STACK, enter_call, init_prefix
from CheckArchiveMenuHandoff import HandoffMemory, HandoffPorts
from CheckArchiveEngineSource import ARCHIVE, compare_source
from CheckAwakenBasicRun import model_rom_context
from CheckControlsLegacySectorRead import run_with_rom
from CheckStationFlightCycle import ROOT, payload, put
from FighterAssetData import decode, original
from skoolkit.simulator import Simulator
from skoolkit.simutils import A, PC, SP


FIXED_CALLS = {
    0x4074: 7, 0x40AB: 0, 0x4238: 0, 0x466E: 0, 0x46F0: 13, 0x474E: 14,
    0x4955: 13, 0x496B: 14, 0x4976: 7, 0x4C96: 7, 0x4CDF: 7,
}
SPRITE_CALLS = {0x46B0, 0x4756}
RESTORE_CALL = 0x4CEB
SPRITE_TABLE_CALL = 0x500E


def check_callers():
    instructions = []
    raw = (ARCHIVE / '46_ENGINE.C.sectors.bin').read_bytes()
    assert raw[:len(ENGINE)] == ENGINE
    count, _ = compare_source(raw, instructions_out=instructions)
    code = dict(instructions)
    assert {pc for pc, op in instructions if op.startswith(('CALL', 'JP')) and op.endswith('#4FB1')} == (
        set(FIXED_CALLS) | {RESTORE_CALL, SPRITE_TABLE_CALL}
    )
    assert {pc for pc, op in instructions if op.startswith(('CALL', 'JP')) and op.endswith('#5006')} == SPRITE_CALLS
    assert {pc for pc, op in instructions if op.startswith('OUT')} == {0x4FCB, 0x4FD7, 0x4FE1, 0x4FEE}
    assert {pc for pc, op in instructions if op == 'CALL#4FFF'} == {0x4FF9}
    assert [code[pc] for pc in (0x4FFF, 0x5002, 0x5003)] == ['LDHL,#2A53', 'PUSHHL', 'JP#3D2F']
    assert all(ENGINE[pc - 0x4002:pc - 0x4000] == bytes((0x3E, page)) for pc, page in FIXED_CALLS.items())
    assert [code[pc] for pc in (0x4CD7, 0x4CDA, 0x4CE8, 0x4FB1)] == [
        'LDA,(#5012)', 'LD(#5013),A', 'LDA,(#5013)', 'LD(#5012),A',
    ]
    assert ENGINE[0x1012:0x1018] == b'\0\0\x08\x09\x0A\x0B'
    assert (code[0x469C], code[0x46A1]) == ('LDA,#0', 'LDB,#4')

    bar, banks = original()
    pointers, groups, _, _ = decode(bar, banks)
    steps = [step for group in groups for step in group['records']]
    assert len(pointers) == 36 and {step['bank'] for step in steps} == set(range(4))
    for group in groups:
        frame_count, flags, repeat, next_action = bar[group['offset']:group['offset'] + 4]
        assert repeat < frame_count if flags & 0x40 else next_action < len(pointers)
    assert code[0x4753] == 'LDA,(IX+#17)'
    assert {pc for pc, op in instructions if op.startswith('LD(IX+#17),')} == {0x4385}
    codes = sorted(set(FIXED_CALLS.values()) | set(ENGINE[0x1014:0x1018]))
    return dict(instructions_checked=count, fixed_calls=FIXED_CALLS, sprite_calls=sorted(SPRITE_CALLS),
                irq_restore_call=RESTORE_CALL, sprite_steps=len(steps), logical_codes=codes)


def selected_page(memory):
    return (memory.o7ffd & 7) | ((memory.o7ffd & 0x40) >> 3)


class PageTrace(HandoffPorts):
    def __init__(self, memory):
        super().__init__(memory)
        self.window_pages = []

    def write_port(self, registers, port, value, offset):
        super().write_port(registers, port, value, offset)
        self.window_pages.append(selected_page(self.memory))


def check_mode(mode, codes, basic, dos):
    prefix = init_prefix(mode)
    memory = HandoffMemory(mode)
    put(memory, 0x4000, bytes(prefix.memory[0x4000:0x505B]))
    bank4 = payload(37)
    memory.banks[12][:] = bank4
    cpu = Simulator(memory)
    memory.cpu = cpu
    ports = PageTrace(memory)
    cpu.set_tracer(ports)

    def set_rom(rom):
        memory.memory[0] = rom

    def select(code):
        enter_call(cpu, 0x4FB1)
        cpu.registers[A] = code
        ports.window_pages.clear()
        set_rom(basic)
        run_with_rom(cpu, basic, dos, set_rom, RETURN, step_limit=200)
        assert cpu.registers[PC] == RETURN and cpu.registers[SP] == STACK
        assert memory[0x5012] == code and selected_page(memory) == code
        assert len(ports.window_pages) == (1 if mode == 0 else 2)
        return set(ports.window_pages)

    # Первый выбор экрана устанавливает страницу 7 из любого состояния окна.
    startup_windows = set()
    for start in range(16):
        select(start)
        startup_windows.update(select(7))
    assert 12 not in startup_windows
    windows = set()
    for start in codes:
        for target in codes:
            select(start)
            windows.update(select(target))
    assert all(page & 7 != 4 for page in windows)
    assert bytes(memory.banks[12]) == bank4 and not memory.unclassified_reads
    return dict(mode=mode, first_screen_inputs=16, selector_transitions=len(codes) ** 2,
                first_screen_windows=sorted(startup_windows), all_windows=sorted(windows))


def main():
    proof = check_callers()
    rom_path = ROOT / 'Tools/Disasm/Research/Runtime/Unreal/rom/trdos504t.rom'
    basic, dos, _ = model_rom_context(rom_path)
    modes = [check_mode(mode, proof['logical_codes'], basic, dos) for mode in range(3)]
    result = dict(passed=True, **proof, profiles=modes, bank4_page=12,
                  external_transfer_to_5c26_executed=False, interrupts_injected=False,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/ArchiveEnginePageDomainVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
