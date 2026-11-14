"""Поиск шаблона CONTROL в физическом образе и декодированных потоках HR."""
from hashlib import sha256
import json
import re

from CheckIntro import ROOT
from CheckDeletedArticleLoader import decode_hr21
from PackedResourceCodec import decode


def occurrences(data, needle):
    start = 0
    while (offset := data.find(needle, start)) >= 0:
        yield offset
        start = offset + 1


def relocated_patterns(control):
    flow = json.loads((ROOT / 'Tools/Disasm/Reports/ControlFlow.json').read_bytes())
    instructions = [row for region in flow for row in region['instructions']
                    if row['slot'] == 23 and row['offset'] < len(control)]
    masked = set()
    for row in instructions:
        start = row['offset']
        raw = bytes.fromhex(row['hex'])
        assert control[start:start + len(raw)] == raw
        operation = row['operation']
        operand = re.search(r'#([0-9A-F]{4})', operation)
        if len(raw) >= 3 and operand and int(operand[1], 16) >= 0x4000 and not operation.startswith(('JR', 'DJNZ')):
            masked.update((start + len(raw) - 2, start + len(raw) - 1))

    patterns = []
    for row in instructions:
        start = row['offset']
        offsets = range(start, start + 20)
        if start + 20 > len(control) or sum(i not in masked for i in offsets) < 12:
            continue
        pattern = b''.join(b'.' if i in masked else re.escape(bytes((control[i],))) for i in offsets)
        patterns.append((start, re.compile(b'(?=' + pattern + b')', re.S)))
    return patterns


def scan_without_signature(disk, expected_offsets):
    # #6500 входит в результат от #6400, результат заканчивается перед AB23.
    min_unpacked = 0x6500 - 0x6400 + 1
    max_unpacked = 0xAB23 - 0x6400
    # Источник от C600 целиком помещается в выбранное окно банка.
    max_packed = 0x10000 - 0xC600
    candidates = 0
    offsets = set()
    needed_lookahead = set()
    lookahead_trials = 0
    for offset in range(len(disk) - 14):
        unpacked = disk[offset + 2] | disk[offset + 3] << 8
        packed = disk[offset + 4] | disk[offset + 5] << 8
        end = offset + packed
        if not min_unpacked <= unpacked <= max_unpacked or not 15 <= packed <= max_packed or end > len(disk):
            continue
        candidates += 1
        # Z80 пропускает два первых байта, независимый декодер требует сигнатуру.
        data = b'HR' + disk[offset + 2:end]
        try:
            decode(data, b'')
        except AssertionError:
            continue
        except IndexError:
            needed_lookahead.add(offset)
        else:
            offsets.add(offset)
            continue
        # Для уже известного потока достаточно одного подтверждённого значения.
        disk_word = int.from_bytes(disk[end:end + 2], 'little')
        for word in range(0x10000):
            lookahead = (word ^ disk_word).to_bytes(2, 'little')
            lookahead_trials += 1
            try:
                decode(data, lookahead)
            except (AssertionError, IndexError):
                continue
            offsets.add(offset)
            break
    assert offsets == expected_offsets
    return dict(candidate_offsets=candidates, min_unpacked=min_unpacked, max_unpacked=max_unpacked,
                min_packed=15, max_packed=max_packed, successful_offsets=sorted(offsets),
                signatures_required=False, additional_successful_offsets=0,
                offsets_requiring_lookahead=len(needed_lookahead), lookahead_trials=lookahead_trials,
                successful_offsets_with_lookahead_reads=sorted(needed_lookahead & offsets),
                unsuccessful_offsets_tested_with_all_lookahead_words=True)


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
    fragment_size = 12
    original_span = control[:315]
    fragments = [(offset, original_span[offset:offset + fragment_size])
                 for offset in range(len(original_span) - fragment_size + 1)]
    control_offset = raw_copies[0]['offset']
    extra_raw_fragments = [(offset, match) for offset, raw in fragments for match in occurrences(disk, raw)
                           if match != control_offset + offset]
    assert not extra_raw_fragments, extra_raw_fragments
    masked_patterns = relocated_patterns(original_span)
    assert len(masked_patterns) == 144
    for offset, pattern in masked_patterns:
        assert [match.start() for match in pattern.finditer(disk)] == [control_offset + offset]

    def check_no_fragments(data):
        assert not any(raw in data for _, raw in fragments)
        assert not any(pattern.search(data) for _, pattern in masked_patterns)

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
        check_no_fragments(data)
        valid.append(dict(disk_offset=offset, packed_bytes=packed, decoded_bytes=expanded,
                          sha256=sha256(data).hexdigest(), template_copies=template_copies(data),
                          legacy_loader_offsets=list(occurrences(data, control[127:315]))))
    assert len(valid) == 21 and sum(row['decoded_bytes'] == 6912 for row in valid) == 20
    assert (valid[0]['disk_offset'], valid[0]['packed_bytes'], valid[0]['decoded_bytes']) == (0x1303, 9350, 40960)
    assert not any(row['template_copies'] or row['legacy_loader_offsets'] for row in valid)
    archive_streams = []
    for offset in occurrences(disk, b'hr21'):
        packed = int.from_bytes(disk[offset + 6:offset + 8], 'little')
        data = decode_hr21(disk[offset:offset + packed + 8])
        check_no_fragments(data)
        archive_streams.append(dict(disk_offset=offset, packed_bytes=packed, decoded_bytes=len(data),
                                    sha256=sha256(data).hexdigest(), template_copies=template_copies(data),
                                    legacy_loader_offsets=list(occurrences(data, control[127:315]))))
    assert len(archive_streams) == 14
    assert not any(row['template_copies'] or row['legacy_loader_offsets'] for row in archive_streams)
    signature_independent = scan_without_signature(
        disk, {row['disk_offset'] for row in valid if row['decoded_bytes'] == 6912})
    report = dict(passed=True, physical_disk_bytes=len(disk), length_operand_masked=True,
                  raw_copies=raw_copies, valid_hr_streams=valid, rejected_hr_offsets=rejected,
                  valid_hr21_streams=archive_streams,
                  partial_copies=dict(fragment_bytes=fragment_size, template_and_loader_bytes=len(original_span),
                                      starting_offsets_tested=len(fragments), extra_physical_matches=0,
                                      decoded_streams_tested=len(valid)+len(archive_streams), decoded_matches=0),
                  masked_fragments=dict(fragment_bytes=20, minimum_exact_bytes=12,
                                        instruction_aligned_patterns=len(masked_patterns), extra_matches=0),
                  implausible_hr_offsets=implausible, signature_independent_scan=signature_independent,
                  other_codecs_or_runtime_constructed_streams_covered=False,
                  temporary_payload_or_runtime_relocation_proved=False, assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsTemporaryModulePackedCandidates.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, raw_copies=raw_copies, valid_hr_streams=len(valid),
                          valid_hr21_streams=len(archive_streams),
                          rejected_hr_candidates=len(rejected), implausible_hr_headers=len(implausible)), indent=2))


if __name__ == '__main__':
    main()
