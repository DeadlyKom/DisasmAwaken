"""Точечное оформление доказанных 64 байтов подготовки новой загрузочной стадии."""
import ControlsStationPrepareFacts as facts
from ClassifyControlsTextDisplay import main

if __name__=='__main__':
    main(facts,'ControlsStationPrepare','ControlsStationPrepare',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ControlsStationPrepareConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FStationReloadFrame',facts.STRUCT_BLOCK)))
