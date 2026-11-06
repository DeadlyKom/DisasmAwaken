"""Публикация двух входов чтения очереди после отдельных проверок управления и загрузки."""
import json
from ClassifyActionRegionType import main, ROOT
import ActionRenderQueueControlFacts as facts


if __name__ == '__main__':
    proof = json.loads((ROOT / 'Tools/Disasm/Reports/ActionRenderQueueLoadVerification.json').read_text('utf-8'))
    assert proof['passed'] and proof['total_cases'] == 8704
    main(facts, 'ActionRenderQueueControl', 'ActionRenderQueueControl', (
        ('SavedEntrySP', 0xE4A7, 'операнд LD SP,nn по E4A6, исходный стек всего обхода'),
        ('SavedNodeSP', 0xE4D6, 'операнд LD SP,nn по E4D5, стек со словом указателя узла')))
