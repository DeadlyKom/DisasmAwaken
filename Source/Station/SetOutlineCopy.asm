                module Station
                module SetOutlineCopy
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [StationSpans.md](../../Docs/StationSpans.md)
; -----------------------------------------
; Исходная копия выбора нулевой середины и одиночных боковых пикселей по AF'
; исходная запись 4, файловые смещения #6224..#6232
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
                LD E, @SpanPattern.Empty
                LD D, @SpanPattern.OutlineLeft
                JR NZ, @Station.SetOutlineCopy.KeepLeft                         ; переход, если входной Z' сброшен и левый край сохраняет собственный образец

                LD D, E
KeepLeft:       LD C, @SpanPattern.OutlineRight
                JR NC, @Station.SetOutlineCopy.KeepRight                        ; переход, если входной Carry' сброшен и правый край сохраняет собственный образец

                LD C, E
KeepRight:      EX AF, AF'
                RET

                endmodule
                endmodule
