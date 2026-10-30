                module Station
                module HandleItem00
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; обработчик события станционного элемента из записи 0 таблицы FInterfaceItem
; исходная запись 4, файловые смещения #21C3..#21DB
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          JP @Station.HandleItem00.Point7F1A


Point7F1A:      CALL Z, @Station.TrackItemGeometry.Entry                        ; вызов, если флаг Z установлен
                RET C                                                           ; выход, если флаг Carry установлен

                PUSH AF
                CALL @Station.CloseActiveItem.Entry
                CALL @Station.MoveItemToTail.Entry
                JP Z, @Station.Unknown7F33.Entry                                ; переход, если флаг Z установлен


                CALL @Station.SuspendPointer.Entry
                LD DE, #7F30
                PUSH DE
                JP (HL)


                endmodule
                endmodule
