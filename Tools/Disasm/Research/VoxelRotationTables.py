"""Разнесённые байты 256 знаковых коэффициентов поворота VOXAL0."""
from CheckVoxelBasisRotation import coefficients
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'VoxelBasisRotation'
TAG = 'VoxelRotationTables'
REQUIRED_REPORTS = ('VoxelBasisRotationVerification', 'ActionBankedBasisRotationVerification')
BINDINGS = ()
TABLES = tuple(
    (20, 0xC000, (
        'VoxelCosine' + part, f'Source/Voxel/Data/Cosine{part}.asm', start, start + 256,
        'FVoxelCosineByte', (('Value', 1, note),),
        tuple(f'Angle{index:02X}' for index in range(256)),
    ))
    for part, start, note in (
        ('Low', 0x2A00, 'младший байт знакового коэффициента'),
        ('High', 0x2B00, 'старший байт знакового коэффициента'),
    )
)


def validate_sources(sources):
    values = coefficients(sources[20])
    assert (values[0], values[64], values[128], values[192]) == (16384, 0, 49152, 0)
    return dict(split_pages=2, verified_signed_coefficients=256, compared_scale=16384)


def render(source, origin, definition):
    text, labels = render_records(source, definition, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[коэффициенты вращения и накопитель](../../../Docs/VoxelBasisRotation.md)'), labels


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ('                struct FVoxelCosineByte\n'
            'Value           db #00                                                          ; исходный байт коэффициента\n'
            '                ends\n'
            '                assert FVoxelCosineByte == 1\n'
            '                assert FVoxelCosineByte.Value == 0\n')
