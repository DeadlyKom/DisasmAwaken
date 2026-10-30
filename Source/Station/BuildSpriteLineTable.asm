                module Station
                module BuildSpriteLineTable
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Построение адресов строк спрайта с обработкой смещения внутри знакоместа
; исходная запись 4, файловые смещения #05CE..#060F
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
Entry:          LD A, E
                ADD A, #08
                LD E, A
                LD A, D
                ADD A, #10
                LD L, A
                LD H, #82
                LD D, (HL)
                INC H
                LD A, (HL)
                INC H
                LD L, E
                ADD A, (HL)
                LD E, A
                AND #1F
                EX AF, AF'
                LD A, E
                AND #E0
                LD E, A
                LD HL, #C900
Point633D:      LD (HL), D
                INC H
                LD (HL), E
                DEC H
                INC D
                LD A, D
                AND #07
                JP NZ, @Station.BuildSpriteLineTable.Point6352                  ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JR C, @Station.BuildSpriteLineTable.Point6352                   ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
Point6352:      INC L
                JR NZ, @Station.BuildSpriteLineTable.Point633D                  ; переход, если флаг Z сброшен


                INC H
                INC H
                EX AF, AF'
Point6358:      LD B, #08
Point635A:      LD (HL), A
                INC L
                DJNZ @Station.BuildSpriteLineTable.Point635A

                INC A
                INC L
                DEC L
                JR NZ, @Station.BuildSpriteLineTable.Point6358                  ; переход, если флаг Z сброшен


                RET


                endmodule
                endmodule
