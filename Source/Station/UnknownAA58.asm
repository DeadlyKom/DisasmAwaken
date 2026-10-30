                module Station
                module UnknownAA58
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #4A58..#4A81
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          CALL @Station.RepaintAndTrack.KeepSelector
                RET C

                DEC A
                JP Z, @Station.UnknownAA58.PointAA81

                CALL #C85E
                JP NZ, @Station.UnknownAA58.PointAA81

                LD HL, #9A58
                LD (#9A89), HL
                LD DE, (#6FC6)
                CALL #C873
                LD DE, (#AA86)
                CALL #C873
                LD DE, (#AA50)
                JP #C873

PointAA81:      RET

                endmodule
                endmodule
