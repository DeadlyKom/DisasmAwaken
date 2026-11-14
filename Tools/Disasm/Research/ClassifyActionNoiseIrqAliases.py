"""Исходные байты хвоста ACTION, которые адресует ROM во время шумового цикла."""

import json

from ClassifyStationWorkspaceResources import ROOT, publish


ORIGIN = 0x6000
START, END = 0x9866, 0x9FDE
KEYBOARD_READS = frozenset((0xFA21, 0xFD01, 0xFD04, 0xFD0E, 0xFD3D, 0xFD5D, 0xFD7C,
                            0xFD9F, 0xFE24, 0xFE5F, 0xFE7F, 0xFED4, 0xFF01, 0xFF3F))
FRAME_INCREMENTS = frozenset((0xFA60, 0xFD40, 0xFD43, 0xFD4D, 0xFD7C, 0xFD9C, 0xFDBB,
                              0xFDDE, 0xFE63, 0xFE9E, 0xFEBE, 0xFF13, 0xFF40, 0xFF7E))


def resources():
    cursor = START
    for address in sorted(KEYBOARD_READS | FRAME_INCREMENTS):
        offset = address - ORIGIN
        if cursor < offset:
            yield (cursor, offset, f'Source/Resources/17_ACTION/Unclassified{cursor:04X}_{offset:04X}.bin',
                   None, 'Unknown, назначения соседних байтов не установлены')
        if address in KEYBOARD_READS and address in FRAME_INCREMENTS:
            role = 'ROM читает бит 4 или увеличивает байт при разных значениях IY'
        elif address in KEYBOARD_READS:
            role = 'ROM 128K читает бит 4 при смещённом IY'
        else:
            role = 'ROM увеличивает байт при переполнении FRAMES и смещённом IY'
        yield (offset, offset + 1, f'Source/Action/Resources/InitialNoiseIrqByte{address:04X}.bin',
               'INITIAL_ACTION_NOISE_IRQ_ALIAS', f'Исходный байт #{address:04X}, {role}')
        cursor = offset + 1
    assert cursor < END
    yield (cursor, END, f'Source/Resources/17_ACTION/Unclassified{cursor:04X}_{END:04X}.bin',
           None, 'Unknown, назначение оставшихся байтов не установлено')


RESOURCES = tuple(resources())


if __name__ == '__main__':
    report = json.loads((ROOT / 'Tools/Disasm/Reports/ActionNoiseExitVerification.json').read_bytes())
    proof = report['timed_rom_irq']
    assert report['passed'] and proof['actual_rom_irq_executed']
    profiles = proof['profiles']
    assert {row['address'] for profile in profiles for row in
            profile['tail_aliases_with_prepared_refresh_and_frames']} == FRAME_INCREMENTS
    assert {row['address'] for profile in profiles for row in
            profile['keyboard_flag_aliases_with_prepared_refresh']} == KEYBOARD_READS
    assert len(KEYBOARD_READS | FRAME_INCREMENTS) == 27
    publish(slot=17, origin=ORIGIN, ranges=((START, END),), resources=RESOURCES,
            tag='ActionNoiseIrqAliases', resource_module='ClassifyActionNoiseIrqAliases',
            resource_name='ACTION_NOISE_IRQ_ALIASES',
            proof=dict(physical_bank=0, keyboard_flag_targets=14, frame_counter_targets=14,
                       original_rom_irq_executed=True, native_alias_reachability_proved=False))
