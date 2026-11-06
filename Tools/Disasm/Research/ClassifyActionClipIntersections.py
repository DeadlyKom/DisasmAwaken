"""Публикация четырёх доказанных пересечений, без запуска сборки."""
from ClassifyActionRegionType import main
import ActionClipIntersectionsFacts as facts

if __name__=="__main__":
    main(facts,"ActionClipIntersections","ActionClipIntersections",(("OutputSize",0x9BA3,"байтовое смещение выхода в странице 90"),),include_blocks=(("Includes/Const/Include.inc","module ActionClipIntersectionConst",'\n                module ActionClipIntersectionConst\nOutputPage      equ #90                                                         ; существующая страница пар выходных байтов\n                endmodule\n'),))
