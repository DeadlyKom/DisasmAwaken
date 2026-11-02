"""Публикация двух входов стекового копировщика после проверки обоих договоров."""
import json
import ControlsBufferCopyFacts as facts
from ClassifyControlsTextDisplay import main, ROOT


if __name__ == '__main__':
    worker = json.loads((ROOT / 'Tools/Disasm/Reports/ControlsBufferCopyWorkerVerification.json').read_text('utf-8'))
    assert worker['passed'] and worker['all_documented_register_outputs_checked']
    main(facts, 'ControlsBufferCopy', 'ControlsBufferCopy', (
        ('SavedStack', 0xCA8A, 'слово SP в исходном LD SP,nn'),
        ('RemainingPages', 0xCA84, 'счётчик в исходном LD A,nn')))
