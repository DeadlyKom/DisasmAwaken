                module Voxel
                module ConfigureSmallEffect
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Общий хвост малого эффекта, настройка параметров #0C и #0D перед поиском свободной записи
; исходная запись 21, файловые смещения #000E..#001A
; In:
;   HL, DE, HL', DE', BC', AF', IY - параметры AllocateEffect, Mode уже записан в операнд #EC5A
; Out:
;   выполнен AllocateEffect с параметрами малого эффекта #0D и #0C
; Corrupt:
;   BC, AF, AF', IY
; Note:
;   это общий хвост CreateSmallEffect, адрес #EC0E в другом банке имеет другое назначение
;   обычный вход идёт из CreateSmallEffect, HL и DE к этому моменту содержат #D800 и #00C0
;   имя адреса #EC0E само по себе не определяет модуль, в банке 1 здесь находится другой код CONTROL
; -----------------------------------------
Entry:          LD A, #0C
                LD (#EC79), A
                LD A, #0D
                LD (#EC6C), A
                JP @Voxel.AllocateEffect.Entry


                endmodule
                endmodule
