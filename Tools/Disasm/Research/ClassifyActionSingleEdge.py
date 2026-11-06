"""Публикация полного одиночного ребра после композиционной проверки, без сборки."""
from ClassifyActionRegionType import main
import ActionSingleEdgeFacts as facts

if __name__=="__main__":main(facts,"ActionSingleEdge","ActionSingleEdge",(),include_blocks=(("Includes/Const/Include.inc","module ActionSingleEdgeConst",'\n                module ActionSingleEdgeConst\nNoCorners       equ #01                                                         ; полный запрет фактического добавления углов\nSegmentBytes    equ #04                                                         ; две пары выходного ребра\n                endmodule\n'),))
