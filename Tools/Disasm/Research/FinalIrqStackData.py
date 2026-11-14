"""Физические слова временного стека обработчика прерываний FINALF."""
from FinalSyncAndPreviewRecord import parse_records, render_records


FIELDS = (
    ('SavedAF', 2, 'слово альтернативного AF после обмена в обработчике'),
    ('ResumeAddress', 2, 'адрес продолжения генерируемой цепочки после HALT'),
)
TABLES = (
    (29, 0x6000, ('FinalIrqFrame', 'Source/Final/Data/IrqFrame.asm',
                  0x0192, 0x0196, 'FFinalIrqFrame', FIELDS, ('Value',))),
)
BINDINGS = ()
REQUIRED_REPORTS = ('FinalCycleVerification',)
DOCUMENT = 'FinalCycle'
TAG = 'FinalIrqStackData'


def validate_sources(sources):
    data = sources[29]
    assert data[0x0192:0x0196] == bytes(4)
    assert data[0x016C:0x017A] == bytes.fromhex('F3 08 F5 01 FD 7F 3E 00 ED 79 F1 08 FB C9')
    return dict(irq_stack_bottom=0x6192, irq_stack_top=0x6196, irq_stack_frames_per_cycle=2)


def render(source, origin, table):
    text, labels = render_records(source, table, origin)
    return text.replace('[подготовка и обход объектов](../../../Docs/PreviewQueueBuild.md)',
                        '[временный стек прерывания](../../../Docs/FinalCycle.md)'), labels


def parse(text, origin, table):
    return parse_records(text, table, origin)


def structures():
    return '''                struct FFinalIrqFrame
SavedAF         dw #0000                                                        ; альтернативный AF на время записи в порт
ResumeAddress   dw #0000                                                        ; адрес возврата из IM 2 в генерируемую цепочку
                ends
                assert FFinalIrqFrame == 4
                assert FFinalIrqFrame.SavedAF == 0
                assert FFinalIrqFrame.ResumeAddress == 2
'''
