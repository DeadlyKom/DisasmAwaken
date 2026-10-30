                module Intro
                module BuildAttributeWriter
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание развёрнутого писателя, таблицы выборок и двух таблиц экранных атрибутов
; исходная запись 3, файловые смещения #062D..#0663
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
;   в #68A9 создаются 32 записи по четыре байта, каждая делает POP HL и LD (nn),HL
;   IXL задаёт исходные младший и старший байты адреса записи, младший увеличивается на два
;   после четырёх слов начинается следующая страница назначения, всего восемь страниц
;   DE и BC первого набора задают начало и шаг значений в 38 записях #6000 и #6100
;   две матрицы атрибутов #60C0 и #61C0 строятся из исходной таблицы #6993
; -----------------------------------------
Entry:          EXX
                LD HL, #68A9
                LD D, IXL
                LD C, #08
Point6935:      LD E, IXL
                LD B, #04
                ; создание четырёх байтов команды, #E1 означает POP HL, #22 означает LD (nn),HL
Point6939:      LD (HL), #E1
                INC HL
                LD (HL), #22
                INC HL
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                INC E
                INC E
                DJNZ @Intro.BuildAttributeWriter.Point6939

                INC D
                DEC C
                JR NZ, @Intro.BuildAttributeWriter.Point6935                    ; переход, если ещё не созданы писатели всех восьми страниц


                EXX
                LD HL, #6000
                LD A, #26
                CALL @Intro.BuildPairedPointers.Entry
                LD DE, #60C0
                LD HL, #6993
                LD B, H
                LD C, L
                CALL @Intro.CombineAttributeNibbles.Entry
                LD DE, #61C0
                LD B, H
                LD C, L
                ; JP @Intro.CombineAttributeNibbles.Entry, продолжение в CombineAttributeNibbles.asm

                endmodule
                endmodule
