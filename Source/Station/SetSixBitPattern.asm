                module Station
                module SetSixBitPattern
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Выбор заполненной середины и шести средних пикселей крайних байтов по AF'
; исходная запись 4, файловые смещения #61DE..#61EC
; In:
;   AF' - Z=1 заменяет левый край серединой, Carry=1 заменяет правый край серединой
; Out:
;   DE - D образец левого края, E образец середины, BC - C образец правого края, B сохраняется
; Corrupt:
;   DE, BC
; Note:
;   основные HL, AF, альтернативные и индексные регистры сохраняются, SP восстанавливается
;   на входе и выходе оба AF совпадают побитно, обмен нужен только для чтения альтернативных условий
;   байты ещё не записываются на экран, последующий писатель строки использует D, E и C
; -----------------------------------------
                ; выбор крайних образцов по альтернативному AF с сохранением обоих AF
Entry:          EX AF, AF'
                LD E, @SpanPattern.Solid
                LD D, @SpanPattern.SixBitEdge
                JR NZ, @Station.SetSixBitPattern.KeepLeft                       ; переход, если входной Z' сброшен и левый край сохраняет собственный образец

                LD D, E
KeepLeft:       LD C, @SpanPattern.SixBitEdge
                JR NC, @Station.SetSixBitPattern.KeepRight                      ; переход, если входной Carry' сброшен и правый край сохраняет собственный образец

                LD C, E
KeepRight:      EX AF, AF'
                RET

                endmodule
                endmodule
