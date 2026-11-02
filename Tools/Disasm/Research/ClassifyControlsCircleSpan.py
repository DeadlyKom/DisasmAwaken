"""Публикация самостоятельного входа D320 после проверки исходного хвостового JP."""
import ControlsCircleSpanFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsCircleSpan', 'ControlsCircleSpan', (
        ('CenterX', 0xD184, 'байтовая горизонтальная координата центра сечения'),
    ))
