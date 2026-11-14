"""Сохраняет двенадцать исходных байтов, прочитанных ROM по IY+7."""
import json

from ClassifyActionNoiseIrqAliases import KEYBOARD_READS
from ClassifyStationWorkspaceResources import ROOT, publish


ORIGIN = 0x6000
GAPS = (
    (0x9A22, 0x9A60, (0xFA27,)),
    (0x9D05, 0x9D0E, (0xFD07, 0xFD0A)),
    (0x9D0F, 0x9D3D, (0xFD14,)),
    (0x9D5E, 0x9D7C, (0xFD63,)),
    (0x9DA0, 0x9DBB, (0xFDA5,)),
    (0x9E25, 0x9E5F, (0xFE2A,)),
    (0x9E64, 0x9E7F, (0xFE65,)),
    (0x9E80, 0x9E9E, (0xFE85,)),
    (0x9ED5, 0x9F01, (0xFEDA,)),
    (0x9F02, 0x9F13, (0xFF07,)),
    (0x9F41, 0x9F7E, (0xFF45,)),
)


def unknown(start, end):
    return (start, end, f'Source/Resources/17_ACTION/Unclassified{start:04X}_{end:04X}.bin',
            None, 'Unknown, назначение соседних байтов не установлено')


def split_resources():
    for start, end, addresses in GAPS:
        cursor = start
        for address in addresses:
            offset = address - ORIGIN
            assert cursor < offset < end
            yield unknown(cursor, offset)
            yield (offset, offset + 1, f'Source/Action/Resources/InitialNoiseIrqByte{address:04X}.bin',
                   'INITIAL_ACTION_NOISE_IRQ_ALIAS',
                   f'Исходный байт #{address:04X}, ROM читает его через IY+7 при декодировании клавиши')
            cursor = offset + 1
        assert cursor < end
        yield unknown(cursor, end)


RESOURCES = tuple(split_resources())


if __name__ == '__main__':
    name = 'ActionNoiseExitVerification.json'
    report = json.loads((ROOT / 'Tools/Disasm/Reports' / name).read_bytes())
    expected = {0xFD43, 0xFD82, *(address for _, _, addresses in GAPS for address in addresses)}
    assert report['passed'] and len(expected) == 14
    profiles = report['timed_rom_irq']['profiles']
    assert {profile['rom'] for profile in profiles} == {'48.rom', '128-1.rom'}
    for profile in profiles:
        key = profile['pressed_key_tail']
        assert key['seeds_checked'] == 256 and key['no_frames_wrap']
        assert key['space_pressed_at_second_irq'] and len(key['cases_with_tail_accesses']) == 15
        accesses = [access for case in key['cases_with_tail_accesses'] for access in case['accesses']]
        assert {row['address'] for row in accesses
                if row['mode'] == 'read' and row['pc'] == 0x02FC} == expected
        assert {row['address'] for row in accesses
                if row['mode'] == 'write' and row['pc'] == 0x030B and row['value'] == 0x20} == KEYBOARD_READS
    publish(slot=17, origin=ORIGIN, ranges=tuple((start, end) for start, end, _ in GAPS),
            resources=RESOURCES, tag='ActionNoiseKeyMode', resource_module='ClassifyActionNoiseKeyMode',
            resource_name='ACTION_NOISE_KEY_MODE',
            proof=dict(verification=name, bank=0, read_pc=0x02FC, rom_profiles=2,
                       native_alias_reachability_proved=False))
