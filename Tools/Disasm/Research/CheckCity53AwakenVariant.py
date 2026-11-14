"""Побайтовое сравнение трёх встроенных файлов City53 с авторским демо Awaken.

Документация: ../../../Docs/ControlsTemporaryModule.md#каталожная-сверка-приложения-city-53
"""
from hashlib import sha256
import json
from zipfile import ZipFile

from CheckIntro import ROOT


ARCHIVES = ROOT / 'Tools/Disasm/Research/References/AuthorArchives'


def check_scl(blob):
    # Проверка внешнего контейнера, всех выделенных секторов и полной контрольной суммы.
    assert blob[:8] == b'SINCLAIR'
    count = blob[8]
    directory = [blob[9 + 14 * i:23 + 14 * i] for i in range(count)]
    start = 9 + 14 * count
    assert start + sum(row[13] * 256 for row in directory) + 4 == len(blob)
    assert int.from_bytes(blob[-4:], 'little') == sum(blob[:-4]) & 0xFFFFFFFF
    return directory, start


def main():
    city_path = ARCHIVES / 'ArchiveCity53.zip'
    author_path = ARCHIVES / 'ArchiveAwakenAuthor.zip'
    assert sha256(city_path.read_bytes()).hexdigest() == '8e392dbff49f386acdcdc0ebf664fe3f59a86e1ae5d80d95199c28409c9c924a'
    assert sha256(author_path.read_bytes()).hexdigest() == '9f58746be8a339575234f0823d41d0e2481eb75910d9439a10aff90eef4b87a6'
    with ZipFile(city_path) as archive:
        city = archive.read('CITY53.SCL')
    with ZipFile(author_path) as archive:
        author = archive.read('AWAKEN_D.SCL')
    city_directory, _ = check_scl(city)
    directory, source_offset = check_scl(author)
    assert [row[:9] for row in directory] == [b'AWAKEN  B', b'Demo    R', b'Version T']
    rows, contents = [], []
    next_header = None
    for descriptor in directory:
        name = descriptor[:9]
        # Поиск единственного имени и проверка всех 14 байтов соответствующего описателя.
        assert city.count(name) == 1
        header = city.index(name)
        assert city[header:header + 14] == descriptor
        if next_header is not None:
            assert header == next_header
        allocated = descriptor[13] * 256
        logical_length = int.from_bytes(descriptor[11:13], 'little')
        # Граница 22 байта проверяется полным равенством содержимого и стыком соседних записей.
        payload_offset = header + 22
        candidate = city[payload_offset:payload_offset + allocated]
        expected = author[source_offset:source_offset + allocated]
        assert len(candidate) == allocated and candidate == expected
        rows.append(dict(name=name.decode('ascii'), descriptor_hex=descriptor.hex(),
            embedded_header=header, embedded_payload=payload_offset, source_payload=source_offset,
            allocated_bytes=allocated, catalog_length_word=logical_length,
            payload_sha256=sha256(candidate).hexdigest(), differing_bytes=0,
            container_prefix_after_descriptor_hex=city[header + 14:payload_offset].hex()))
        contents.append(candidate)
        next_header = payload_offset + allocated
        source_offset += allocated
    # Восстановление только в памяти исходного SCL, включая каталог и checksum.
    reconstructed = b'SINCLAIR' + bytes([len(directory)]) + b''.join(directory) + b''.join(contents)
    reconstructed += (sum(reconstructed) & 0xFFFFFFFF).to_bytes(4, 'little')
    assert reconstructed == author
    result = dict(passed=True, method='whole_allocated_embedded_payload_and_reconstructed_SCL_comparison',
        city_source_url='https://zxpress.ru/files/CITY53.ZIP',
        city_archive_sha256=sha256(city_path.read_bytes()).hexdigest(),
        city_scl_sha256=sha256(city).hexdigest(), city_scl_checksum_verified=True,
        city_outer_file_count=len(city_directory), author_scl_checksum_verified=True,
        author_scl_sha256=sha256(author).hexdigest(), reconstructed_scl_bytes=len(reconstructed),
        reconstructed_SCL_identical=True, all_allocated_embedded_file_bytes=sum(len(c) for c in contents),
        files=rows, embedded_prefix_size=22, prefix_fields_semantics_proved=False,
        current_Awakenv02_module_recovered=False, applicability_to_current_game_proved=False,
        all_other_city_data_semantically_scanned=False, duplicate_files_extracted=False,
        assembly_executed=False, native_execution=False)
    (ROOT / 'Tools/Disasm/Reports/City53AwakenVariantComparison.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, compared_allocated_bytes=result['all_allocated_embedded_file_bytes'],
        reconstructed_SCL_identical=True, source_scl_sha256=result['author_scl_sha256']), ensure_ascii=False))


if __name__ == '__main__':
    main()
