"""Публикация полного растрового прохода радара."""
import ControlsRadarLoopFacts as facts
from ClassifyControlsTextDisplay import main


if __name__ == '__main__':
    main(facts, 'ControlsRadarLoop', 'ControlsRasterBackground', state_fields=())
