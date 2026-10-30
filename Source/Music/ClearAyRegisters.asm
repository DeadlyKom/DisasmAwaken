                module Music
                module ClearAyRegisters
; Документация [Music](../../Docs/FunctionDetails/Music.md)
; -----------------------------------------
; Запись нуля во все 14 музыкальных регистров AY через порты #FFFD и #BFFD
; исходная запись 10, файловые смещения #007C..#009F
; In:
;   дополнительные параметры не требуются
; Out:
;   DE - 0, BC - #BFFD, регистры AY с номерами 13..0 обнулены
; Corrupt:
;   DE, BC, AF
; Note:
;   на каждый регистр выполняются OUT #FFFD с номером и OUT #BFFD с нулевым значением
;   A, HL, индексные и альтернативные регистры сохраняются, IFF не меняется
; -----------------------------------------
                ; обнуление четырнадцати регистров AY в порядке от формы огибающей к младшему байту тона A
Entry:          LD DE, #0E00
PointDB7F:      DEC D
                ; выбор очередного регистра через #FFFD, запись нулевого значения через #BFFD
                LD BC, #FFFD
                OUT (C), D
                LD B, #BF
                OUT (C), E
                JR NZ, @Music.ClearAyRegisters.PointDB7F                        ; переход, если номер следующего обнуляемого регистра ещё не достиг нуля


                RET


                LD A, (DE)
                INC DE
                LD (#DF74), A
                EX DE, HL
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                EX DE, HL
                LD (#DF6E), HL
                LD A, #06
                LD (#DF6B), A
                RET


                endmodule
                endmodule
