"""Публикация полного цикла после проверки рамки, без сборки."""
from ClassifyActionRegionType import main
import ActionPolygonFacts as facts

if __name__=="__main__":main(facts,"ActionPolygon","ActionPolygon",(),allow_named=True,include_blocks=(("Includes/Const/Include.inc","module ActionPolygonConst",'\n                module ActionPolygonConst\nTableLowPage    equ #CF                                                         ; страница младших байтов целей\nOutsideMask     equ #0F                                                         ; младшие признаки выхода за границы\nMinimumBytes    equ #06                                                         ; три пары байтов выходного полигона\n                endmodule\n'),))
