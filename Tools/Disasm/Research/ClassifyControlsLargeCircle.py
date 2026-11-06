"""Публикация диспетчера после проверки всех дочерних передач до RET."""
from ClassifyControlsTextDisplay import main
import ControlsLargeCircleFacts as facts


if __name__ == '__main__':
    main(facts, 'ControlsLargeCircle', 'ControlsCircleDispatch', state_fields=(), include_blocks=(
        ('Includes/Const/Include.inc', 'module ControlsLargeCircleConst', facts.CONST_BLOCK),))
