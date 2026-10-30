                module ActionBoot
                module LoadFileToBank
; Документация [ActionBoot](../../Docs/FunctionDetails/ActionBoot.md)
; -----------------------------------------
; Загрузка выбранного файла по адресу #C000 в уже подключённый банк
; исходная запись 17, файловые смещения #0109..#010B
; In:
;   выбран файл в системном буфере TR-DOS и подключён требуемый банк
; Out:
;   HL устанавливается в #C000, управление завершается общей загрузкой LoadFileAtAddress
; Corrupt:
;   HL, BC, AF, остальные побочные эффекты определяются TR-DOS
; Note:
;   этот вход отличается от следующего только установкой HL, вызова между фрагментами нет
; -----------------------------------------
Entry:          LD HL, #C000
                ; JP @ActionBoot.LoadFileAtAddress.Entry, продолжение в LoadFileAtAddress.asm

                endmodule
                endmodule
