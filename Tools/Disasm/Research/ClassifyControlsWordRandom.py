"""Публикация проверенного генератора, существующие слова состояния не перемещаются."""
import ControlsWordRandomFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsWordRandom', 'ControlsWordRandom', (
        ('First', 0x9B15, 'первое слово состояния, получает прежнее Second'),
        ('Second', 0x9B17, 'второе слово состояния, результат двухсловной рекурсии'),
    ))
