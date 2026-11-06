"""Публикация общих писателей без изменения исходных инструкций и сборки."""
from ClassifyActionRegionType import main
import ActionClipPointWritersFacts as facts

if __name__=="__main__":main(facts,"ActionClipPointWriters","ActionClipPointWriters",(("CornerBlock",0xCF03,"полный байт запрета вывода углов"),),allow_named=True,include_blocks=(("Includes/Const/Include.inc","module ActionClipCornerConst",'\n                module ActionClipCornerConst\nTopLeft         equ #0000                                                       ; упакованный угол, E как Second, D как First\nTopRight        equ #00FF                                                       ; упакованный угол, E как Second, D как First\nBottomLeft      equ #5F00                                                       ; упакованный угол, E как Second, D как First\nBottomRight     equ #5FFF                                                       ; упакованный угол, E как Second, D как First\n                endmodule\n'),))
