"""Публикация подготовителя с отдельным кандидатом и сохранением оригинальных инструкций."""
import json
import ControlsSmallMasksFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__=='__main__':
    assert json.loads((ROOT/'Tools/Disasm/Reports/ControlsSmallMaskTablesClassification.json').read_text('utf-8'))['passed']
    path=ROOT/'Includes/Const/Include.inc'
    before=path.read_bytes()
    text=before.decode('utf-8')
    assert 'module SmallMaskConst' not in text
    block=('\n                ; Поля упакованной затравки масок малой фигуры\n'
        '                module SmallMaskConst\n'
        'CountMask       equ #07                                                         ; числовое поле количества арифметических сдвигов\n'
        'PixelsMask      equ #F8                                                         ; начальные пиксели до сдвигов и повторов\n'
        '                endmodule\n\n')
    history=ROOT/'Tools/Disasm/Research/History/BeforeControlsSmallMaskConst/Includes/Const/Include.inc'
    assert not history.exists()
    history.parent.mkdir(parents=True,exist_ok=True)
    history.write_bytes(before)
    if b'\r\n' in before:
        block=block.replace('\n','\r\n')
    assert path.read_bytes()==before
    path.write_bytes(text.replace('                endif',block+'                endif').encode('utf-8'))
    main(facts,'ControlsSmallMasks','ControlsSmallMasks',())
