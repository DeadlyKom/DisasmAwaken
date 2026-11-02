"""Публикация двух полностью доказанных арифметических процедур после отделения хвостов."""
import json
import ControlsSquaresFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__ == '__main__':
    proof=json.loads((ROOT/'Tools/Disasm/Reports/ControlsSquareEntrySplitClassification.json').read_text('utf-8'))
    assert proof['passed']
    # Именование исходных страниц двух плоскостей, память не выделяется.
    path=ROOT/'Includes/Const/Include.inc'
    before=path.read_bytes()
    text=before.decode('utf-8')
    assert 'module ControlsSquareConst' not in text
    block='\n                ; Страницы двух исходных плоскостей квадратов\n                module ControlsSquareConst\n'
    for name,value,note in (('LowPage',0xC3,'младшие байты квадратов индексов 0..255'),('HighPage',0xC4,'старшие байты квадратов тех же индексов')):
        block+=name.ljust(16)+('equ #'+format(value,'02X')).ljust(64)+'; '+note+'\n'
    block+='                endmodule\n\n'
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsSquareConst/Includes/Const/Include.inc'
    assert not history.exists()
    history.parent.mkdir(parents=True,exist_ok=True)
    history.write_bytes(before)
    assert path.read_bytes()==before
    if b'\r\n' in before:
        block=block.replace('\n','\r\n')
    path.write_bytes(text.replace('                endif',block+'                endif').encode('utf-8'))
    main(facts,'ControlsSquares','ControlsSquares',(
        ('SquareDiff',0xD188,'рабочее слово D*D-A*A-Carry по модулю 65536'),))
