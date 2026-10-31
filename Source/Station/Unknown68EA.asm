                module Station
                module Unknown68EA
                ; Документация [корабельные периодические входы](../../Docs/ShipPeriodicCode.md)
                ; -----------------------------------------
                ; Unknown, исходный корабельный callback, полный договор зависимых рисователей и банка 4 ещё не установлен
                ; исходная запись 4, файловые смещения #0B96..#0BBE
                ; In:
                ;   Unknown, полный договор зависимых рисователей ещё не установлен
                ; Out:
                ;   исходные инструкции и физические адреса сохранены, известные ветви описаны в документации
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная граница до разбора вызовов
                ; Note:
                ;   выделение достижимого кода не доказывает полный смысловой разбор
                ; -----------------------------------------
Entry:          LD A, #00
                ; проверка байтового состояния перед выбором ветви
                OR A
                JR NZ, @Station.Unknown68CC.Entry                               ; переход, если PendingRedraw ненулевой, обработать отложенное обновление

                CALL @Station.GetLastDraw.Entry
                LD DE, @Station.DrawItem26.Entry
                OR A
                ; сравнение последнего рисователя с исходным адресом DrawItem26
                SBC HL, DE
                RET NZ                                                          ; выход, если последний рисователь не равен DrawItem26.Entry

                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.FillWindowBody.Entry
                HALT
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, #00
                CALL #E07F
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
