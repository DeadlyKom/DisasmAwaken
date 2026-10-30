                module Intro
                module BuildMirroredTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Построение отражённой текстуры и перенос результата в страницу 4
; исходная запись 3, файловые смещения #0AB6..#0B30
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
Entry:          EI
                LD A, #C3
                LD (#6BDA), A
                LD A, #50
                CALL @Intro.SelectTexturePointerRow.Entry
                SUB A
                LD (#6BA2), A
                LD (#6BA6), A
                LD (#6BA9), A
                LD (#6BAC), A
                LD H, #64
                LD DE, #9400
                LD C, #03
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.BuildPhaseTable.Entry
                LD C, #05
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.BuildPhaseTable.Entry
                CALL @Intro.RenderLookupTexture.Entry
                EI
                LD HL, #80D0
                LD DE, #8000
                LD IXL, #20
Point6DF0:      LD BC, #0020
                PUSH BC
                LDIR
                POP BC
                ADD HL, BC
                PUSH HL
                LD H, D
                LD L, E
                DEC L
                LD B, #20
Point6DFE:      LD A, (HL)
                SUB #89
                LD (HL), A
                LD (DE), A
                INC DE
                DEC L
                DJNZ @Intro.BuildMirroredTexture.Point6DFE

                POP HL
                DEC IXL
                JR NZ, @Intro.BuildMirroredTexture.Point6DF0                    ; переход, если ещё не обработаны все 32 строки отражаемой текстуры


                LD HL, #87FF
                LD DE, #8800
                LD BC, #0800
Point6E15:      LD A, (HL)
                LD (DE), A
                DEC HL
                INC DE
                DEC BC
                LD A, B
                OR C
                JR NZ, @Intro.BuildMirroredTexture.Point6E15                    ; переход, если ещё не отражены все #0800 байтов второй половины


                LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #8000
                LD DE, #C000
                LD BC, #1000
                LDIR
                JP @Intro.SelectIntroPage.Entry


                endmodule
                endmodule
