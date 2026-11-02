"""Публикация двух помощников адреса и масок с сохранением общей неизвестной ячейки D18C."""
import ControlsSpanMasksFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts,'ControlsSpanMasks','ControlsSpanMasks',(
        ('SavedB',0xD18A,'существующий временный байт сохранения B'),))
