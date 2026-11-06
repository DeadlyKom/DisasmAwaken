"""Публикация фазового затухания и точных писателей существующих операндов."""
import ActionControlDecayFacts as facts
from ClassifyActionRegionType import main

if __name__=='__main__':
    main(facts,'ActionControlDecay','ActionControlDecay',state_fields=facts.FIELDS,include_blocks=(
        ('Includes/Const/Include.inc','module ActionControlDecayConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FControlDecayFrame',facts.STRUCT_BLOCK)))
