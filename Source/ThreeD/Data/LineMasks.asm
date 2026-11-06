                module ThreeDLineMasks
                ; Документация [растеризатор и маски](../../../Docs/ThreeDOverlayMirror.md)
                assert $ == #E010
Set0:           FLinePixelMask {
                    #80                                                         ; Mask, единица выбирает пиксель, фаза 0
                }
Set1:           FLinePixelMask {
                    #40                                                         ; Mask, единица выбирает пиксель, фаза 1
                }
Set2:           FLinePixelMask {
                    #20                                                         ; Mask, единица выбирает пиксель, фаза 2
                }
Set3:           FLinePixelMask {
                    #10                                                         ; Mask, единица выбирает пиксель, фаза 3
                }
Set4:           FLinePixelMask {
                    #08                                                         ; Mask, единица выбирает пиксель, фаза 4
                }
Set5:           FLinePixelMask {
                    #04                                                         ; Mask, единица выбирает пиксель, фаза 5
                }
Set6:           FLinePixelMask {
                    #02                                                         ; Mask, единица выбирает пиксель, фаза 6
                }
Set7:           FLinePixelMask {
                    #01                                                         ; Mask, единица выбирает пиксель, фаза 7
                }
Clear0:         FLinePixelMask {
                    #7F                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 0
                }
Clear1:         FLinePixelMask {
                    #BF                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 1
                }
Clear2:         FLinePixelMask {
                    #DF                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 2
                }
Clear3:         FLinePixelMask {
                    #EF                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 3
                }
Clear4:         FLinePixelMask {
                    #F7                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 4
                }
Clear5:         FLinePixelMask {
                    #FB                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 5
                }
Clear6:         FLinePixelMask {
                    #FD                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 6
                }
Clear7:         FLinePixelMask {
                    #FE                                                         ; Mask, нуль выбирает очищаемый пиксель, фаза 7
                }
                assert $ == #E020
                endmodule
