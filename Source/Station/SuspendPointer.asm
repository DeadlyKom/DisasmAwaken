                module Station
                module SuspendPointer
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [указатель и сохранение фона](../../Docs/Pointer.md)
; -----------------------------------------
; Запрет периодического обновления указателя с восстановлением его фона
; исходная запись 4, файловые смещения #066F..#0683
; In:
;   действует предусловие RestorePointer, стек вмещает динамический FPointerGuardFrame
; Out:
;   HL, DE, BC, AF, все альтернативные и индексные регистры сохранены
;   UpdateBlocked=1, при активном рисунке фон восстановлен и RestoredFlag=1
; Corrupt:
;   регистры сохранены
; Note:
;   I и IFF сохраняются, SP восстанавливается, флаг запрета записывается до восстановления фона
;   при ненулевом прежнем RestoredFlag его значение не нормализуется
; -----------------------------------------
                ; создание динамического кадра FPointerGuardFrame для сохранения вызывающего контекста
Entry:          PUSH IX
                PUSH AF
                PUSH HL
                PUSH DE
                PUSH BC
                ; запрет периодического обновления перед восстановлением пикселей фона
                LD A, #01
                LD (@PointerState.UpdateBlocked), A
                ; восстановление фона только при активном рисунке указателя
                CALL @Station.RestorePointer.Entry
                ; снятие FPointerGuardFrame с полным восстановлением основного контекста и IX
                POP BC
                POP DE
                POP HL
                POP AF
                POP IX
                RET

                endmodule
                endmodule
