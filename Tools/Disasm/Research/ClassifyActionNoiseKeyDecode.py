"""Публикует исходный байт, прочитанный декодером клавиши через смещённый IY."""
import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x9D7D, 0x9D82, 'Source/Resources/17_ACTION/Unclassified9D7D_9D82.bin', None,
     'Unknown, назначение соседних байтов не установлено'),
    (0x9D82, 0x9D83, 'Source/Action/Resources/InitialNoiseIrqByteFD82.bin', 'INITIAL_ACTION_NOISE_IRQ_ALIAS',
     'Исходный байт #FD82, ROM 128K читает его через IY+7 при декодировании клавиши'),
    (0x9D83, 0x9D9C, 'Source/Resources/17_ACTION/Unclassified9D83_9D9C.bin', None,
     'Unknown, назначение соседних байтов не установлено'),
)


if __name__ == '__main__':
    name = 'ActionNoiseStationCycleVerification.json'
    report = json.loads((ROOT / 'Tools/Disasm/Reports' / name).read_bytes())
    profile = report['aliased_hook_profile']['flight_transition']
    decode, = profile['tail_key_decode']
    assert report['passed'] and decode['frame'] == 100 and decode['iy'] == 0xFD7B
    assert decode['accesses'][0] == ['read', 0xFD82, 0x02FC]
    assert all(access[0] != 'write' or access[1] != 0xFD82 for access in decode['accesses'])
    publish(slot=17, origin=0x6000, ranges=((0x9D7D, 0x9D9C),), resources=RESOURCES,
            tag='ActionNoiseKeyDecode', resource_module='ClassifyActionNoiseKeyDecode',
            resource_name='ACTION_NOISE_KEY_DECODE',
            proof=dict(verification=name, bank=0, read_pc=0x02FC,
                       native_alias_reachability_proved=False))
