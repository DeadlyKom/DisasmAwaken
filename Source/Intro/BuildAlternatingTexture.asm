                module Intro
                module BuildAlternatingTexture
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Построение текстуры с чередованием исходного байта и байта, уменьшенного в четыре раза, копия в банк 6
; исходная запись 3, файловые смещения #0338..#0362
; In:
;   таблица координат #6400 подготовлена, стек расположен ниже #8000
; Out:
;   HL - #C000, DE - 0, BC - 0, AF - A=#16, преобразованная текстура скопирована в банк 6
; Corrupt:
;   HL, DE, BC, AF, IX, IY
; Note:
;   изменяется младший байт IY, альтернативные регистры не используются
;   строитель выборок сначала подключает банк 1, источник второй стадии #A000..#DFFF
;   сначала BuildTextureLookup строит таблицу по данным #6663, A=#6F сохраняет LD IYL,A
;   в каждой исходной строке #A000..#DFFF чётный байт делится на четыре, нечётный копируется
;   результат #8000..#BFFF переносится в банк 6 после записи #16 в #7FFD
; -----------------------------------------
Entry:          LD A, #6F
                LD HL, #6663
                CALL @Intro.BuildTextureLookup.Entry
                LD DE, #8000
                LD H, #A0
Point6645:      LD L, #00
                ; преобразование чётного байта исходной строки, нечётный байт сохраняется
Point6647:      LD A, (HL)
                SRL A
                SRL A
                LD (DE), A
                INC L
                INC E
                LD A, (HL)
                LD (DE), A
                INC L
                INC E
                JR NZ, @Intro.BuildAlternatingTexture.Point6647                 ; переход, если строка приёмника ещё не содержит 256 байтов


                INC H
                INC D
                BIT 6, D
                JR Z, @Intro.BuildAlternatingTexture.Point6645                  ; переход, если приёмник ещё не достиг #C000


                LD A, #16
                CALL @Intro.SelectMemoryPage.Entry
                JP @Intro.CopyTextureToBank.Entry


                endmodule
                endmodule
