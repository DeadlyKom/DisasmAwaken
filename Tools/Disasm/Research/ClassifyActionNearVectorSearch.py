"""Точечное оформление поиска первой близкой цели и существующей рамки CPU-стека."""
import ActionNearVectorSearchFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionNearVectorSearch','ActionNearVectorSearch',state_fields=(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionNearSearchConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FNearVectorSearchFrame',facts.STRUCT_BLOCK)))
