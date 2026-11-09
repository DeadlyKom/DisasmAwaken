"""Только доказанные записи участка A981..AA89, адрес без банка не определяет изменяемую инструкцию."""
from functools import cache
import json
from pathlib import Path


GROUPS = (
    (0xD408, (0xD408,)),
    (0xD6CC, (0xD6CC, 0xD77A, 0xD7C1, 0xD82D, 0xDA61, 0xDA9E, 0xC09F, 0xC13A, 0xD138,
        0xD1BA, 0xC1DC, 0xC2B8, 0xC301, 0xC370, 0xC3D5, 0xC44E, 0xC545, 0xC649, 0xC6B2,
        0xD222, 0xC787, 0xC820, 0xC92F, 0xD3CF, 0xD3F9, 0xD3FE, 0xD53B, 0xCA96, 0xD67D,
        0xCB9F, 0xCBA4, 0xCC77, 0xCCE5, 0xCD79, 0xCDC3, 0xCE28, 0xCE6C, 0xCE9D, 0xCF47,
        0xCF9C, 0xCFEF, 0xD083, 0xD0C6, 0xD0CB, 0xD0D0, 0xD0D5)),
    (0xD873, (0xD873, 0xD877, 0xD87B, 0xD87F, 0xD883, 0xD887, 0xD88B, 0xD88F, 0xC243,
        0xC247, 0xC5CA, 0xC5E7, 0xC672, 0xC6AE, 0xD34D, 0xD355, 0xD359, 0xD2DE, 0xD2FD,
        0xC733, 0xC765, 0xC9A2, 0xC9C4, 0xCA24, 0xCA2F, 0xD5C9, 0xD5D1, 0xCB29, 0xCB39,
        0xCE0E, 0xCE1C, 0xD0F2, 0xD0F6)))
HEADER_ADDRESSES = frozenset(target for _, targets in GROUPS for target in targets)
GROUP_ENTRIES = (0xA986, 0xA98E, 0xAA1D)


@cache
def header_names():
    """Имена полей физических записей OBJECT3D, совпадения из других банков исключены."""
    root = Path(__file__).resolve().parents[3]
    packets = json.loads((root / 'Tools/Disasm/Reports/ActionModelPacketsVerification.json').read_bytes())
    names = {}
    for packet in packets['packets']:
        for index, primitive in enumerate(packet['records']):
            address = 0xC000 + primitive['offset']
            if address in HEADER_ADDRESSES:
                assert primitive['kind'] == 'face' and address not in names
                names[address] = f"ActionModels.R{packet['offset']:04X}_{index:02X}.Header"
    assert names.keys() == HEADER_ADDRESSES
    return names


def name_instruction(region, address, operation):
    if region != 'Action' or not 0xA986 <= address < 0xAA85:
        return operation
    for (source, targets), start in zip(GROUPS, GROUP_ENTRIES):
        if address == start:
            return operation.replace(f'#{source:04X}', '@' + header_names()[source])
        if address == start + 3:
            return operation.replace('#60', '@ActionPacketRendererConst.MaterialToggle')
        delta = address - start - 5
        if 0 <= delta < 3 * len(targets) and delta % 3 == 0:
            target = targets[delta // 3]
            return operation.replace(f'#{target:04X}', '@' + header_names()[target])
    return operation


def records(regions):
    region = next(r for r in regions if r['name'] == 'Action')
    instructions = {i['address']: i for i in region['instructions']}
    assert instructions[0xA981]['operation'] == 'LD A,#14'
    assert instructions[0xA983]['operation'] == 'CALL #AB1B'
    assert instructions[0xAA85]['operation'] == 'LD A,#10'
    assert instructions[0xAA87]['operation'] == 'CALL #AB1B'
    result = []
    for (source, targets), start in zip(GROUPS, GROUP_ENTRIES):
        assert instructions[start]['operation'] == 'LD A,(#' + format(source, '04X') + ')'
        assert instructions[start + 3]['operation'] == 'XOR #60'
        for index, target in enumerate(targets):
            writer = start + 5 + 3 * index
            instruction = instructions[writer]
            assert instruction['operation'] == 'LD (#' + format(target, '04X') + '),A'
            result.append(dict(region='Action', writer=writer, writer_bank=2, writer_slot=17,
                writer_offset=instruction['offset'], path='Source/Action/UpdateFrame.asm', target=target,
                target_bank=4, target_slot=24, target_offset=target - 0xC000, size=1,
                value_source_bank=4, value_source=source, xor_mask=0x60,
                target_kind='OBJECT3D_resource_byte', bank0_instruction_at_same_address_not_written=True))
    assert len(result) == 80
    return result


def qualify_mutations(mutations, regions):
    proved = {(r['region'], r['writer'], r['target']) for r in records(regions)}
    # Удаление только ложных совпадений банкового адреса, сами записи сохранены в отдельном реестре.
    removed = [m for m in mutations if (m['region'], m['writer'], m['target']) in proved]
    mutations[:] = [m for m in mutations if (m['region'], m['writer'], m['target']) not in proved]
    return removed
