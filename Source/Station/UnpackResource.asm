                module Station
                module UnpackResource
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; -----------------------------------------
; Распаковка ресурса с заголовком, переносом упакованного потока и обработкой ссылок
; исходная запись 4, файловые смещения #3EFF..#4013
; In:
;   Unknown, регистровый контракт ещё не доказан
; Out:
;   исходный поток управления, включая переходы в соседние фрагменты
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX, IY, консервативная верхняя граница
; Note:
;   граница файла не доказывает границу логической процедуры
;   состояние самомодификации и активной страницы учитывается отдельно
; -----------------------------------------
Entry:          PUSH DE
                PUSH HL
                INC HL
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                INC HL
                DEC BC
                EX DE, HL
                ADD HL, BC
                EX DE, HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                DEC BC
                POP HL
                ADD HL, BC
                SBC HL, DE
                ADD HL, DE
                JR C, @Station.UnpackResource.Point9F18                         ; переход, если флаг Carry установлен


                LD D, H
                LD E, L
Point9F18:      LDDR
                EX DE, HL
                POP DE
                LD C, #0C
                ADD HL, BC
                PUSH HL
                POP IX
                LD A, #03
Point9F24:      DEC HL
                LD B, (HL)
                DEC HL
                LD C, (HL)
                PUSH BC
                DEC A
                JR NZ, @Station.UnpackResource.Point9F24                        ; переход, если флаг Z сброшен


                LD B, A
                EXX
                LD D, #BF
                LD C, #10
                CALL @Station.UnknownA014.Entry
Point9F35:      LD A, (IX + #00)
                INC IX
                EXX
Point9F3B:      LD (DE), A
                INC DE
Point9F3D:      EXX
Point9F3E:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9F44

                CALL @Station.UnknownA014.Entry
Point9F44:      JR C, @Station.UnpackResource.Point9F35                         ; переход, если флаг Carry установлен


                LD E, #01
Point9F48:      LD A, #80
Point9F4A:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9F50

                CALL @Station.UnknownA014.Entry
Point9F50:      RLA
                JR C, @Station.UnpackResource.Point9F4A                         ; переход, если флаг Carry установлен


                CP #03
                JR C, @Station.UnpackResource.Point9F5C                         ; переход, если флаг Carry установлен


                ADD A, E
                LD E, A
                XOR C
                JR NZ, @Station.UnpackResource.Point9F48                        ; переход, если флаг Z сброшен


Point9F5C:      ADD A, E
                CP #04
                JR Z, @Station.UnpackResource.Point9FC3                         ; переход, если флаг Z установлен


                ADC A, #FF
                CP #02
                EXX
Point9F66:      LD C, A
Point9F67:      EXX
                LD A, #BF
                JR C, @Station.UnpackResource.Point9F81                         ; переход, если флаг Carry установлен


Point9F6C:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9F72

                CALL @Station.UnknownA014.Entry
Point9F72:      RLA
                JR C, @Station.UnpackResource.Point9F6C                         ; переход, если флаг Carry установлен


                JR Z, @Station.UnpackResource.Point9F7C                         ; переход, если флаг Z установлен


                INC A
                ADD A, D
                JR NC, @Station.UnpackResource.Point9F83                        ; переход, если флаг Carry сброшен


                SUB D
Point9F7C:      INC A
                JR NZ, @Station.UnpackResource.Point9F8C                        ; переход, если флаг Z сброшен


                LD A, #EF
Point9F81:      RRCA
                CP A
Point9F83:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9F89

                CALL @Station.UnknownA014.Entry
Point9F89:      RLA
                JR C, @Station.UnpackResource.Point9F83                         ; переход, если флаг Carry установлен


Point9F8C:      EXX
                LD H, #FF
                JR Z, @Station.UnpackResource.Point9F9A                         ; переход, если флаг Z установлен


                LD H, A
                INC A
                LD A, (IX + #00)
                INC IX
                JR Z, @Station.UnpackResource.Point9FA5                         ; переход, если флаг Z установлен


Point9F9A:      LD L, A
                ADD HL, DE
                LDIR
Point9F9E:      JR @Station.UnpackResource.Point9F3D


Point9FA0:      EXX
                RRC D
                JR @Station.UnpackResource.Point9F3E


Point9FA5:      CP #E0
                JR C, @Station.UnpackResource.Point9F9A                         ; переход, если флаг Carry установлен


                RLCA
                XOR C
                INC A
                JR Z, @Station.UnpackResource.Point9FA0                         ; переход, если флаг Z установлен


                SUB #10
Point9FB0:      LD L, A
                LD C, A
                LD H, #FF
                ADD HL, DE
                LDI
                LD A, (IX + #00)
                INC IX
                LD (DE), A
                INC HL
                INC DE
                LD A, (HL)
                JP @Station.UnpackResource.Point9F3B


Point9FC3:      LD A, #80
Point9FC5:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9FCB

                CALL @Station.UnknownA014.Entry
Point9FCB:      ADC A, A
                JR NZ, @Station.UnpackResource.Point9FF2                        ; переход, если флаг Z сброшен


                JR C, @Station.UnpackResource.Point9FC5                         ; переход, если флаг Carry установлен


                LD A, #FC
                JR @Station.UnpackResource.Point9FF5


Point9FD4:      LD B, A
                LD C, (IX + #00)
                INC IX
                CCF
                JR @Station.UnpackResource.Point9F67


Point9FDD:      CP #0F
                JR C, @Station.UnpackResource.Point9FD4                         ; переход, если флаг Carry установлен


                JR NZ, @Station.UnpackResource.Point9F66                        ; переход, если флаг Z сброшен


                LD B, #03
                EX DE, HL
Point9FE6:      POP DE
                LD (HL), E
                INC HL
                LD (HL), D
                INC HL
                DJNZ @Station.UnpackResource.Point9FE6

                LD HL, #2758
                EXX
                RET


Point9FF2:      SBC A, A
                LD A, #EF
Point9FF5:      ADD HL, HL
                DJNZ @Station.UnpackResource.Point9FFB

                CALL @Station.UnknownA014.Entry
Point9FFB:      RLA
                JR C, @Station.UnpackResource.Point9FF5                         ; переход, если флаг Carry установлен


                EXX
                JR NZ, @Station.UnpackResource.Point9FB0                        ; переход, если флаг Z сброшен


                BIT 7, A
                JR Z, @Station.UnpackResource.Point9FDD                         ; переход, если флаг Z установлен


                SUB #EA
                ADD A, A
                LD B, A
PointA009:      LD A, (IX + #00)
                INC IX
                LD (DE), A
                INC DE
                DJNZ @Station.UnpackResource.PointA009

                JR @Station.UnpackResource.Point9F9E


                endmodule
                endmodule
