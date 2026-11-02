"""Публикация функции XOR-маркера после типизации её физической таблицы."""
import ControlsMarkerFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsMarker', 'ControlsMarker', (
        ('Position', 0x9B19, 'положение маркера, смещение по битам в линейном буфере'),))
