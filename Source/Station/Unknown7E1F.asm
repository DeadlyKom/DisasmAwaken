                module Station
                module Unknown7E1F
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Unknown, назначение этого фрагмента ещё не установлено
; исходная запись 4, файловые смещения #20CB..#20FE
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
Entry:          LD (#6906), A
                LD A, #01
                LD (#68EB), A
                LD A, #FF
                LD (#67D7), A
                XOR A
                LD (#79DD), A
                LD HL, (#7A83)
                LD A, #04
                CALL @Station.GetItemField.Entry
                SET 0, (HL)
                LD HL, (#7A56)
                LD A, #04
                CALL @Station.GetItemField.Entry
                RES 0, (HL)
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                XOR A
                LD (#E146), A
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                RET


                endmodule
                endmodule
