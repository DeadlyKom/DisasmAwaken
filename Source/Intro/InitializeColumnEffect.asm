                module Intro
                module InitializeColumnEffect
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание обработчика #D000, таблиц выбора столбцов и суммированной текстуры для эффекта
; исходная запись 3, файловые смещения #07C1..#0859
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   #D000 получает 64 копии 25-байтового шаблона #6B5A и RET в конце
;   16 таблиц #D840..#E79F содержат допустимые старшие адреса #D8..#E7 либо ноль
;   шаг DE уменьшается на пять после каждой таблицы, начало HL остаётся #D800
;   хвосты 32 страниц #DA..#F9 с младшими адресами #E0..#FF заполняются 32-байтовой таблицей выбора
;   каждая ячейка текстуры суммирует квадрат 2 на 2 плюс #40 modulo 256
;   после построения #8000..#BFFF выбираются адреса писателя с исходным байтом #C0
; -----------------------------------------
Entry:          CALL @Intro.SelectIntroPage.Entry
                LD DE, #D000
                LD HL, #6B5A
                LD BC, #4019
                CALL @Intro.RepeatPattern.Entry
                LD (HL), #C9
                LD IXH, #D8
                LD HL, #D800
                LD DE, #0100
                LD C, #10
Point6ADD:      PUSH HL
                LD IXL, #40
                LD B, #60
                ; проверка допустимости старшего байта адреса столбца в диапазоне #D8..#E7
Point6AE3:      LD A, H
                CP #E8
                JR C, @Intro.InitializeColumnEffect.Point6AE9                   ; переход, если старший байт адреса меньше #E8


                SUB A
Point6AE9:      CP #D8
                JR NC, @Intro.InitializeColumnEffect.Point6AEE                  ; переход, если старший байт адреса не меньше #D8


                SUB A
Point6AEE:      LD (IX + #00), A
                INC IXL
                ADD HL, DE
                DJNZ @Intro.InitializeColumnEffect.Point6AE3

                INC IXH
                LD HL, #FFFB
                ADD HL, DE
                EX DE, HL
                POP HL
                DEC C
                JR NZ, @Intro.InitializeColumnEffect.Point6ADD                  ; переход, если ещё не созданы все 16 таблиц выбора столбцов


                LD D, #DA
                LD A, #20
Point6B05:      LD E, #E0
                LD HL, #6B73
                LD BC, #0020
                LDIR
                DEC A
                JR NZ, @Intro.InitializeColumnEffect.Point6B05                  ; переход, если ещё не заполнены хвосты всех 32 страниц


                LD (#67FE), A
                LD IXL, #00
                CALL @Intro.ExpandTextureRows.Entry
                LD HL, #8000
                PUSH HL
                LD DE, #C000
                LD BC, #0100
                LDIR
                POP HL
Point6B28:      LD L, #00
                ; расчёт суммы соседнего квадрата 2 на 2 плюс #40 по модулю 256
Point6B2A:      LD A, (HL)
                INC H
                ADD A, (HL)
                INC L
                ADD A, (HL)
                DEC H
                ADD A, (HL)
                DEC L
                ADD A, #40
                LD (HL), A
                INC L
                BIT 6, L
                JR Z, @Intro.InitializeColumnEffect.Point6B2A                   ; переход, если ещё не рассчитаны 64 байта строки


                LD E, L
                LD D, H
                LD BC, #00C0
                LD L, B
                LDIR
                INC H
                BIT 6, H
                JR Z, @Intro.InitializeColumnEffect.Point6B28                   ; переход, если ещё не преобразованы все 64 страницы текстуры


                SUB A
                LD (#6993), A
                LD IXL, #C0
                LD DE, #D800
                LD BC, #0100
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
