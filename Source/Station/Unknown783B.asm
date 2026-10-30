                module Station
                module Unknown783B
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #1AE7..#1B2F
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          CALL @Station.RepaintAndFlag.Entry
                RET C

                DEC A
                JP Z, @Station.Unknown783B.Point784F

                CALL #C85E
                JR NZ, @Station.Unknown783B.Point784E

                LD HL, #9A58
                LD (#9A89), HL
Point784E:      RET

Point784F:      LD A, (#9848)
                LD HL, (#9844)
                LD DE, (#9846)
                CALL @Station.DescribeKeyBanked.Entry
                RET Z

                EX AF, AF'
                LD HL, (#788D)
                XOR A
                CALL @Station.GetItemField.Entry
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                LD A, #11
                CALL @Station.SelectRamBank.Entry
                EX AF, AF'
                CALL @Map.SelectNearestMapVariant.Entry
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.TryDrawSystemInfo.Entry
                CALL @Station.TryDrawVariantPanel.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                endmodule
                endmodule
