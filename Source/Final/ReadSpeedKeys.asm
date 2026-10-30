                module Final
                module ReadSpeedKeys
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
                JP NC, @Final.ReadSpeedKeys.Point6134                           ; переход, если флаг Carry сброшен


                LD A, #FD
                IN A, (#FE)
                RRA
                JP NC, @Final.ReadSpeedKeys.Point613D                           ; переход, если флаг Carry сброшен


                RET


Point6134:      LD A, (#60D4)
                OR A
                RET Z                                                           ; выход, если флаг Z установлен

                DEC A
                JP @Final.ReadSpeedKeys.Point6144


Point613D:      LD A, (#60D4)
                CP #64
                RET Z                                                           ; выход, если флаг Z установлен

                INC A
Point6144:      LD (#60D4), A
                RET


                endmodule
                endmodule
