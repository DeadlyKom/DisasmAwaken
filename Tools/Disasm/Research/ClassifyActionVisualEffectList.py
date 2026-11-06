"""Публикация обхода и продолжения после сквозной проверки восьми записей."""
import ActionVisualEffectListFacts as facts
from ClassifyActionRegionType import main


if __name__ == '__main__':
    main(facts, 'ActionVisualEffectList', 'ActionVisualEffectWalk', (
        ('Enabled', 0x6D39, 'операнд допуска кадрового обхода'),
        ('Frames', 0x6D3D, 'операнд числа оставшихся кадров'),
        ('SavedSP', 0x6DD2, 'операнд восстановления настоящего SP'),
    ))
