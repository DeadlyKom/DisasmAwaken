"""Публикация проверенной межбанковой перерисовки без переноса кода или стека."""
from ClassifyActionRegionType import main
import ActionRefreshPanelFacts as facts

if __name__=='__main__':
    main(facts,'ActionRefreshPanel','ActionRefreshPanel',(),include_blocks=(
        ('Includes/Const/Include.inc','module ActionPanelRefreshConst',facts.CONST_BLOCK),
        ('Includes/Structs/Include.inc','struct FPanelRefreshGaugeFrame',facts.STRUCT_BLOCK)))
