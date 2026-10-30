                module Intro
                module InitializeIntro
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Перенос завершающего загрузчика, вывод экрана и создание таблиц вступления
; исходная запись 3, файловые смещения #0200..#02B2
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
Entry:          DI
                LD HL, #65B7
                LD DE, #5D3B
                LD BC, #0100
                LDIR
                LD SP, #5FFF
                SUB A
                OUT (#FE), A
                LD HL, #6E31
                LD DE, #4000
                LD BC, #1B00
                LDIR
                LD HL, #8931
                LD DE, #6E31
                LD BC, #1B00
                LDIR
                LD C, #FF
                CALL @Intro.FillBitmap.Entry
                LD IY, #5C3A
                LD (#65B4), SP
                CALL @Intro.SelectIntroPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #3FFF
                LD (HL), L
                LDIR
                LD HL, #6000
                LD DE, #6001
                LD BC, #03FF
                LD (HL), L
                LDIR
                LD HL, #8F93
                LD DE, #8F94
                LD BC, #306C
                LD (HL), #00
                LDIR
                LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #12FF
                LD (HL), L
                LDIR
                LD A, #16
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #C000
                LD DE, #C001
                LD BC, #3FFF
                LD (HL), L
                LDIR
                CALL @Intro.BuildScreenTables.Entry
                CALL @Intro.BuildIntroTexture.Entry
                CALL @Intro.BuildAlternatingTexture.Entry
                EI
                CALL @Intro.InitializeLookupEffect.Entry
                CALL @Intro.BuildMirroredTexture.Entry
                CALL @Intro.InitializeColumnEffect.Entry
                CALL @Intro.InitializeScrolledTexture.Entry
                LD C, #00
                CALL @Intro.FillBitmap.Entry
                LD HL, #5800
                LD DE, #5801
                LD BC, #01FF
                LD (HL), #88
                LDIR
                LD BC, #012C
                LD HL, #661E
                CALL @Intro.RunTimedEffect.Entry
Point65B0:      JP #5D3B


                endmodule
                endmodule
