"""Реальные два копирования загрузчика и точная граница экранного потока, без сборки."""
import hashlib
import json
from CheckIntro import ROOT, original_memory, execute
from IntroScreenCodec import decode, physical
from IntroScreenResources import render_attributes, parse_attributes


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
    for flags in (0, 0x55, 255):
        memory = original_memory()
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
        cases += 1
    result = dict(passed=True, total_cases=cases, initial_screen_bytes=6912,
                  packed_stream_bytes=1440, stream_unused_last_bits=3,
                  original_allocation_tail_bytes=149,
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
