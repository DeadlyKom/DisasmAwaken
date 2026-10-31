                module Station
                module Unknown6963
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0C0F..#0C23
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, (@ShipPanelState.Selector)
                CALL #E124
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD (#692B), DE
                RET

                endmodule
                endmodule
