                module Station
                module SetDeepInset
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [внутренний контур рамки](../../Docs/StationSpans.md)
; -----------------------------------------
; Выбор заполненной середины и краёв с тремя внешними пропусками
; исходная запись 4, файловые смещения #6201..#620F
; In:
;   AF' - Z=1 заменяет левый край серединой, Carry=1 заменяет правый край серединой
; Out:
;   DE - D образец левого края, E образец середины, BC - C образец правого края, B сохранён
; Corrupt:
;   DE, BC
; Note:
;   при обоих разрешённых краях D=#1F, E=#FF, C=#F8
;   HL, оба AF, альтернативные и индексные регистры сохраняются, SP восстанавливается
;   I и IFF сохраняются, пиксели не записываются, образцы использует DrawSpanRow
; -----------------------------------------
                ; выбор узоров по альтернативным условиям отсечения с сохранением обоих AF
Entry:          EX AF, AF'
                LD E, @SpanPattern.Solid
                LD D, @SpanPattern.DeepLeft
                JR NZ, @Station.SetDeepInset.KeepLeft                           ; переход, если Z' сброшен, собственный левый край сохраняется

                LD D, E
KeepLeft:       LD C, @SpanPattern.DeepRight
                JR NC, @Station.SetDeepInset.KeepRight                          ; переход, если Carry' сброшен, собственный правый край сохраняется

                LD C, E
KeepRight:      EX AF, AF'
                RET

                endmodule
                endmodule
