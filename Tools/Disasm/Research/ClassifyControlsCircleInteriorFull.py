"""Точечная классификация полной композиции внутреннего контура, общие отсечённые ядра остаются Unknown."""
import ControlsCircleInteriorFullFacts as facts
from ClassifyControlsTextDisplay import main

if __name__=='__main__':
    main(facts,'ControlsCircleInteriorFull','ControlsCircleInteriorFull',state_fields=(),include_blocks=(
        ('Includes/Structs/Include.inc','struct FInteriorCircleUpFrame',facts.STRUCT_BLOCK),))
