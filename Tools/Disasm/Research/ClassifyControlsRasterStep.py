"""Публикация двух проверенных помощников со штатным нелокальным возвратом."""
import ControlsRasterStepFacts as facts
from ClassifyControlsTextDisplay import main


if __name__=='__main__':
    main(facts,'ControlsRasterStep','ControlsRasterStep',(
        ('SavedSP',0xD186,'указатель сохранённого AF и внешнего возврата рисователя'),))
