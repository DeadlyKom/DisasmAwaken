"""Поиск шаблона CONTROL в физическом образе и декодированных потоках HR."""
from hashlib import sha256
import json

from CheckIntro import ROOT
from PackedResourceCodec import decode


def occurrences(data, needle):
    start = 0
    while (offset := data.find(needle, start)) >= 0:
        yield offset
        start = offset + 1


def main():
    disk = (ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes()
    control = (ROOT / 'Tools/Disasm/Extracted/Active/23_CONTROL.C.bin').read_bytes()
    template = control[:127]
    length = 0xDB01 - 0xDADE
    assert template[length - 1:length + 2] == bytes.fromhex('01 00 00')
    prefix, suffix = template[:length], template[length + 2:]

    def template_copies(data):
        return [dict(offset=offset, length_word=int.from_bytes(data[offset + length:offset + length + 2], 'little'))
                for offset in occurrences(data, prefix)
                if data[offset + length + 2:offset + len(template)] == suffix]

    raw_copies = template_copies(disk)
    assert len(raw_copies) == 1 and raw_copies[0]['length_word'] == 0
    assert disk[raw_copies[0]['offset']:raw_copies[0]['offset'] + len(control)] == control
    valid, implausible, rejected = [], [], []
    for offset in occurrences(disk, b'HR'):
        expanded = int.from_bytes(disk[offset + 2:offset + 4], 'little')
        packed = int.from_bytes(disk[offset + 4:offset + 6], 'little')
        if not 7 <= expanded <= 0xFFFF or not 15 <= packed <= len(disk) - offset:
            implausible.append(offset)
            continue
        try:
            data = decode(disk[offset:offset + packed], disk[offset + packed:offset + packed + 2])['data']
        except (IndexError, AssertionError):
            rejected.append(offset)
            continue
        assert len(data) == expanded
        valid.append(dict(disk_offset=offset, packed_bytes=packed, decoded_bytes=expanded,
                          sha256=sha256(data).hexdigest(), template_copies=template_copies(data),
                          legacy_loader_offsets=list(occurrences(data, control[127:315]))))
    assert len(valid) == 21 and sum(row['decoded_bytes'] == 6912 for row in valid) == 20
    assert (valid[0]['disk_offset'], valid[0]['packed_bytes'], valid[0]['decoded_bytes']) == (0x1303, 9350, 40960)
    assert not any(row['template_copies'] or row['legacy_loader_offsets'] for row in valid)
    report = dict(passed=True, physical_disk_bytes=len(disk), length_operand_masked=True,
                  raw_copies=raw_copies, valid_hr_streams=valid, rejected_hr_offsets=rejected,
                  implausible_hr_offsets=implausible, headerless_streams_or_other_codecs_covered=False,
                  temporary_payload_or_runtime_relocation_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsTemporaryModulePackedCandidates.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, raw_copies=raw_copies, valid_hr_streams=len(valid),
                          rejected_hr_candidates=len(rejected), implausible_hr_headers=len(implausible)), indent=2))


if __name__ == '__main__':
    main()
