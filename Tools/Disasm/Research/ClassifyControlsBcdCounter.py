"""Публикация трёх входов BCD-счётчика общей проверяемой процедурой."""
import ControlsBcdCounterFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsBcdCounter', 'ControlsBcdCounter', (
        ('RotateGate', 0xF10E, 'сохраняемый вращаемый байт в операнде LD A'),
        ('LowPairs', 0x9BBF, 'две младшие BCD-пары в порядке L,H'),
        ('HighPairs', 0x9BBD, 'две старшие BCD-пары в порядке E,D')))
