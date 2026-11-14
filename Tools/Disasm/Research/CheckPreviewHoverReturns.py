"""Пустые наведения просмотра и описания, физические владельцы и точные RET.

Документация: ../../../Docs/PreviewHover.md#проверка-обоих-пустых-возвратов
"""
from pathlib import Path
import json

from ProbeShipPreviewCallbacks import Fixture, make_context
from PackedRefreshTrace import PackedRefreshTrace
from skoolkit.simutils import A, F, PC, SP, I, R, IFF, IM

ROOT = Path(__file__).resolve().parents[3]


def main():
    _, _, banks = make_context()
    fixture = Fixture(banks)
    memory, simulator = fixture.memory, fixture.sim
    before = [bytes(bank) for bank in memory.banks]
    code = ((0x6837, 'c36f68'), (0x686F, 'c9'),
            (0x6913, 'c33d69'), (0x693D, 'c9'))
    trace = PackedRefreshTrace([dict(address=a, hex=h) for a, h in code], 0)
    results = {}
    for index, proxy, target in ((26, 0x6837, 0x686F), (27, 0x6913, 0x693D)):
        # Проверка владельца в физической FInterfaceItem, действие располагается через три байта.
        record = 0xF0FD + index * 16
        assert memory[record + 6] + memory[record + 7] * 256 == proxy
        assert bytes(memory[proxy:proxy + 3]) == bytes([0xC3, target & 255, target >> 8])
        assert memory[target] == 0xC9
        for entry, cost in ((proxy, 2), (target, 1)):
            for af in range(65536):
                initial = list(fixture.initial)
                initial[A], initial[F] = af >> 8, af & 255
                initial[PC], initial[SP] = entry, 0x7FFE
                initial[I], initial[R] = af >> 8, (af >> 8) ^ (af & 255)
                initial[IFF], initial[IM] = af & 1, (af >> 8) % 3
                simulator.registers[:] = initial
                registers = simulator.registers
                trace.initial_r = registers[R]
                trace.m1 = trace.steps = 0
                trace.prefix_counts.clear()
                # Проверка реального JP и RET, возвращённая цель не исполняется.
                for _ in range(cost):
                    trace.before(memory, registers[PC], registers[R])
                    simulator.run()
                    trace.after(registers[R])
                trace.finish(registers[R])
                assert trace.m1 == trace.steps == cost
                assert registers[PC] == 0x3FFF and registers[SP] == 0x8000
                assert all(registers[i] == initial[i] for i in
                           (*range(12), I, *range(16, 24), IFF, IM))
            results[f'{entry:04X}'] = dict(cases=65536, m1=cost, physical_owner=index)
    assert [bytes(bank) for bank in memory.banks] == before
    assert not fixture.trace.writes
    report = dict(passed=True, entries=results, total_cases=262144,
                  all_AF_values_per_entry=True, all_initial_R_values_per_entry=True,
                  every_instruction_and_R_step_checked=True, I_IM_IFF_preserved=True,
                  all_GPR_and_alternates_preserved=True, all_bank_bytes_unchanged=True,
                  no_memory_writes_from_verified_JP_RET_opcodes=True, no_port_writes=True,
                  fixed_stack_fixture=True, full_joint_register_cartesian=False,
                  returned_target_executed=False, irq_executed=False,
                  native_execution=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/PreviewHoverReturnsVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
