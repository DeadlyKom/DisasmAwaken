"""Сохраняет исходный байт, который ROM проверяет по IY+30 при выборе регистра."""
import json

from ClassifyActionNoiseKeyMode import unknown
from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    unknown(0x9DA6, 0x9DAB),
    (0x9DAB, 0x9DAC, 'Source/Action/Resources/InitialNoiseIrqByteFDAB.bin',
     'INITIAL_ACTION_NOISE_IRQ_ALIAS', 'Исходный байт #FDAB, ROM проверяет бит 3 через IY+#30 при вводе буквы'),
    unknown(0x9DAC, 0x9DBB),
)


if __name__ == '__main__':
    verification = 'ActionNoiseLetterCaseVerification.json'
    report = json.loads((ROOT / 'Tools/Disasm/Reports' / verification).read_bytes())
    assert report['passed'] and report['flag_value_from_original_rom']
    assert (report['target'], report['flag'], report['read_pc'], report['bank']) == (0xFDAB, 0xFD7C, 0x035A, 0)
    assert {profile['rom'] for profile in report['profiles']} == {'48.rom', '128-1.rom'}
    for profile in report['profiles']:
        original = profile['profiles'][1]
        assert original['rom_frame_increments'] == list(range(1, 9))
        assert original['test_accesses'] == [['read', 0x035A, 0xFDAB, 0]]
        assert original['key_value'] == 0x61
    publish(slot=17, origin=0x6000, ranges=((0x9DA6, 0x9DBB),),
            resources=RESOURCES, tag='ActionNoiseLetterCase', resource_module='ClassifyActionNoiseLetterCase',
            resource_name='ACTION_NOISE_LETTER_CASE', proof=dict(verification=verification, bank=0,
                read_pc=0x035A, flag_written_by_rom=True, native_alias_reachability_proved=False))
