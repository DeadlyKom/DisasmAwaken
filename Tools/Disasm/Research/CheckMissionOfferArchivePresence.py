"""Физические копии текущего предложения в сохранённых версиях Awaken.

Документация: ../../../Docs/MissionOffer.md
"""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckStationFlightCycle import ROOT, payload


def find_all(data, needle):
    start = 0
    while (offset := data.find(needle, start)) >= 0:
        yield offset
        start = offset + 1


def main():
    directory = ROOT / 'Tools/Disasm/Research/References/AuthorArchives'
    manifest = json.loads((directory / 'Manifest.json').read_bytes())
    expected = {row['path']: row for row in manifest['archives']}
    needle = payload(4)[0x38B0:0x38C0]
    assert needle == bytes.fromhex('394b06000000000000000000e8030f01')
    archives, matches, counts = [], [], dict(trd_files=0, scl_files=0)
    for archive_path in sorted(directory.glob('ArchiveAwaken*.zip')):
        path = archive_path.relative_to(ROOT).as_posix()
        digest = sha256(archive_path.read_bytes()).hexdigest()
        assert digest == expected[path]['sha256']
        archives.append(dict(path=path, sha256=digest))
        with ZipFile(archive_path) as archive:
            for member in archive.namelist():
                image = archive.read(member)
                known = next(row for row in expected[path]['members'] if row['name'] == member)
                assert len(image) == known['bytes'] and sha256(image).hexdigest() == known['sha256']
                if member.lower().endswith('.trd'):
                    # Проверка действующих логических файлов, удалённые записи не входят в этот поиск.
                    entries = []
                    for slot in range(128):
                        header = image[slot * 16:(slot + 1) * 16]
                        if header[0] == 0:
                            break
                        if header[0] == 1:
                            continue
                        start = (16 * header[15] + header[14]) * 256
                        size = int.from_bytes(header[11:13], 'little')
                        entries.append((slot, header[:9], image[start:start + size]))
                    counts['trd_files'] += len(entries)
                elif member.lower().endswith('.scl'):
                    assert image[:8] == b'SINCLAIR'
                    entries = []
                    start = 9 + image[8] * 14
                    for slot in range(image[8]):
                        header = image[9 + slot * 14:9 + (slot + 1) * 14]
                        sector_size = header[13] * 256
                        size = int.from_bytes(header[11:13], 'little')
                        assert size <= sector_size and start + sector_size <= len(image)
                        entries.append((slot, header[:9], image[start:start + size]))
                        start += sector_size
                    counts['scl_files'] += len(entries)
                else:
                    continue
                for slot, name, data in entries:
                    for offset in find_all(data, needle):
                        matches.append(dict(archive=archive_path.name, member=member,
                            slot=slot, name=name.decode('cp866'), file_offset=offset))
    assert len(archives) == 4 and len(matches) == 6
    assert {(row['archive'], row['member']) for row in matches} == {
        ('ArchiveAwakenSDC.zip', 'AWAK_SDC.SCL')}
    assert [(row['name'], row['file_offset']) for row in matches] == [
        ('STATIONFC', 0x38B0), ('SAVE1   s', 0x75), ('SAVE2   s', 0x75),
        ('SAVE3   s', 0x75), ('SAVE4   s', 0x75), ('SAVE0   s', 0x75)]
    report = dict(passed=True, original_record_hex=needle.hex(), record_bytes=16,
        archives=archives, logical_files_checked=counts, matches=matches,
        compiled_or_plain_logical_files_only=True,
        compressed_or_runtime_generated_copies_excluded=False,
        absence_of_exact_record_is_not_absence_of_code=True,
        unknown_words_purpose_proved=False, assembly_executed=False,
        native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/MissionOfferArchivePresenceVerification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, logical_files_checked=counts,
                         exact_record_copies=len(matches)), ensure_ascii=False))


if __name__ == '__main__':
    main()
