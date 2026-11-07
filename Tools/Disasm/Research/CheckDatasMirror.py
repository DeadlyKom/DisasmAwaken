"""Побайтовая связь DATAS с начальным блоком ACTION, без предположения о загрузке DATAS."""
import hashlib
import json

from CheckIntro import ROOT


def main():
    base = ROOT / 'Tools/Disasm'
    action = (base / 'Extracted/Active/17_ACTION.C.bin').read_bytes()
    data = (base / 'Extracted/Active/18_DATAS.C.bin').read_bytes()
    assert len(data) == 0x1C2D and data == action[0x2C00:0x482D]
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
    result = dict(passed=True, total_cases=1, exact_bytes=len(data), action_runtime_start=0x8C00,
                  action_runtime_end_exclusive=0xA82D, sha256=hashlib.sha256(data).hexdigest(),
                  disk_copy_load_path_proved=False, source_spans=spans, assembly_executed=False)
    (base / 'Reports/DatasMirrorVerification.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_spans'}, indent=2))


if __name__ == '__main__':
    main()
