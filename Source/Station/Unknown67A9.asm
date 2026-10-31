                module Station
                module Unknown67A9
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #0A55..#0A7B
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          RET

Point67AA:      CALL @Station.BeginScreenUpdate.Entry
                LD A, #14
                CALL @Station.SelectRamBank.Entry
                LD A, (@PanelHoverState.ShipsRow)
                CP #FF
                JR Z, @Station.Unknown67A9.Point67BC

                LD (#E146), A
Point67BC:      LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD HL, #0000
                LD (#6933), HL
                CALL @Station.EndScreenUpdate.Entry
                LD A, #01
                LD (@ShipPanelState.PendingRedraw), A
                RET

                endmodule
                endmodule
