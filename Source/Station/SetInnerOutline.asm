                module Station
                module SetInnerOutline
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [внутренний контур рамки](../../Docs/StationSpans.md)
; -----------------------------------------
; Выбор пустой середины и боковых пикселей на два бита от внешнего края
; исходная запись 4, файловые смещения #6210..#621E
; In:
;   AF' - Z=1 заменяет левый край серединой, Carry=1 заменяет правый край серединой
; Out:
;   DE - D образец левого края, E образец середины, BC - C образец правого края, B сохранён
; Corrupt:
;   DE, BC
; Note:
;   при обоих разрешённых краях D=#20, E=#00, C=#04
;   HL, оба AF, альтернативные и индексные регистры сохраняются, SP восстанавливается
;   I и IFF сохраняются, пиксели не записываются, образцы использует DrawSpanRow
; -----------------------------------------
                ; выбор узоров по альтернативным условиям отсечения с сохранением обоих AF
Entry:          EX AF, AF'
                LD E, @SpanPattern.Empty
                LD D, @SpanPattern.InnerLeft
                JR NZ, @Station.SetInnerOutline.KeepLeft                        ; переход, если Z' сброшен, собственный левый край сохраняется

                LD D, E
KeepLeft:       LD C, @SpanPattern.InnerRight
                JR NC, @Station.SetInnerOutline.KeepRight                       ; переход, если Carry' сброшен, собственный правый край сохраняется

                LD C, E
KeepRight:      EX AF, AF'
                RET

                endmodule
                endmodule
