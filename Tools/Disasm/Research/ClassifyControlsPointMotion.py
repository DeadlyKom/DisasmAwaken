"""Точечный выпуск CB00 после проверки полного алгоритма и четырёх встроенных умножителей."""
import json
import re
import ControlsPointMotionFacts as facts
from ClassifyControlsTextDisplay import main, ROOT
from ValidateNotes import validate_notes


if __name__ == '__main__':
    reports = ROOT / 'Tools/Disasm/Reports'
    # Проверка доказательств полного прохода и арифметических ядер перед публикацией.
    proof = json.loads((reports / 'ControlsPointMotionVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['whole_cb00_in_documented_domain']
    assert proof['original_action_sine_page_additionally_checked'] and proof['total_cases'] == 3712
    assert json.loads((reports / 'ControlsPointProductsVerification.json').read_text('utf-8'))['passed']
    flow = next(r for r in json.loads((reports / 'ControlFlow.json').read_text('utf-8')) if r['name'] == 'Controls')
    validate_notes([flow], {'Controls': facts.COMMENTS})
    # Проверка наличия точного смыслового комментария у каждого условного перехода и выхода.
    for instruction in flow['instructions']:
        if 0xCB00 <= instruction['address'] < 0xCE16 and re.match(r'^(JP|JR|RET) (NZ|Z|NC|C|PO|PE|P|M)\b', instruction['operation']):
            assert facts.COMMENTS[instruction['address']][1], instruction
    path = ROOT / 'Includes/Const/Include.inc'
    before = path.read_bytes()
    text = before.decode('utf-8')
    assert 'module BufferPointMotionConst' not in text
    block = '\n                ; Центр и фаза исходного табличного преобразования точек\n                module BufferPointMotionConst\n'
    for name, value, note in (('CenterY', 0x30, 'центр Y в исходном преобразовании'),
                              ('CenterX', 0x80, 'центр X в исходном преобразовании'),
                              ('SinePage', 0x99, 'страница исходной синусоиды из ACTION'),
                              ('QuarterCycle', 0x40, 'четверть 256-элементного периода для косинуса')):
        block += name.ljust(16) + ('equ #' + format(value, '02X')).ljust(64) + '; ' + note + '\n'
    block += '                endmodule\n\n'
    # Сохранение прежнего файла констант отдельно от кандидата до точечного добавления модуля.
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsPointMotionConstants/Includes/Const/Include.inc'
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsPointMotionConstants/Includes/Const/Include.inc'
    assert not history.exists() and not candidate.exists()
    result = text.replace('                endif', block + '                endif').encode('utf-8')
    history.parent.mkdir(parents=True, exist_ok=True)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    history.write_bytes(before)
    candidate.write_bytes(result)
    assert path.read_bytes() == before
    path.write_bytes(result)
    main(facts, 'ControlsPointMotion', 'ControlsPointMotion', (
        ('YControl', 0x9B95, 'управление проходом Y'),
        ('XControl', 0x9B96, 'управление проходом X'),
        ('TurnControl', 0x9B97, 'отрицание задаёт индекс синусоиды'),
        ('YWrapOffset', 0xCB2B, 'исходное нулевое смещение нового Y'),
        ('XWrapOffset', 0xCBC4, 'исходное нулевое смещение нового X'),
        ('YCosCoeff', 0xCC7E, 'операнд косинуса для нового Y'),
        ('XSinCoeff', 0xCCD2, 'операнд синуса для нового Y'),
        ('XCosCoeff', 0xCD49, 'операнд косинуса для нового X'),
        ('YNegSinCoeff', 0xCD9D, 'операнд отрицательного синуса для нового X'),
        ('YRespawnCall', 0xCD31, 'операнд CALL при недопустимом Y'),
        ('XRespawnCall', 0xCDFC, 'операнд CALL при недопустимом X'),
        ('TurnYStore', 0xCE0B, 'отложенный новый Y, операнд LD (HL), n')))
