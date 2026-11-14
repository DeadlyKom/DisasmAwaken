"""Физическая сверка двух блоков, чьи имена сохранены в 3DTABS."""
import re


BLOCKS = (
    (0x3B98, 0x3BA1, 'Source/Action/Data/ArchivedEyeState.asm'),
    (0x3BB3, 0x3BBD, 'Source/Action/Data/ArchivedSpawnChances.asm'),
)
FIELDS = {
    'FArchivedEyeState': dict(EyeX=0, EyeY=2, EyeZ=4, StpA=6, StpB=7, StpG=8),
    'FArchivedSpawnChances': dict(Pirates=0, Civilians=1, Police=2, Military=3, Legion=4,
                                  SecondPirates=5, Ufo=6, SecondUfo=7, Hermit=8),
}
LABELS = {
    'ActionArchivedEyeState.Value': 0x9B98,
    'ActionArchivedSpawnChances.ParameterTail': 0x9BB3,
    'ActionArchivedSpawnChances.Value': 0x9BB4,
}


def verify_archived_fields(root, action):
    labels = {}
    for start, end, path in BLOCKS:
        text = (root / path).read_text('utf-8')
        code = '\n'.join(line.split(';', 1)[0] for line in text.splitlines())
        module = re.search(r'\bmodule (Action\w+)', code)[1]
        records = re.finditer(r'(?m)^(\w+):\s+(db #[0-9A-F]{2}|FArchived\w+\s*\{[^}]+\})', code)
        data = bytearray()
        for record in records:
            label, declaration = record.groups()
            labels[module + '.' + label] = 0x6000 + start + len(data)
            for literal in re.findall(r'#([0-9A-F]+)', declaration):
                assert len(literal) in (2, 4)
                data.extend(int(literal, 16).to_bytes(len(literal) // 2, 'little'))
        assert data == action[start:end]
    assert labels == LABELS
