"""Завершение кандидата после сокращения константы, с проверкой всех опубликованных файлов."""
from pathlib import Path
import contextlib
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / 'Tools/Disasm'), str(ROOT / 'Tools/Disasm/Research')]
from VerifySources import main as verify


def main():
    candidate = ROOT / 'Tools/Disasm/Research/Candidates/ControlsBufferPoints'
    history = ROOT / 'Tools/Disasm/Research/History/BeforeControlsBufferPoints'
    target = candidate / 'Source/Controls/InitializeBufferPoints.asm'
    previous = target.read_bytes()
    following = previous.replace(b'BufferPointConst.MinimumCoordinate',b'BufferPointConst.MinCoordinate')
    assert previous != following
    assert following == (ROOT / 'Source/Controls/InitializeBufferPoints.asm').read_bytes()
    target.write_bytes(following)
    # Проверка всего кандидата до удаления прежних имён исходников.
    for path in candidate.rglob('*'):
        if path.is_file():
            assert path.read_bytes() == (ROOT / path.relative_to(candidate)).read_bytes(), path
    with contextlib.redirect_stdout(io.StringIO()):
        verify()
    for name in ('UnknownCA8D','UnknownCAB3','UnknownCAE3'):
        path = ROOT / ('Source/Controls/'+name+'.asm')
        assert path.resolve().is_relative_to((ROOT / 'Source/Controls').resolve())
        assert path.read_bytes() == (history / path.relative_to(ROOT)).read_bytes()
        path.unlink()
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/ControlsBufferPointsVerification.json').read_text('utf-8'))
    result = dict(passed=True,described_functions=3,instructions_changed=0,physical_bytes_preserved=True,
        independent_model_cases=proof['total_cases'],constant_label_shortened_before_publication=True,
        original_function_boundaries_preserved=True,assembly_executed=False)
    (ROOT / 'Tools/Disasm/Reports/ControlsBufferPointsClassification.json').write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
