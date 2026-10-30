                module Station
                module UnknownA191
; Документация [новые входы действий](../../Docs/StationEventActions.md)
; -----------------------------------------
; Unknown, новый достижимый участок из действия интерфейса, отдельный алгоритм и контракт ещё разбираются
; исходная запись 4, файловые смещения #4191..#41D5
; In:
;   Unknown, отдельный контракт нового входа ещё не установлен
; Out:
;   исходные инструкции, адреса и порядок байтов сохранены
; Corrupt:
;   Unknown, достижимость не доказывает назначение или регистровый договор
; -----------------------------------------
Entry:          PUSH HL
PointA192:      LD A, (BC)
                AND A
                JR Z, @Station.UnknownA191.PointA1CB

                SUB #1D
                ADD A, A
                ADD A, #AC
                LD L, A
                LD A, #96
                ADC A, #00
                LD H, A
                LD A, (DE)
                CP #7F
                JR C, @Station.UnknownA191.PointA1BA

                JR Z, @Station.UnknownA191.PointA1C1

                CP #82
                JR NC, @Station.UnknownA191.PointA1C1

                LD A, (BC)
                CP #59
                LD A, #81
                JR Z, @Station.UnknownA191.PointA1BD

                LD A, (BC)
                CP #4E
                LD A, #80
                JR Z, @Station.UnknownA191.PointA1BD

PointA1BA:      LD A, (BC)
                SUB #30
PointA1BD:      LD (DE), A
                INC DE
                JR @Station.UnknownA191.PointA1C7

PointA1C1:      LD A, (HL)
                LD (DE), A
                INC DE
                INC HL
                LD A, (HL)
                LD (DE), A
PointA1C7:      INC DE
                INC BC
                JR @Station.UnknownA191.PointA192

PointA1CB:      POP HL
                RET

PointA1CD:      POP DE
                LD (#6307), DE
                CALL @Station.ResumePointer.Entry
                RET

                endmodule
                endmodule
