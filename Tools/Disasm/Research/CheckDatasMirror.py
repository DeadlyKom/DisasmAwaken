"""Побайтовая связь DATAS с ACTION и фактическая граница чтения TR-DOS."""
from collections import Counter
import hashlib
import json
import re

from CheckIntro import ROOT


def direct_trdos_branches(original, entries, flows):
    direct = re.compile(rb'[\xC3\xCD\xC2\xCA\xD2\xDA\xE2\xEA\xF2\xFA\xC4\xCC\xD4\xDC\xE4\xEC\xF4\xFC]\x13\x3D')
    entry_by_slot = {row['slot']: row for row in entries}
    known = {}
    for region in flows:
        for instruction in region['instructions']:
            if not direct.fullmatch(bytes.fromhex(instruction['hex'])):
                continue
            entry = entry_by_slot[instruction['slot']]
            offset = entry['offset'] + instruction['offset']
            assert not entry['deleted'] and offset not in known
            known[offset] = dict(disk_offset=offset, slot=entry['slot'], file_offset=instruction['offset'],
                                 runtime_address=instruction['address'], region=region['name'],
                                 operation=instruction['operation'])
    active, deleted, outside_catalogue = [], [], []
    for match in direct.finditer(original):
        offset = match.start()
        containing = [row for row in entries
                      if row['offset'] <= offset < row['offset'] + row['allocated_length']]
        if any(not row['deleted'] for row in containing):
            assert offset in known and len(containing) == 1, (offset, containing)
            active.append(known[offset])
        elif containing:
            deleted.append(dict(disk_offset=offset, slots=[row['slot'] for row in containing],
                                hex=match.group().hex()))
        else:
            outside_catalogue.append(dict(disk_offset=offset, hex=match.group().hex()))
    assert len(active) == len(known) == 28
    assert [row['disk_offset'] for row in deleted] == [0x1051, 0x3847]
    assert [row['disk_offset'] for row in outside_catalogue] == [
        0x8752F, 0x8B783, 0x8B798, 0x8B7BA, 0x8BA28, 0x8C38C, 0x8C70F, 0x8C74E]
    return dict(active=active, deleted=deleted, outside_catalogue=outside_catalogue,
                indirect_and_computed_targets_covered=False)


def main():
    base = ROOT / 'Tools/Disasm'
    action = (base / 'Extracted/Active/17_ACTION.C.bin').read_bytes()
    data = (base / 'Extracted/Active/18_DATAS.C.bin').read_bytes()
    assert len(data) == 0x1C2D and data == action[0x2C00:0x482D]
    original = (base / 'Disk/original.trd').read_bytes()
    disk_hash = hashlib.sha256(original).hexdigest()
    manifest = json.loads((base / 'Disk/Manifest.json').read_bytes())
    datas = next(row for row in manifest['entries'] if row['slot'] == 18)
    assert original[datas['offset']:datas['offset'] + len(data)] == data
    key = b'DATAS   C'
    catalogue_address = datas['slot'] * 16
    assert original.find(key) == original.rfind(key) == catalogue_address
    flows = json.loads((base / 'Reports/ControlFlow.json').read_bytes())
    direct_calls = direct_trdos_branches(original, manifest['entries'], flows)
    first_sector = [datas['first_track'], datas['first_sector'] + 1]
    boot = json.loads((base / 'Reports/BootBankFileReadsVerification.json').read_bytes())
    assert boot['passed'] and boot['disk_sha256'] == disk_hash
    flights = [profile['flight_transition'] for profile in boot['intro_transitions']]
    assert len(flights) == 2
    for flight in flights:
        assert not flight['trdos_calls_substituted']
        assert flight['next_file_sector_after_action'] == first_sector
        assert flight['next_file_sector_scratch_address'] == 0x5D25
        assert flight['hyperjump']['data_sectors'] == flight['outbound_data_sectors']
    source_map = json.loads((base / 'Reports/SourceMap.json').read_text(encoding='utf-8'))
    spans = []
    for item in source_map:
        if item['slot'] != 17:
            continue
        start, end = max(item['offset'], 0x2C00), min(item['offset'] + item['length'], 0x482D)
        if start < end:
            assert data[start - 0x2C00:end - 0x2C00] == action[start:end]
            spans.append(dict(datas_offset=start - 0x2C00, length=end - start, action_offset=start,
                              action_kind=item['kind'], action_path=item['path']))
    spans.sort(key=lambda row: row['datas_offset'])
    assert spans[0]['datas_offset'] == 0 and sum(row['length'] for row in spans) == len(data)
    assert all(a['datas_offset'] + a['length'] == b['datas_offset'] for a, b in zip(spans, spans[1:]))
    bytes_by_kind = Counter()
    for row in spans:
        bytes_by_kind[row['action_kind']] += row['length']
    result = dict(passed=True, total_cases=1, exact_bytes=len(data), action_runtime_start=0x8C00,
                  action_runtime_end_exclusive=0xA82D, sha256=hashlib.sha256(data).hexdigest(),
                  original_disk_sha256=disk_hash, bytes_by_action_kind=dict(bytes_by_kind),
                  literal_file_key_offsets=[catalogue_address],
                  direct_trdos_branch_patterns=direct_calls,
                  first_sector_read=dict(track=first_sector[0], sector=first_sector[1], length=256,
                                         scratch=0x5D25, flight_profiles=len(flights),
                                         action_load_and_reload=True),
                  disk_copy_load_path_proved=False, source_spans=spans, assembly_executed=False)
    (base / 'Reports/DatasMirrorVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('source_spans', 'direct_trdos_branch_patterns')},
                     indent=2))


if __name__ == '__main__':
    main()
