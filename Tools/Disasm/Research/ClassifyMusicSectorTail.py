"""Именование исходных 215 байтов за логическим концом MUZ1.C, без удаления данных."""
from pathlib import Path
import contextlib, io, json, sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'Tools/Disasm'), str(ROOT/'Tools/Disasm/Research')]
from VerifySources import main as verify


def main():
    def read(stem):
        return json.loads((ROOT/('Tools/Disasm/Reports/'+stem+'.json')).read_text('utf-8'))
    def encoded(value):
        return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    source_map = read('SourceMap')
    item = next(item for item in source_map if item['slot'] == 10 and item['offset'] == 7209)
    assert item['length'] == 215 and item['kind'] == 'unclassified'
    original = ROOT/item['path']
    data = original.read_bytes()
    entry = next(entry for entry in json.loads((ROOT/'Tools/Disasm/Disk/Manifest.json').read_text('utf-8'))['entries'] if entry['slot'] == 10)
    assert entry['length'] == 7209 and entry['allocated_length'] == 7424
    assert data == (ROOT/(entry['path']+'.sectors.bin')).read_bytes()[7209:7424]
    candidate = ROOT/'Tools/Disasm/Research/Candidates/MusicSectorTail'
    history = ROOT/'Tools/Disasm/Research/History/BeforeMusicSectorTail'
    assert not candidate.exists() and not history.exists()
    destination = 'Source/Music/Resources/SectorTail.bin'
    assert not (ROOT/destination).exists()
    old_path = item['path']
    item.update(path=destination, kind='binary_resource', format='TRDOS_SECTOR_TAIL')
    inventory = read('Inventory')
    inventory['physical_bytes_by_kind']['unclassified'] -= 215
    inventory['physical_bytes_by_kind']['binary_resource'] += 215
    inventory['ranges_by_kind']['unclassified'] -= 1
    inventory['ranges_by_kind']['binary_resource'] += 1
    p = ROOT/'Source/Files/10_MUZ1.inc'
    text = p.read_text('utf-8')
    needle = '                ; Unknown, исходные байты вне подтверждённого прямого потока управления\n                incbin "../Resources/10_MUZ1/Unclassified018.bin"'
    assert text.count(needle) == 1
    text = text.replace(needle, '                ; Исходные 215 байтов секторного хвоста за логическим концом MUZ1.C, сохраняются целиком\n                incbin "../Music/Resources/SectorTail.bin"')
    pending = {ROOT/destination: data, p: text.encode('utf-8'), ROOT/'Tools/Disasm/Reports/SourceMap.json': encoded(source_map),
               ROOT/'Tools/Disasm/Reports/Inventory.json': encoded(inventory)}
    before = {p: p.read_bytes() if p.exists() else None for p in pending}
    for p, blob in pending.items():
        c = candidate/p.relative_to(ROOT)
        c.parent.mkdir(parents=True, exist_ok=True)
        c.write_bytes(blob)
    for p, blob in {**{p: blob for p, blob in before.items() if blob is not None}, original: data}.items():
        h = history/p.relative_to(ROOT)
        h.parent.mkdir(parents=True, exist_ok=True)
        h.write_bytes(blob)
    for p, blob in pending.items():
        assert (p.read_bytes() == before[p]) if before[p] is not None else not p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(blob)
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    assert original.resolve().is_relative_to((ROOT/'Source/Resources/10_MUZ1').resolve())
    assert original.read_bytes() == data == (history/original.relative_to(ROOT)).read_bytes()
    original.unlink()
    report = dict(passed=True, logical_length=7209, allocation_length=7424, preserved_sector_tail_bytes=215,
                  source_path=destination, unused_or_discardable_claimed=False, assembly_executed=False)
    (ROOT/'Tools/Disasm/Reports/MusicSectorTailClassification.json').write_bytes(encoded(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
