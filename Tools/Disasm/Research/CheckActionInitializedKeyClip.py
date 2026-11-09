"""Перекрытый шаг клавиатуры на копиях состояния реальных полётных кадров модели."""
import json

from TraceFlight import D, E, H, L, PC, ROOT, SP, Simulator, main as trace_flight
from CheckActionParameterActivation import RecordedBanks
from CheckActionOverlappingKeyClipReturns import run_to
from CheckActionOverlappingKeyDispatch import StationaryKey


FRAMES = (1, 2, 4, 8, 16, 32, 64)
PATHS = {0xC4F6: 'top_intersection', 0xC641: 'left_then_corner_request', 0xC0E0: 'left_then_corner_mark'}


def read_bytes(memory, address, length):
    return bytes(memory[address + offset] for offset in range(length))


def point(memory, address):
    data = read_bytes(memory, address, 5)
    return dict(second=int.from_bytes(data[:2], 'little', signed=True),
                first=int.from_bytes(data[2:4], 'little', signed=True), code=data[4])


def main():
    cases = {}

    def observe(frame, memory, registers):
        if frame not in FRAMES:
            return
        assert frame not in cases and memory.o7ffd == 0x10
        # Ветвь с клавишей не меняет основной проход, поэтому все кадры до снимка проходят без клавиш.
        branch = RecordedBanks(banks=[bank.copy() for bank in memory.banks], out7ffd=memory.o7ffd)
        branch.roms = tuple(rom.copy() for rom in memory.roms)
        branch.out7ffd(memory.o7ffd)
        simulator = Simulator(branch, config={'fast_ldir': False, 'fast_djnz': False})
        simulator.registers[:] = registers
        ports = StationaryKey()
        simulator.set_tracer(ports)
        run_to(simulator, 0xC0C9, 1000)
        assert len(ports.reads) == 27 and not ports.outs
        assert read_bytes(branch, simulator.registers[SP], 2) == bytes.fromhex('4e6f')
        state = dict(first_point=point(branch, 0xCF0B), second_point=point(branch, 0xCF1B),
                     corner_block=branch[0xCF03], seen=branch[0xCF07],
                     output_size=branch[0x9BA3], scan_sp=registers[SP], clip_sp=simulator.registers[SP])
        assert state['first_point'] == state['second_point'] == dict(second=0, first=0, code=0)
        assert state['corner_block'] == state['seen'] == state['output_size'] == 0
        branch.writes = []
        branch.recording = True
        # Обе точки равны. Фиксируем фактический вход в делитель и выход за числовой договор.
        visited = run_to(simulator, 0xC88C, 3000)
        divisor = simulator.registers[D] * 256 + simulator.registers[E]
        assert divisor == 0 and simulator.registers[H] == simulator.registers[L] == 0
        visited |= run_to(simulator, 0x6F4E, 3000)
        branch.recording = False
        paths = [name for address, name in PATHS.items() if address in visited]
        assert paths == ['left_then_corner_mark'] and 0xC993 not in visited and 0xC6EA not in visited
        assert branch[0xCF07] == 8 and branch[0x9BA3] == 2
        output = read_bytes(branch, 0x9000, 2)
        assert output == bytes(2)
        run_to(simulator, 0x6F55, 20)
        assert simulator.registers[SP] == registers[SP] and not ports.outs
        cases[frame] = dict(state=state, path=paths[0], divisor=divisor, output=output.hex(),
                            writes=branch.writes, immediate_return=0x6F4E, end_pc=simulator.registers[PC])

    baseline = trace_flight(['--verify-flight-cycle', '--frames', '65'], observe)
    assert tuple(cases) == FRAMES and baseline['complete_frame_returns'] == 64
    result = dict(passed=True, total_cases=len(cases), frame_probes=cases,
                  baseline_complete_frame_returns=baseline['complete_frame_returns'],
                  real_bootstrap_and_original_payloads_with_trdos_stub=True,
                  coordinates_unchanged_by_probe=True, keyboard_branch_irq_not_injected=True,
                  author_intent_proved=False, assembly_executed=False, native_execution=False)
    report = ROOT / 'Tools/Disasm/Reports/ActionInitializedKeyClipVerification.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
