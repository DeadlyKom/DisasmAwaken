"""Публикация полного малого рисователя с точным контрактом исходного шаблона."""
import json
import ControlsSmallBodiesFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__=='__main__':
    assert json.loads((ROOT/'Tools/Disasm/Reports/ControlsBodyProjectionClassification.json').read_text('utf-8'))['passed']
    path=ROOT/'Includes/Const/Include.inc'
    before=path.read_bytes()
    text=before.decode('utf-8')
    assert 'module SmallBodyConst' not in text
    block='\n                ; Исходные пределы и фазы малого рисователя\n                module SmallBodyConst\n'
    for name,value,note in (
        ('ModeLimit',4,'первый режим, для которого рисование не выполняется'),('RadiusLimit',9,'исключённый верхний радиус'),('RadiusMin',2,'минимальный допустимый радиус'),
        ('XBias',0x7F,'промежуточный горизонтальный центр и максимум смещения'),('YBias',0x30,'вертикальный центр до применения смещения'),
        ('YMaxOffset',0x48,'максимальное принимаемое смещение Y'),('BytePixels',8,'число пикселей в байте и порог левого отсечения'),
        ('RightClipFrom',0xF8,'X от этого значения исключает правый соседний байт'),('RasterFactor',4,'старший байт до умножения адреса на 32'),
        ('PhaseMask',7,'числовая фаза пикселя внутри байта'),('RowBytes',0x20,'байтовый шаг строки линейного растра'),
        ('LowPagePass',0x60,'исходный пропуск страниц ниже этой границы'),('BufferEndPage',0x8C,'первая страница после линейного растра'),
        ('BufferFirstPage',0x80,'первая страница линейного растра'),('UpperHalfBit',7,'номер разряда верхней половины во внутренних флагах D')):
        assert len(name)<=15
        block+=name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsSmallBodyConst/Includes/Const/Include.inc'
    assert not history.exists()
    history.parent.mkdir(parents=True,exist_ok=True)
    history.write_bytes(before)
    if b'\r\n' in before:
        block=block.replace('\n','\r\n')
    assert path.read_bytes()==before
    path.write_bytes(text.replace('                endif',block+'                endif').encode('utf-8'))
    main(facts,'ControlsSmallBodies','ControlsSmallBodies',(
        ('Mode',0xCEF9,'исходный режим, принимаются только 0..3'),
        ('Pattern',0xD240,'два байта рисунка и XOR-чередования, операнд LD IX, nn'),
        ('LeftMask',0xDA83,'изменяемый операнд старшего байта выровненной маски')))
