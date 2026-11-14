"""Реальные два копирования загрузчика и точная граница экранного потока, без сборки."""
import hashlib
import json
from CheckIntro import A, H, L, PC, ROOT, SP, Simulator, execute, get_registers, original_memory, word
from IntroScreenCodec import Writer, decode, physical
from IntroScreenResources import render_attributes, parse_attributes
from skoolkit.simutils import F, IXh, IXl


def check_detached_unpack_return(memory, expected_screen):
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    # Начальные регистры берутся из подлинного префикса распаковщика, затем моделируется вход в хвост.
    profiles = []
    for extra_byte, branch_target in ((0x00, 0x7501), (0x43, 0x7580)):
        ram = memory.copy()
        ram[:0x4000] = rom
        assert ram[0x7500] == 0x7F
        ram[0x5B07] = extra_byte
        sim, _ = execute(ram, {'PC': 0x6E31}, stop=0x6E3C)
        registers = sim.registers
        registers[PC] = 0x74EC
        for _ in range(500000):
            if registers[PC] == 0x74EF:
                break
            sim.run()
        else:
            raise AssertionError('Условный CALL из хвоста не вернулся')
        assert bytes(ram[0x4000:0x5B00]) == expected_screen and ram[0x5AFF] == 7
        assert (registers[A], registers[F], registers[SP]) == (0xFF, 0xA8, 0xBFFE)
        for _ in range(9):
            if registers[PC] in (0x68EE, 0x7501, 0x7580):
                break
            sim.run()
        assert registers[PC] == branch_target and registers[SP] == 0xBFFE
        assert registers[IXh] * 256 + registers[IXl] == 0x5AFF
        assert registers[A] == extra_byte
        profiles.append(dict(byte_at_5b07=extra_byte, returned_a=0xFF, returned_f=0xA8,
                             byte_at_5aff=ram[0x5AFF], jr_displacement=0x7F, next_pc=branch_target))
    return profiles


def check_detached_attribute_jump(memory):
    # ADC A,FF возвращается только при нулевой сумме входных A и Carry.
    tail = memory.copy()
    word(tail, 0xBFFE, 0x74EF)
    assert bytes(tail[0x6E77:0x6E7D]) == bytes.fromhex('CE FF DD 6F 38 D8')
    for a in range(256):
        for carry in (0, 1):
            target = 0x74EF if a + carry == 0 else 0x6E55
            sim, _ = execute(tail, {'PC': 0x6E77, 'AF': a << 8 | carry}, stop=target, limit=7)
            if target == 0x74EF:
                assert sim.registers[A] == 0xFF and not sim.registers[F] & 0x40

    writer = Writer()
    writer.literal(7, first=True)
    remaining = 6908
    while remaining:
        count = min(256, remaining)
        writer.match(count, -1, extended=True)
        remaining -= count
    writer.literal(0)
    writer.match(2, -1)
    writer.end()
    assert decode(writer.data)['data'] == bytes((7,)) * 6909 + bytes(3)
    rom = (ROOT / 'Tools/Disasm/Research/vendor/skoolkit-10.1/skoolkit/resources/48.rom').read_bytes()
    profiles = []
    for generated in (False, True):
        ram = memory.copy()
        ram[:0x4000] = rom
        ram[0x6ECB:0x6ECB + len(writer.data)] = writer.data
        if generated:
            execute(ram, {'PC': 0x692D, 'IX': 0x80, 'DE': 0x7100, 'BC': 4}, limit=6000)
            execute(ram, {'PC': 0x68A4, 'HL': 0xA000}, limit=120)
        words = [0x9F00 + i * 37 for i in range(14)]
        for i, value in enumerate(words):
            word(ram, 0xBFFE + 2 * i, value)
        sim, _ = execute(ram, {'PC': 0x6E31}, stop=0x6E3C)
        sim.registers[PC] = 0x74EC
        for _ in range(500000):
            if sim.registers[PC] in (0x68EE, 0x7501, 0x7580):
                break
            sim.run()
        assert sim.registers[PC] == 0x68EE, (generated, hex(sim.registers[PC]), ram[0x5AFF],
                                             sim.registers[:12])
        assert (sim.registers[A], sim.registers[SP]) == (0, 0xBFFE) and ram[0x5AFF] == 0
        returned_hl = sim.registers[H] * 256 + sim.registers[L]
        assert 0x5AFD <= returned_hl <= 0x5AFF and ram[returned_hl] == 0
        before = ram.copy()
        for _ in range(60):
            if sim.registers[PC] == 0x6929:
                break
            sim.run()
        assert sim.registers[PC] == 0x6929
        expected = before.copy()
        if generated:
            for index, value in enumerate([returned_hl, *words], 17):
                row, column = divmod(index, 4)
                word(expected, (0x80 + row) * 256 + 0x80 + 2 * column, value)
        assert ram == expected
        assert sim.registers[SP] == (0xC01A if generated else 0xBFFE)
        assert word(ram, 0x692A) == (0xBFFE if generated else 0x3131)
        profiles.append(dict(generated_writer=generated, second_jump_target=0x68EE,
                             returned_hl=returned_hl,
                             written_words=15 if generated else 0, stack_words_consumed=14 if generated else 0,
                             restored_stack_operand=word(ram, 0x692A)))
    return dict(terminator_af_cases=512, first_jump_taken_on_return=False,
                generated_and_ungenerated_paths=profiles, original_game_caller_proved=False)


def check_detached_relative_targets(memory):
    cases = [(value, 0x7F) for value in range(256)]
    cases += [(value, offset) for offset in range(256) for value in (0x43, 0)]
    sim = Simulator(memory)
    initial = get_registers({'PC': 0x74F7, 'SP': 0xBFFE, 'HL': 0x5AFF}, None, False)
    for value, offset in cases:
        memory[0x5B07] = value
        memory[0x7500] = offset
        signed = offset if offset < 128 else offset - 256
        target = 0x7501 + (signed if value == 0x43 else 0)
        sim.registers[:] = initial
        for _ in range(5):
            sim.run()
        assert sim.registers[PC] == target
        assert (sim.registers[A], sim.registers[SP]) == (value, 0xBFFE)
        assert sim.registers[IXh] * 256 + sim.registers[IXl] == 0x5AFF
    return len(cases)


def check_source_clear_after_transfer(memory, seed):
    probe = memory.copy()
    probe[0x9000:0xC000] = [seed] * 0x3000
    assert probe[0x8F93] == probe[0x7493] == 0xFF
    assert probe[0x8F6B:0x9000] == probe[0x746B:0x7500]
    expected = probe.copy()
    expected[0x8F93:0xC000] = [0] * 0x306D
    simulator, _ = execute(probe, {'PC': 0x6550}, stop=0x655D)
    assert probe == expected
    assert simulator.registers[H] * 256 + simulator.registers[L] == 0xBFFF
    return dict(seed=seed, start=0x8F93, end_exclusive=0xC000,
                first_store=0x6559, overlapping_copy=0x655B,
                original_prefix_bytes_preserved=40, transferred_tail_bytes_preserved=149,
                whole_ram_compared=True)


def main():
    data = (ROOT / 'Tools/Disasm/Extracted/Active/03_AWAKEN.B.sectors.bin').read_bytes()
    initial = data[0xB31:0x2631]
    assert len(initial) == 6912
    text, labels = render_attributes(initial[6144:])
    assert parse_attributes(text) == initial[6144:] and labels['IntroInitialScreen.Row00'] == 0x8631
    # Проверка точного окончания битового потока, три непрочитанных бита последнего байта сохраняются.
    decoded = decode(data[0x26CB:])
    assert decoded['stream_position'] == 1440 and decoded['remaining_bits'] == 3
    assert len(decoded['data']) == 6912
    assert decode(data[0x26CB:0x2C6B]) == decoded
    screen = bytearray(6912)
    for index, value in enumerate(decoded['data']):
        screen[physical(0x4000+index)-0x4000] = value
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/IntroScreenVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['original_physical_screen_sha256'] == hashlib.sha256(screen).hexdigest()
    assert screen != initial
    cases = 0
    tail_profiles = []
    source_clear_profiles = []
    tail = bytes.fromhex('cd3c6e caee68 3c be caee68 e5 dde1 dd7e08 fe43 28')
    assert data[0x2CEC:0x2D00] == tail and len(data) == 0x2D00
    for flags, displacement in ((0, 0), (0x55, 0x80), (255, 0x7F)):
        memory = original_memory()
        memory[0x9000] = displacement
        expected = list(memory)
        # Расчёт результата переноса загрузчика и первого экрана до следующего LD HL,8931.
        expected[0x5D3B:0x5E3B] = memory[0x65B7:0x66B7]
        expected[0x4000:0x5B00] = initial
        simulator, _ = execute(memory, {'PC': 0x6500, 'AF': flags}, stop=0x651D)
        assert memory == expected
        # Расчёт второго копирования, код и поток переносятся вместе с неизученным продолжением RAM.
        expected[0x6E31:0x8931] = memory[0x8931:0xA431]
        execute(memory, {'PC': 0x651D, 'AF': flags}, stop=0x6528)
        assert memory == expected
        assert bytes(memory[0x6ECB:0x746B]) == data[0x26CB:0x2C6B]
        source_clear_profiles.append(check_source_clear_after_transfer(memory, displacement))
        # Проверка границы файла и первого CALL, после него начинается чужой контекст распаковщика.
        assert bytes(memory[0x74EC:0x7500]) == tail and memory[0x7500] == displacement
        assert memory[0x6E3C] == 0x19 and memory[0x68EE] == 0x00
        sim, _ = execute(memory, {'PC': 0x74EC}, stop=0x6E3C, limit=2)
        assert sim.registers[SP] == 0xBFFC and word(memory, 0xBFFC) == 0x74EF
        # Изолированная проверка JR Z с операндом из RAM за последним дисковым байтом.
        target = 0x7501 + int.from_bytes(bytes((displacement,)), 'little', signed=True)
        for flag_z, next_pc in ((0, 0x7501), (0x40, target)):
            sim, _ = execute(memory, {'PC': 0x74FF, 'AF': flag_z}, stop=next_pc, limit=2)
            assert sim.registers[PC] == next_pc and sim.registers[SP] == 0xBFFE
        tail_profiles.append(dict(ram_9000=displacement, runtime_7500=memory[0x7500],
                                  taken_branch_target=target))
        cases += 1
    result = dict(passed=True, total_cases=cases, initial_screen_bytes=6912,
                  packed_stream_bytes=1440, stream_unused_last_bits=3,
                  original_allocation_tail_bytes=149,
                  source_clear_after_transfer_profiles=source_clear_profiles,
                  detached_prefix_start=0x74EC, detached_prefix_bytes=len(tail),
                  detached_prefix_call_enters_unpacker_interior=0x6E3C,
                  detached_prefix_jp_target_before_generation=0x68EE,
                  detached_prefix_displacement_profiles=tail_profiles,
                  detached_call_with_prepared_unpack_registers=check_detached_unpack_return(memory, screen),
                  detached_attribute_jump=check_detached_attribute_jump(memory),
                  detached_relative_target_cases=check_detached_relative_targets(memory),
                  detached_prefix_full_contract_proved=False,
                  initial_screen_sha256=hashlib.sha256(initial).hexdigest(),
                  decoded_screen_sha256=hashlib.sha256(screen).hexdigest(),
                  both_actual_loader_copies_executed=True, full_flat_ram_compared=True,
                  physical_bank_mapping_separately_proved=False,
                  whole_intro_executed=False, assembly_executed=False,
                  irq_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/IntroScreenResourcesVerification.json').write_text(
        json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
