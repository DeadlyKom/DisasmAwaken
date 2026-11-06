"""Публикация двух доказанных инициализаторов канонического сечения, общие отсечённые входы не переименовываются."""
import ControlsCircleHalfFacts as facts
from ClassifyControlsTextDisplay import main

if __name__=='__main__':
    main(facts,'ControlsCircleHalf','ControlsCircleHalf',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ControlsCircleHalfConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FSingleCircleHalfFrame',facts.STRUCT_BLOCK)))
