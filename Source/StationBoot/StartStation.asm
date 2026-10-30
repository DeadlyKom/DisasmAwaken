                module StationBoot
                module StartStation
; Документация [StationBoot](../../Docs/FunctionDetails/StationBoot.md)
; -----------------------------------------
; Загрузка банков карты, музыки, справки, 3D и языка, выбор фона, настройка устройств и запуск цикла станции
; исходная запись 4, файловые смещения #0389..#05CD
; In:
;   ядро станции перенесено в #6322, загрузчик находится по исходному адресу #4000, TR-DOS доступен
; Out:
;   подключён банк 0, установлен IM 2, разрешены прерывания, управление передано #9A59
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, побочные эффекты загруженных модулей и TR-DOS
; Note:
;   банки 1, 3, 7, 4 и 6 получают карту, музыку, справку, D3D и язык соответственно
;   из stscr выбирается один из 16 фонов по младшему полубайту R, чтение учитывает исходные физические сектора
;   каждый обработчик рисования из таблицы #F0FD получает индекс элемента в операнд своей обёртки
;   проверяются порты #1F, #FBDF и #FFDF с учётом сохранённых настроек, назначение остальных полей требует отдельного разбора
; -----------------------------------------
Entry:          LD A, #09
                LD (#5D06), A
                LD A, #11
                CALL #639F
                LD HL, #402A
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #13
                CALL #639F
                LD HL, #4033
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #DB00
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                CALL #DB00
                LD A, #17
                CALL #639F
                LD HL, #4045
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #DB00
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #14
                CALL #639F
                LD HL, #404E
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                XOR A
                LD L, A
                LD H, A
                LD (#C200), HL
                LD (#C202), A
                LD (#C20E), HL
                LD (#C212), HL
                LD (#C218), HL
                LD (#C21A), HL
                LD (#C210), HL
                LD (#C216), HL
                LD HL, #7FFF
                LD (#C20C), HL
                LD (#C214), HL
                LD (#C21C), HL
                LD A, #16
                CALL #639F
                LD HL, #4057
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD HL, #C000
                LD C, #0E
                LD A, #03
                CALL @TrDos.Dispatch
                LD A, #13
                CALL #639F
                LD HL, #403C
                LD DE, #5CDD
                LD BC, #0009
                LDIR
                LD C, #0A
                CALL @TrDos.Dispatch
                LD A, C
                LD C, #08
                CALL @TrDos.Dispatch
                LD A, R
                AND #0F
                LD C, A
                LD L, A
                LD H, #00
                LD DE, #4060
                ADD HL, DE
                PUSH HL
                INC C
                EX DE, HL
                XOR A
Point414C:      DEC C
                JR Z, @StationBoot.StartStation.Point4153                       ; переход, если флаг Z установлен


                ADD A, (HL)
                INC HL
                JR @StationBoot.StartStation.Point414C


Point4153:      LD DE, (#5CEB)
                LD C, A
                AND #0F
                ADD A, E
                LD E, A
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                ADD A, D
                LD D, A
                LD A, C
                RRCA
                RRCA
                RRCA
                RRCA
                AND #0F
                ADD A, D
                LD D, A
                LD A, E
                AND #0F
                LD E, A
                POP HL
                LD B, (HL)
                LD HL, #C000
                LD C, #05
                CALL @TrDos.Dispatch
                LD HL, #C000
                LD DE, #C000
                CALL #9EFF
                LD HL, #3838
                LD (#DAFE), HL
                LD (#DAFC), HL
                LD (#DAFB), HL
                LD A, #10
                CALL #639F
                DI
                LD HL, #8000
                LD A, H
                LD I, A
                LD DE, #8001
                LD BC, #0100
                LD (HL), #81
                LDIR
                LD HL, #8181
                LD (HL), #C3
                INC L
                LD (HL), #EA
                INC L
                LD (HL), #9A
                LD HL, #F3DE
                LD (#9CA6), HL
                LD HL, #8200
                LD DE, #4000
Point41BD:      LD (HL), D
                INC H
                LD (HL), E
                DEC H
                INC D
                LD A, D
                AND #07
                JP NZ, @StationBoot.StartStation.Point41D2                      ; переход, если флаг Z сброшен


                LD A, E
                ADD A, #20
                LD E, A
                JR C, @StationBoot.StartStation.Point41D2                       ; переход, если флаг Carry установлен


                LD A, D
                SUB #08
                LD D, A
Point41D2:      INC L
                JR NZ, @StationBoot.StartStation.Point41BD                      ; переход, если флаг Z сброшен


                INC H
                INC H
                XOR A
Point41D8:      LD B, #08
Point41DA:      LD (HL), A
                INC L
                DJNZ @StationBoot.StartStation.Point41DA

                INC A
                CP #20
                JR C, @StationBoot.StartStation.Point41D8                       ; переход, если флаг Carry установлен


                LD HL, #0000
                LD (#6307), HL
                LD A, #BF
                LD (#66CF), A
                LD A, #FF
                LD (#66D1), A
                LD A, #08
                LD (#6501), A
                LD A, #02
                LD (#66CD), A
                LD HL, #0000
                LD (#6550), HL
                LD HL, #6000
                LD (#64B3), HL
                IN A, (#1F)
                AND #1F
                LD A, #01
                JR NZ, @StationBoot.StartStation.Point4212                      ; переход, если флаг Z сброшен


                DEC A
Point4212:      LD E, A
                LD A, (#99B0)
                RES 7, A
                CPL
                AND E
                LD (#6639), A
                LD BC, #FBDF
                IN A, (C)
                INC A
                LD E, #01
                JR Z, @StationBoot.StartStation.Point4228                       ; переход, если флаг Z установлен


                DEC E
Point4228:      LD B, #FF
                IN A, (C)
                INC A
                LD A, #01
                JR Z, @StationBoot.StartStation.Point4232                       ; переход, если флаг Z установлен


                DEC A
Point4232:      AND E
                LD E, A
                LD A, (#99AE)
                RES 7, A
                CPL
                AND E
                LD (#65A8), A
                XOR A
                LD (#9CAA), A
                LD BC, @SettingsText.Interface
                LD DE, @InterfaceChoices.MouseOption
                CALL @Station.FormatSettingsLabel.Entry
                LD BC, @SettingsText.Controls
                LD DE, @ControlOptions.Unknown00
                CALL @Station.FormatSettingsLabel.Entry
                CALL #CB7F
                LD IX, #F0FD
                LD C, #00
                LD DE, #0010
Point4260:      LD A, (IX + #00)
                CP #80
                JR Z, @StationBoot.StartStation.Point4278                       ; переход, если флаг Z установлен


                LD L, (IX + #0C)
                LD H, (IX + #0D)
                INC HL
                LD (HL), C
                INC HL
                LD (HL), #00
                INC C
                ADD IX, DE
                JP @StationBoot.StartStation.Point4260


Point4278:      LD HL, (#6DA9)
                LD A, #0A
                CALL #9EED
                LD A, (HL)
                INC HL
                LD H, (HL)
                LD L, A
                DEC L
                DEC H
                DEC L
                DEC H
                DEC H
                ADD HL, HL
                ADD HL, HL
                ADD HL, HL
                LD (#6304), HL
                LD A, #11
                CALL #639F
                LD DE, (#983F)
                LD HL, (#9841)
                CALL #C333
                LD A, #10
                CALL #639F
                LD A, (#99B3)
                LD (#9B62), A
                LD HL, #993D
                LD (#6309), HL
                IM 2
                EI
                JP #9A59


                endmodule
                endmodule
