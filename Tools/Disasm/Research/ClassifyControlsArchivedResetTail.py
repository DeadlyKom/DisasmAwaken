"""Публикация точного хвоста архивного шаблона NDATA из CONTROL."""
from hashlib import sha256
import json

from CheckIntro import ROOT


RESOURCES = (
    (0x0148, 0x0150, 'Source/Resources/23_CONTROL/Unclassified0148_0150.bin', None,
     'Unknown, восемь изменённых байтов заголовка, назначение полей ещё не установлено'),
    (0x0150, 0x01BD, 'Source/Controls/Resources/LegacyResetContextTail.bin', 'CONTROL_LEGACY_RESET_CONTEXT_TAIL',
     'Хвост шаблона NDATA для сброса перед возвратом на станцию в раннем CONTROL'),
)


if __name__ == '__main__':
    from CheckStationFlightCycle import payload
    from ClassifyStationWorkspaceResources import publish

    report = json.loads((ROOT / 'Tools/Disasm/Reports/ControlsArchivedHyperEffectVerification.json').read_bytes())
    context = report['reset_context']
    assert report['passed'] and context['exact_suffix_offsets'] == [0x150, 0x1BD]
    assert sha256(payload(23)[0x150:0x1BD]).hexdigest() == context['exact_suffix_sha256']
    publish(slot=23, origin=0xDADE, ranges=((0x148, 0x1BD),), resources=RESOURCES,
            tag='ControlsArchivedResetTail', resource_module='ClassifyControlsArchivedResetTail',
            resource_name='CONTROLS_ARCHIVED_RESET_TAIL', proof=context)
