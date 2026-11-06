"""Публикация родительской композиции и трёх реально создаваемых стековых форматов."""
import ActionHalfDeltaCodesFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionHalfDeltaCodes','ActionHalfDeltaCodes',state_fields=(),include_blocks=(
        ('Includes/Structs/Include.inc','struct FDeltaCodeRootFrame',facts.BLOCK),))
