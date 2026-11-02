"""Публикация доказанного сравнения с именованными полями динамических записей."""
import ControlsComponentCompareFacts as facts
from ClassifyControlsTextDisplay import main,ROOT


if __name__=='__main__':
    # Добавление формата указуемой записи, статические экземпляры и новая RAM не создаются.
    for relative,marker,block in (
        ('Includes/Structs/Include.inc','struct FComponent24',
            '\n                ; Динамическая трёхбайтовая запись сравниваемого компонента\n'
            '                struct FComponent24\n'
            'Low             db #00                                                          ; младший байт, CompareComponents его не читает\n'
            'Middle          db #00                                                          ; средний байт числового ключа\n'
            'High            db #00                                                          ; старшая часть, разряд 7 исключается перед сравнением\n'
            '                ends\n                assert FComponent24 == 3\n\n'),
        ('Includes/Const/Include.inc','module ComponentCompareConst',
            '\n                ; Исходная маска и порог прямого допуска сравнения компонентов\n'
            '                module ComponentCompareConst\n'
            'HighMask        equ #7F                                                         ; разряд 7 исключён, младшие семь разрядов задают число\n'
            'DirectLimit     equ #0A                                                         ; меньшая старшая часть сразу возвращает NZ\n'
            '                endmodule\n\n')):
        path=ROOT/relative
        before=path.read_bytes()
        text=before.decode('utf-8')
        assert marker not in text
        history=ROOT/'Tools/Disasm/Research/History/BeforeControlsComponentCompareFormat'/relative
        assert not history.exists()
        history.parent.mkdir(parents=True,exist_ok=True)
        history.write_bytes(before)
        if b'\r\n' in before:
            block=block.replace('\n','\r\n')
        assert path.read_bytes()==before
        path.write_bytes(text.replace('                endif',block+'                endif').encode('utf-8'))
    main(facts,'ControlsComponentCompare','ControlsComponentCompare',())
