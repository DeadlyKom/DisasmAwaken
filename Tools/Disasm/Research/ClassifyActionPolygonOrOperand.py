"""Отдельный OR по 8D5B, его парный AND перекрывает существующее поле FaceGate."""

import json

from ClassifyStationWorkspaceResources import ROOT, publish


RESOURCES = (
    (0x2D5B, 0x2D5C, 'Source/Action/Resources/OddRightPhase2Mode5Or.bin',
     'POLYGON_LITERAL_OR_OPERAND',
     'Буквальный операнд OR при индексе 5, правой фазе 2 и странице 8D'),
)


if __name__ == '__main__':
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/ActionPolygonExtraMaskPairsVerification.json').read_bytes())
    assert proof['passed'] and 0x8D5B in proof['mask_addresses']
    publish(slot=17, origin=0x6000, ranges=((0x2D5B, 0x2D5C),), resources=RESOURCES,
            tag='ActionPolygonOrOperand', resource_module='ClassifyActionPolygonOrOperand',
            resource_name='ACTION_POLYGON_OR_OPERAND',
            proof=dict(read_address=0x8D5B, paired_and_operand_overlaps_face_gate=True))
