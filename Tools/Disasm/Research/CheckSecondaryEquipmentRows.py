"""Настоящий второй подготовитель таблиц и общий печататель строк оснащения."""
import json

from CheckEquipmentRows import Fixture, ROOT, SP, make_context, put, reference
from CheckEquipmentListAction import prepare
from ProbeShipPreviewCallbacks import PC, payload


BASES = (0x98F6, 0x95D4, 0x9632, 0x9484, 0xF066)


def main():
    _, _, base = make_context()
    cases = frame_count = original_text_cases = 0
    for top in (0, 1, *range(2, 14), 0x0100, 0x0101, 0xFFFF):
        for width in (92, 156, 188):
            for height in (24, 29, 48, 192):
                for ship in (0, 1, 3, 6, 255):
                    fixture = Fixture(base)
                    memory = fixture.memory
                    r = fixture.sim.registers
                    r[6:8] = [top >> 8, top & 255]
                    for address, value in (
                        (0xAEB3, width), (0xAEAB, height),
                        (0xAEBB, 3), (0xAEBF, 0), (0xAEC7, 3), (0xAECB, 0),
                        (0xBD26, 0), (0xBD73, 116), (0xBD7E, 134),
                        (0xBD89, 156), (0xBD94, 174), (0x72DD, 8), (0x984A, ship),
                    ):
                        memory[address] = value
                    if top > 1:
                        # Для произвольного индекса принудительно даём конечный CR-поток.
                        put(memory, 0xF066, bytes((13,)) * 257 + b'A\rB\n')
                    else:
                        original_text_cases += 1
                    if top > 13:
                        quantity = (0x98F6 + top) & 65535
                        put(memory, quantity, (1, 128))
                    expected = reference(memory, top, width, height, bases=BASES, ship_address=0x984A)

                    def observe(_, pc):
                        nonlocal frame_count
                        if pc == 0x726C:
                            sp = r[SP]
                            words = [memory[sp + j] + 256 * memory[sp + j + 1] for j in range(0, 14, 2)]
                            assert sp == 0x7FF2 and words == [
                                top, 0x98F6, 0x9632, 0x9484, ship << 8 | fixture.initial[1],
                                0x95D4, 0x3FFF,
                            ]
                            frame_count += 1

                    fixture.run(0x7403, observe)
                    assert tuple(r[:2]) == expected['af']
                    for start, words in ((2, expected['main']), (18, expected['alternate'])):
                        assert tuple(r[start:start + 6]) == tuple(
                            byte for word in words for byte in (word >> 8, word & 255))
                    assert tuple(r[16:18]) == expected['counter'] and r[SP] == 0x8000
                    assert (memory[0x6320], memory[0x6321]) == (expected['x'], expected['y'])
                    assert bytes(memory[0x4000:0x5B00]) == bytes(expected['screen'])
                    assert memory[0x7306] == ship and not fixture.trace.writes
                    cases += 1
    assert cases == frame_count == 1020 and original_text_cases == 120
    base[6][:len(payload(5))] = list(payload(5))
    paths = dict(scroll=0, absent=0, changed=0, repeated=0, full_event=0, draw=0, gate=0, render_rows=0)

    def panel(row=255, mode=0, index=0):
        fixture = prepare(base, row, mode, index)
        memory = fixture.memory
        put(memory, 0xF0FD, (0, 0, 32, 12, 1, 0))
        put(memory, 0x98F6, (1, 128))
        memory[0xAEAB], memory[0xAEB3] = 24, 188
        put(memory, 0x73D8, (row, 2))
        return fixture

    for row in (0, 1, 255):
        fixture = panel(row)
        fixture.run(0x735F)
        memory = fixture.memory
        assert memory[0x73D8] == 255
        assert memory[0xA265:0xA267] == [0xFB, 0x73] and memory[0xA235:0xA237] == [13, 0]
        assert memory[0x737D:0x737F] == [0, 0] and memory[0xC6E3] == 24
        paths['scroll'] += 1

    fixture = panel()
    before = [bytes(bank) for bank in fixture.memory.banks]
    fixture.run(0x7386)
    assert fixture.sim.registers[:2] == [0, 0x51] and not fixture.trace.writes
    assert [bytes(bank) for bank in fixture.memory.banks] == before
    paths['absent'] += 1

    for row, top in ((0, 0), (1, 3), (254, 33)):
        fixture = panel(row, index=255)
        memory = fixture.memory
        memory[0x737D] = top
        calls = []

        def observe(_, pc):
            if pc in (0xA49F, 0x6AAF, 0x73D7, 0x73DE, 0xA496):
                calls.append(pc)

        fixture.run(0x7386, observe)
        assert calls == [0xA49F, 0x6AAF, 0x73D7, 0xA496]
        assert memory[0x6ACC] == (row + top + 30) & 255
        assert memory[0x6AA4:0x6AA6] == [0, 0] and memory[0x73D8] == row
        paths['changed'] += 1

    for mode in range(256):
        fixture = panel(1, mode, index=31)
        memory, simulator = fixture.memory, fixture.sim
        simulator.registers[PC] = 0x7386
        for _ in range(100):
            if simulator.registers[PC] == 0xC000 and memory.o7ffd & 7 == 6:
                break
            simulator.run()
        else:
            raise AssertionError(('вход LANG', mode, simulator.registers[PC]))
        assert memory[0x983A] == 7 + int(mode != 0)
        paths['repeated'] += 1

    for mode in (0, 1, 255):
        fixture = panel(1, mode, index=31)
        memory = fixture.memory
        calls = []

        def observe(_, pc):
            if pc in (0xC000, 0xA49F, 0x7F35, 0x73DE, 0xA496):
                calls.append((pc, memory.o7ffd & 7))

        fixture.run(0x7386, observe)
        assert calls == [(0xC000, 6), (0xA49F, 0), (0x7F35, 0), (0x73DE, 0), (0xA496, 0)]
        assert memory[0x983A] == 7 + int(mode != 0) and memory[0x73D8] == 255
        assert memory.o7ffd == 0x10
        paths['full_event'] += 1

    for top in (0, 1):
        for listed in (False, True):
            fixture = panel()
            memory = fixture.memory
            put(memory, 0x737D, (top, 0))
            put(memory, 0x73D8, (0xDE, 0x73))
            put(memory, 0xF3DE, (0xDE, 0x73, 1, 1) if listed else (1, 1))
            fixture.run(0x73D7)
            assert fixture.wakes == int(listed)
            assert memory[0x73D8] == (255 if listed else 0xDE)
            if listed:
                assert memory[0x73D9] == fixture.sim.registers[0]
                paths['draw'] += 1
            paths['gate'] += 1

        fixture = panel()
        fixture.sim.registers[6:8] = [0, top]
        fixture.run(0x73FB)
        assert fixture.memory[0x73D8] == 255 and fixture.wakes == 0
        assert fixture.memory[0x73D9] == fixture.sim.registers[0]
        paths['render_rows'] += 1

    extra_cases = sum(paths.values()) - paths['draw']
    report = dict(passed=True, total_cases=cases + extra_cases, row_cases=cases, original_text_cases=original_text_cases,
                  frames_checked=frame_count, original_common_code_executed=True,
                  bitmap_and_both_register_banks_agree=True,
                  physical_secondary_bases=list(BASES), normal_game_caller_proved=False,
                  panel_paths=paths, total_panel_cases=extra_cases,
                  assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/SecondaryEquipmentRowsVerification.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
