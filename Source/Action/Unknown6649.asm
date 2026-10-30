                module Action
                module Unknown6649
; Документация [Action](../../Docs/FunctionDetails/Action.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 17, файловые смещения #0886..#090E
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
Entry:          LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point665B                             ; переход, если флаг Z установлен


                LD A, (#A794)
                LD HL, #49A1
                CALL @Action.Unknown6639.Entry
                XOR A
                LD (#664A), A
Point665B:      LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point666A                             ; переход, если флаг Z установлен


                CALL @Action.Unknown74FB.Entry
                RRA
                LD HL, #49E1
                CALL @Action.Unknown6639.Entry
Point666A:      LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point667C                             ; переход, если флаг Z установлен


                LD A, (#A8BC)
                LD HL, #5121
                CALL @Action.Unknown6639.Entry
                XOR A
                LD (#666B), A
Point667C:      LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point668D                             ; переход, если флаг Z установлен


                LD A, #00
                LD HL, #5181
                CALL @Action.Unknown6639.Entry
                XOR A
                LD (#667D), A
Point668D:      LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point669E                             ; переход, если флаг Z установлен


                LD A, #00
                LD HL, #51C1
                CALL @Action.Unknown6639.Entry
                XOR A
                LD (#668E), A
Point669E:      LD A, #00
                AND A
                JR Z, @Action.Unknown6649.Point66D1                             ; переход, если флаг Z установлен


                XOR A
                LD (#669F), A
                LD HL, (#A78F)
                BIT 7, H
                JR Z, @Action.Unknown6649.Point66B5                             ; переход, если флаг Z установлен


                LD A, L
                CPL
                LD L, A
                LD A, H
                CPL
                LD H, A
                INC HL
Point66B5:      LD A, H
                SRL A
                RR L
                SRL A
                RR L
                AND A
                JR Z, @Action.Unknown6649.Point66C3                             ; переход, если флаг Z установлен


                LD L, #2E
Point66C3:      LD A, L
                CP #2F
                JR C, @Action.Unknown6649.Point66CA                             ; переход, если флаг Carry установлен


                LD L, #2E
Point66CA:      LD A, L
                LD HL, #49B9
                CALL @Action.Unknown6639.Entry
Point66D1:      RET


                endmodule
                endmodule
