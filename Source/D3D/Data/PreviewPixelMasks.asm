                module PreviewPixelMasks
                ; Документация [маски пикселя и режимы ребра](../../../Docs/PreviewEdgeRaster.md)
                assert $ == #CDB0
                ; каждый байт выбирает один экранный бит, слева направо разряды 7..0
SetBit:         DB #80, #40, #20, #10, #08, #04, #02, #01
                ; каждый байт сохраняет остальные семь битов при AND
ClearBit:       DB #7F, #BF, #DF, #EF, #F7, #FB, #FD, #FE
                assert $ == #CDC0
                endmodule
