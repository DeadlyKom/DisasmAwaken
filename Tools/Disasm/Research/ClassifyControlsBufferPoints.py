"""Публикация трёх процедур генератора и XOR-точек."""
import ControlsBufferPointsFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__ == '__main__':
    path = ROOT / 'Includes/Const/Include.inc'
    before = path.read_bytes()
    text = before.decode('utf-8')
    assert 'module BufferPointConst' not in text
    block = '\n                ; Размер таблицы, исходные ограничения координат и страница адресов строк\n                module BufferPointConst\n'
    for name,value,note in (('ByteCount',0x46,'35 физических записей по два байта'),
        ('MinCoordinate',1,'нулевая координата заменяется шагом EdgeStep'),
        ('EdgeStep',2,'шаг коррекции нуля и правой границы X'),
        ('XUpperLimit',0xFE,'X от этого значения уменьшается на два'),
        ('YIndexMask',0x7F,'семибитовый индекс Y, это числовое поле'),
        ('YUpperLimit',0x5F,'Y от этого значения уменьшается на YFold'),
        ('YFold',0x40,'исходное смещение больших значений Y'),
        ('LineHighPage',0x94,'старший байт страницы таблицы HIGH адресов строк')):
        block += name.ljust(16) + ('equ #'+format(value,'02X')).ljust(64) + '; '+note+'\n'
    block += '                endmodule\n'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsBufferPointsConstants/Includes/Const/Include.inc'
    assert not history.exists()
    history.parent.mkdir(parents=True,exist_ok=True)
    history.write_bytes(before)
    assert path.read_bytes() == before
    path.write_text(text.replace('                endif',block+'\n                endif'),encoding='utf-8')
    main(facts,'ControlsBufferPoints','ControlsBufferPoints', (
        ('Seed',0xCA8F,'слово состояния в исходном операнде LD BC,nn'),))
