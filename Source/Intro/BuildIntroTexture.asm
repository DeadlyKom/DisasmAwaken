                module Intro
                module BuildIntroTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Преобразование текстуры и копирование #1300 байт в страницу 4
; исходная запись 3, файловые смещения #0A8D..#0AB5
; In:
;   HL - поток параметров, IY - IYL исходный накопитель для BuildTextureLookup, стек ниже #8000
; Out:
;   HL - #9300, DE - #D300, BC - 0, AF - A=#14, #1300 байт подготовленной текстуры находятся в банке 4
; Corrupt:
;   HL, DE, BC, AF, IX, IY
; Note:
;   исходные 128-байтовые фрагменты берутся с младшего адреса #40 на каждой странице начиная с #AD
;   число подготовительных копирований определяется выходным A построителя, ноль означает 256
;   конечное сохранение в банк 4 всегда имеет фиксированную длину #1300
; -----------------------------------------
Entry:          LD A, #2C
                LD IYL, #C0
                CALL @Intro.BuildTextureLookup.Entry
                LD DE, #8000
                LD H, #AD
Point6D9A:      LD L, #40
                LD BC, #0080
                LDIR
                INC H
                DEC A
                JR NZ, @Intro.BuildIntroTexture.Point6D9A                       ; переход, если счётчик A после построителя текстуры ещё не обнулился


                LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD HL, #8000
                LD DE, #C000
                LD BC, #1300
                LDIR
                RET


                endmodule
                endmodule
