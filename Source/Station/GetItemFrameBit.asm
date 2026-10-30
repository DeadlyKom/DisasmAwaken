                module Station
                module GetItemFrameBit
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [объединение входов и чтение бита контура](../../Docs/InterfaceInput.md)
; -----------------------------------------
; Чтение бита 0 Flags элемента по индексу в DE с сохранением контекста
; исходная запись 4, файловые смещения #3E97..#3EA4
; In:
;   HL - произвольное сохраняемое значение, DE - индекс, BC сохраняется
;   адрес (StationState.Items+16*DE+FInterfaceItem.Flags) AND #FFFF доступен для чтения
; Out:
;   HL, DE и BC сохранены, A=Flags AND 1
;   при нулевом бите AF=#0054, при установленном AF=#0110
; Corrupt:
;   AF
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   нет проверки диапазона индекса, переполнение адреса сохраняется по модулю 65536
;   бит 0 является выбором контура, не признаком наличия или валидности записи
; -----------------------------------------
                ; сохранение HL, DE, BC перед адресацией записи по индексу DE
Entry:          PUSH HL
                PUSH DE
                PUSH BC
                ; передача DE-индекса в GetItemFlags через HL
                EX DE, HL
                CALL @Station.GetItemFlags.Entry
                ; чтение физического Flags до восстановления исходного контекста
                LD A, (HL)
                POP BC
                POP DE
                POP HL
                ; выделение только бита 0, используемого выбором контура
                AND @InterfaceFlags.FrameBitMask
                RET

                endmodule
                endmodule
