"""Публикация фазового обновления тела и широких векторов."""
import ActionBodyMotionFacts as facts
from ClassifyActionRegionType import main


if __name__ == '__main__':
    main(facts, 'ActionBodyMotion', 'ActionWideMotionPrefix', (
        ('PhaseWord', 0x6781, 'изменяемое слово фазового входа'),
        ('WideStepX', 0x68D5, 'знаковый шаг X для широких векторов'),
        ('WideStepY', 0x68FD, 'знаковый шаг Y для широких векторов'),
        ('WideStepDepth', 0x6925, 'знаковый шаг глубины для широких векторов'),
    ))
