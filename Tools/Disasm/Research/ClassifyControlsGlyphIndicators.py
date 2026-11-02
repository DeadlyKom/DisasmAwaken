"""Публикация полного обновления индикаторов с физическими входами и хвостовым продолжением."""
import ControlsGlyphIndicatorsFacts as facts
from ClassifyControlsTextDisplay import main


if __name__=='__main__':
    main(facts,'ControlsGlyphIndicators','ControlsGlyphIndicators',(
        ('RestoreSP',0xE089,'изменяемый операнд LD SP,nn по E088, заполняется входным SP'),))
