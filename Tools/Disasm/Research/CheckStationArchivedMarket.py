"""Сверяет SPECTO, TWRM и CENS2 с исходными байтами STATIONF."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from CheckControlsArchivedHyperEffect import read_entry
from CheckIntro import ROOT


def declarations(lines, label, following):
    start, end = lines.index(label), lines.index(following)
    rows = []
    for line in lines[start + 1:end]:
        match = re.search(rb'\x05g([0-9,]+)(?:;(.*))?$', line)
        if match:
            values = bytes(int(value) for value in match[1].split(b','))
            name = (match[2] or b'').decode('cp866')
            rows.append((values, name))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    args = parser.parse_args()
    digest = sha256(args.archive.read_bytes()).hexdigest()
    assert digest == 'd3a9efb3b7d4dbd9a2c44f5ed4d43801723a2a9f6393e7266c7ebb57c6c3647b'
    with ZipFile(args.archive) as archive:
        _, source, _ = read_entry(archive.read('awk6.trd'), b'DATA_M  a')
    _, station, _ = read_entry((ROOT / 'Tools/Disasm/Disk/original.trd').read_bytes(), b'STATIONFC')
    lines = source.split(b'\r')
    categories = declarations(lines, b'SPECTO', b'TWRM')
    weights = declarations(lines, b'TWRM', b'CENS2')
    rules = declarations(lines, b'CENS2', b'TWRS')
    assert [len(categories), len(weights), len(rules)] == [30, 30, 31]
    assert all(len(value) == 1 for value, _ in categories + weights)
    assert all(len(value) == 2 for value, _ in rules[:30])
    assert rules[30] == (b'\x00', '')
    assert [name for _, name in categories] == [name for _, name in weights] == [name for _, name in rules[:30]]
    assert '0-АГРО,1-КУЛЬТ,2-ТЕХ,3-ОБЩ'.encode('cp866') in source
    for rows, start, end in ((categories, 0x34DC, 0x34FA), (weights, 0x34FA, 0x3518),
                             (rules, 0x3518, 0x3555)):
        assert b''.join(value for value, _ in rows) == station[start:end]
    assert b'\x05iTKOL*2' in b'\r'.join(lines[lines.index(b'TWRS') + 1:lines.index(b'TWRS') + 6])
    assert station[0x3555:0x3592] == bytes(60) + b'\xff'
    report = dict(passed=True, archive_sha256=digest, source='awk6.trd:DATA_M.a',
                  categories_exact_bytes=30, weights_exact_bytes=30, rules_exact_bytes=60,
                  declared_trailing_zero_offset=0x3554, authored_market_rows=30,
                  goods=[name for _, name in categories],
                  final_categories=list(station[0x34F7:0x34FA]),
                  assembly_executed=False, native_execution=False)
    path = ROOT / 'Tools/Disasm/Reports/StationArchivedMarketVerification.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print('DATA_M.a: 30 категорий, 30 кодов веса, 30 правил и отдельный нулевой байт совпадают')


if __name__ == '__main__':
    main()
