                module Final
                module ReadSpeedKeys
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
; Документация [Final](../../Docs/FunctionDetails/Final.md)
; -----------------------------------------
; Изменение счётчика задержки клавишами Q и A с границами 0..100
; исходная запись 29, файловые смещения #0123..#0147
; In:
;   операнд #60D4 содержит задержку от 0 до 100
; Out:
;   по Q задержка уменьшается до нуля, по A увеличивается до 100, без клавиши сохраняется
; Corrupt:
;   AF
; Note:
;   опрос Q имеет приоритет при одновременном нажатии, используются порты #FBFE и #FDFE, бит 0
;   за пределами 0..100 процедура не нормализует исходное значение
; -----------------------------------------
                ; проверка Q, бит 0 строки #FBFE имеет приоритет перед A
Entry:          LD A, #FB
                IN A, (#FE)
                RRA
                JP NC, @Final.ReadSpeedKeys.DecreaseDelay                       ; переход, если нажата Q, уменьшить задержку


                LD A, #FD
                IN A, (#FE)
                RRA
                JP NC, @Final.ReadSpeedKeys.IncreaseDelay                       ; переход, если нажата A, увеличить задержку


                RET


DecreaseDelay:  LD A, (#60D4)
                OR A
                RET Z                                                           ; выход, если задержка уже равна нулю, Q не уменьшает её дальше

                DEC A
                JP @Final.ReadSpeedKeys.StoreDelay


IncreaseDelay:  LD A, (#60D4)
                CP #64
                RET Z                                                           ; выход, если задержка уже равна ста, A не увеличивает её дальше

                INC A
StoreDelay:     LD (#60D4), A
                RET


                endmodule
                endmodule
