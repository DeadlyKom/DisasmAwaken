                module Intro
                module ExpandTextureRows
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Добавление IXL к 4096 байтам банка 4 и четырёхкратное повторение каждой 64-байтовой строки
; исходная запись 3, файловые смещения #0429..#0456
; In:
;   IX - IXL добавка к каждому байту текстуры, банк 4 содержит #1000 байт исходных строк
; Out:
;   #8000..#BFFF содержат 64 страницы повторяющихся строк, AF - A=#11, подключён банк 1
; Corrupt:
;   HL, DE, BC, AF
; Note:
;   каждые исходные 64 байта превращаются в 256 байт перекрывающимся LDIR, IX сохраняется
;   первые #1000 байт банка 4 разворачиваются в 64 строки по 64 байта, к каждому добавляется IXL modulo 256
;   перекрывающийся LDIR с расстоянием #40 повторяет строку ещё три раза в пределах страницы
;   после заполнения #8000..#BFFF восстанавливается банк 1 через SelectIntroPage
; -----------------------------------------
Entry:          LD A, #14
                CALL @Intro.SelectMemoryPage.Entry
                LD D, #80
                LD HL, #C000
Point6733:      LD E, #00
                LD B, #40
                ; преобразование очередного байта текстуры с добавлением смещения IXL
Point6737:      LD A, (HL)
                ADD A, IXL
                LD (DE), A
                INC HL
                INC E
                DJNZ @Intro.ExpandTextureRows.Point6737

                INC D
                BIT 6, D
                JR Z, @Intro.ExpandTextureRows.Point6733                        ; переход, если ещё не созданы все 64 строки текстуры


                LD H, #80
                LD D, H
Point6747:      LD BC, #00C0
                LD L, B
                LD E, #40
                ; повторение 64-байтового образца ещё три раза перекрывающимся копированием
                LDIR
                INC H
                BIT 6, H
                JR Z, @Intro.ExpandTextureRows.Point6747                        ; переход, если ещё не повторены строки всех 64 страниц


                JP @Intro.SelectIntroPage.Entry


                endmodule
                endmodule
