"""Проверка обхода записей F729 и возврата из счётчика в F775."""
from itertools import product
import json

from CheckActionParameterActivation import flat_action
from CheckIntro import ROOT
from CheckMusic import PC, SP, Simulator, get_registers
from ReferenceControlsPointRespawn import refresh
from skoolkit.simutils import IXh, IXl


def main():
    memory = flat_action()
    memory[0xBFFE:0xC000] = [255, 63]
    memory[0x9B83] = 0
    sim = Simulator(memory)
    cases = 0
    high_nibble_routes = {}

    def verify(high, low, cls, flags, value, limit, count, link, seed):
        nonlocal cases
        start = 0xA140
        memory[0xA100:0xA102] = [0, 128]
        before = bytearray((offset * 73 + seed) & 255 for offset in range(64))
        before[0], before[1], before[12], before[18] = low, high, flags, cls
        before[11], before[19], before[34] = link, value, limit
        memory[start:start + 64] = before
        for index in range(count):
            address = start + 64 * (index + 1)
            memory[address:address + 64] = bytes(64)
            memory[address + 10:address + 12] = [2, link]
            memory[address + 18] = 3
        marker = start + 64 * (count + 1)
        memory[marker:marker + 2] = [128, 128]
        memory[0x9BCD] = 30
        expected_delta = 30
        target, expected_ix = 0x3FFF, start if low == 128 else marker
        if high != 128:
            expected_ix = start
            if cls < 16 and value < ((limit - 1) & 255):
                before[19] += 1
            if not flags:
                target = 0xF843
            elif flags & 2:
                target = 0xF7C6
            elif cls != 18:
                target = 0xF792
            else:
                target = 0xF843
                before[13] = link
                if count < 2:
                    before[10] = 11
                    if link == 26:
                        expected_delta = 38
        sim.registers[:] = get_registers({'PC': 0xF729, 'SP': 0xBFFE}, None, False)
        sim.registers[15] = seed
        saw_resume = False
        for _ in range(320):
            pc = sim.registers[PC]
            if pc in (0x3FFF, 0xF843, 0xF7C6, 0xF792):
                break
            if pc == 0xF775:
                saw_resume = True
            if pc == 0xF77C:
                before[22] = 2 + (refresh(sim.registers[15], 2) & 1)
            sim.run()
        context = (high, low, cls, flags, value, limit, count, link, seed)
        assert saw_resume == (high != 128 and flags != 0 and not flags & 2 and cls == 18), context
        assert sim.registers[PC] == target and sim.registers[SP] == (0xC000 if target == 0x3FFF else 0xBFFE), context
        assert sim.registers[IXh] * 256 + sim.registers[IXl] == expected_ix, context
        assert bytes(memory[start:start + 64]) == before and memory[0x9BCD] == expected_delta, context
        # Фиксируем влияние старшей тетрады отдельно от индивидуального назначения её битов.
        if high == 0 and low == 128 and cls in (15, 18) and count == link == seed == 0 and flags & 15 == 0:
            high_nibble_routes[cls, flags] = dict(class_code=cls, link_flags=flags,
                target=target, final_state_code=memory[start + 10],
                class_link_counter_executed=saw_resume)
        cases += 1

    for value, limit in product(range(256), repeat=2):
        verify(0, 0, 15, 0, value, limit, 0, 0, 0)
    for cls, flags, count, link, seed in product((0, 15, 16, 18, 255), range(256), (0, 1, 2),
                                                 (0, 26, 255), (0, 1, 128, 255)):
        verify(0, 128, cls, flags, 33, 70, count, link, seed)
    for high, low in ((128, 0), (128, 128)):
        verify(high, low, 18, 1, 30, 100, 0, 26, 0)
    # Проверяем оба класса при каждой старшей тетраде и нулевых младших флагах.
    assert len(high_nibble_routes) == 32
    for cls in (15, 18):
        assert high_nibble_routes[cls, 0]['target'] == 0xF843
        for flags in range(16, 256, 16):
            item = high_nibble_routes[cls, flags]
            assert item['target'] == (0xF792 if cls == 15 else 0xF843)
            assert item['class_link_counter_executed'] == (cls == 18)
            if cls == 18:
                assert item['final_state_code'] == 11
    report = dict(passed=True, total_cases=cases, class_link_counter_executed=True,
                  real_resume_0xf775=True, exact_state_handler_not_executed=True, assembly_executed=False)
    report.update(high_nibble_routes=list(high_nibble_routes.values()),
                  high_nibble_can_change_whole_byte_zero_gate=True,
                  independent_meanings_of_bits_7_4_proved=False,
                  high_bit_states_reachable_in_native_game_proved=False)
    payload = json.dumps(report, indent=2) + '\n'
    (ROOT / 'Tools/Disasm/Reports/ActionObjectWalkVerification.json').write_text(payload, encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    main()
