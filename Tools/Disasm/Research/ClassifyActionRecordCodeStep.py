"""Публикация основного обработчика и проверенного внутреннего ApplyCodes."""
import ActionRecordCodeStepFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionRecordCodeStep','ActionRecordCodeStep',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionCodeStepConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FRecordStepRootFrame',facts.STRUCT_BLOCK)))
