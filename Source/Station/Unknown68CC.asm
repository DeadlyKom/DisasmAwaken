                module Station
                module Unknown68CC
                ; Документация [корабельные периодические входы](../../Docs/ShipPeriodicCode.md)
                ; -----------------------------------------
                ; Unknown, исходный корабельный callback, полный договор зависимых рисователей и банка 4 ещё не установлен
                ; исходная запись 4, файловые смещения #0B78..#0B95
                ; In:
                ;   Unknown, полный договор зависимых рисователей ещё не установлен
                ; Out:
                ;   исходные инструкции и физические адреса сохранены, известные ветви описаны в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная граница до разбора вызовов
                ; Note:
                ;   выделение достижимого кода не доказывает полный смысловой разбор
                ; -----------------------------------------
Entry:          LD A, (@ActiveItemState.Active)
                ; проверка байтового состояния перед выбором ветви
                OR A
                RET NZ                                                          ; выход, если ActiveItemState.Active ненулевой, отложить обновление

                LD (@ShipPanelState.PendingRedraw), A
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawModelListPanel.Entry
                CALL @Station.TryDrawModelDescription.Entry
                LD DE, (#6878)
                CALL @Station.MoveItemToTail.Entry
                CALL @Station.Unknown6870.Entry
                JP @Station.EndScreenUpdate.Entry

                endmodule
                endmodule
