"""Оформление обеих точек входа горизонтального рисователя."""
import ControlsHorizontalCircleFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsHorizontalCircle', 'ControlsHorizontalCircle', state_fields=(), include_blocks=(
        ('Includes/Const/Include.inc', 'module ControlsHorizontalCircleConst', facts.CONST_BLOCK),))
