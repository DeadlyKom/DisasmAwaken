"""Физический ограничитель исходного списка объектов предпросмотра D3D."""
from PreviewSceneTables import parse as parse_records, render as render_records


DOCUMENT = 'PreviewQueueBuild'
TAG = 'PreviewObjectEnd'
REQUIRED_REPORTS = ('PreviewUnclassifiedAccesses', 'PreviewQueueBuildVerification')
BINDINGS = ()
TABLES = ((6, 0xC000, ('PreviewObjectEnd', 'Source/D3D/Data/PreviewObjectEnd.asm',
    0x0E00, 0x0E02, 'FPreviewObjectEnd', (
        ('Low', 1, 'бит 7 завершает обход при старшем байте 80'),
        ('High', 1, '80 выбирает проверку специального маркера'),
    ), ('Value',))),)


def validate_sources(sources):
    assert sources[6][0x0E00:0x0E02] == b'\x80\x80'
    assert 0x0E00 - 0x0DC0 == 64
    return dict(original_marker=0x8080, original_record_step=64)


def render(source, origin, definition):
    return render_records(source, definition, origin)


def parse(text, origin, definition):
    return parse_records(text, definition, origin)


def structures():
    return ('                struct FPreviewObjectEnd\n'
            'Low             db #80                                                          ; бит 7 означает конец списка при High=80\n'
            'High            db #80                                                          ; старший байт специальной записи\n'
            '                ends\n'
            '                assert FPreviewObjectEnd == 2\n'
            '                assert FPreviewObjectEnd.Low == 0\n'
            '                assert FPreviewObjectEnd.High == 1\n')
