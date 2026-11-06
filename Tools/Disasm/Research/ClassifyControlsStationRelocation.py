"""Точечное оформление переноса, содержимое копии и TR-DOS не объявляются разобранными."""
import ControlsStationRelocationFacts as facts
from ClassifyControlsTextDisplay import main

if __name__=='__main__':
    main(facts,'ControlsStationRelocation','ControlsStationRelocation',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ControlsStationRelayConst',facts.CONST_BLOCK),))
