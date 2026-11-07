                module Voxel
                module RotateBasisVectors
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
; -----------------------------------------
; Последовательное преобразование трёх векторов ориентации #9B00..#9B11 по углам #9B14, #9B12 и #9B13
; исходная запись 20, файловые смещения #2500..#28A0
; In:
;   #9B00..#9B11 - три исходных вектора по три слова, #9B12..#9B14 - углы
;   IY - входное состояние накопителя SignedSeededProduct, подключён банк с VOXAL0
; Out:
;   исходные девять слов векторов обновлены по трём последовательным преобразованиям
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IY
; Note:
;   IX кодом этой цепочки не используется, промежуточные слова сохраняются в изменяемых операндах
;   при нулевых углах исходные девять слов сохраняются, ненулевые используют две страницы таблицы #EA00 и #EB00
;   математическое сохранение длины вектора не доказано, исходная зависимость от IY не исправляется
;   три вектора занимают девять слов #9B00..#9B10, поля углов являются байтами
;   нулевой угол обходится копированием текущих компонент, ненулевой использует две страницы таблицы #EA00 и #EB00
;   первый этап преобразует первые две компоненты, второй смешивает вторую и третью, третий первую и третью
;   промежуточные компоненты сохраняются в непосредственных операндах, сумма проверяется флагом переполнения
;   все произведения используют SignedSeededProduct, его зависимость от входного IY сохранена буквально
; -----------------------------------------
                ; проверка первого угла перед изменением первой и второй компонент трёх векторов
Entry:          LD A, (#9B14)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateFirst                    ; переход, если первый угол ненулевой, выполнить соответствующее преобразование


                LD HL, (#9B00)
                LD (#E7AF), HL
                LD HL, (#9B06)
                LD (#E801), HL
                LD HL, (#9B0C)
                LD (#E853), HL
                LD HL, (#9B02)
                LD (#E67B), HL
                LD HL, (#9B08)
                LD (#E6CD), HL
                LD HL, (#9B0E)
                LD (#E71F), HL
                JP @Voxel.RotateBasisVectors.CheckSecond


RotateFirst:    LD L, A
                LD H, #EA
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB #40
                LD L, A
                LD B, (HL)
                DEC H
                LD C, (HL)
                LD A, C
                CPL
                LD L, A
                LD A, B
                CPL
                LD H, A
                INC HL
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B00)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B02)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V0C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V0C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V0C0:     LD (#E7AF), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#9B00)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B02)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V0C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V0C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V0C1:     LD (#E67B), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B06)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B08)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V1C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V1C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V1C0:     LD (#E801), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#9B06)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B08)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V1C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V1C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V1C1:     LD (#E6CD), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B0C)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B0E)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V2C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V2C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V2C0:     LD (#E853), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#9B0C)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B0E)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V2C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage1V2C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage1V2C1:     LD (#E71F), HL
CheckSecond:    LD A, (#9B12)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateSecond                   ; переход, если второй угол ненулевой, выполнить соответствующее преобразование


                LD HL, (#9B04)
                LD (#E7BA), HL
                LD HL, (#9B0A)
                LD (#E80C), HL
                LD HL, (#9B10)
                LD (#E85E), HL
                LD HL, (#E67B)
                LD (#9B02), HL
                LD HL, (#E6CD)
                LD (#9B08), HL
                LD HL, (#E71F)
                LD (#9B0E), HL
                JP @Voxel.RotateBasisVectors.CheckThird


RotateSecond:   LD L, A
                LD H, #EA
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB #40
                LD L, A
                LD B, (HL)
                DEC H
                LD C, (HL)
                LD A, C
                CPL
                LD L, A
                LD A, B
                CPL
                LD H, A
                INC HL
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B04)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V0C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V0C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V0C1:     LD (#9B02), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#E67B)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B04)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V0C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V0C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V0C2:     LD (#E7BA), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B0A)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V1C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V1C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V1C1:     LD (#9B08), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#E6CD)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B0A)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V1C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V1C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V1C2:     LD (#E80C), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#9B10)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V2C1                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V2C1                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V2C1:     LD (#9B0E), HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, (#E71F)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#9B10)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V2C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage2V2C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage2V2C2:     LD (#E85E), HL
CheckThird:     LD A, (#9B13)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateThird                    ; переход, если третий угол ненулевой, выполнить соответствующее преобразование


                LD HL, (#E7AF)
                LD (#9B00), HL
                LD HL, (#E801)
                LD (#9B06), HL
                LD HL, (#E853)
                LD (#9B0C), HL
                LD HL, (#E7BA)
                LD (#9B04), HL
                LD HL, (#E80C)
                LD (#9B0A), HL
                LD HL, (#E85E)
                LD (#9B10), HL
                RET


RotateThird:    LD L, A
                LD H, #EA
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB #40
                LD L, A
                LD B, (HL)
                DEC H
                LD C, (HL)
                LD A, C
                CPL
                LD L, A
                LD A, B
                CPL
                LD H, A
                INC HL
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V0C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V0C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V0C0:     LD (#9B00), HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#E7AF)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#E7BA)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V0C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V0C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V0C2:     LD (#9B04), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V1C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V1C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V1C0:     LD (#9B06), HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#E801)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#E80C)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V1C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V1C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V1C2:     LD (#9B0A), HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH HL
                EXX
                POP BC
                LD HL, #0000
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V2C0                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V2C0                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V2C0:     LD (#9B0C), HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (#E853)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (#E85E)
                CALL @Voxel.SignedSeededProduct.Entry
                POP DE
                ADC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V2C2                     ; переход, если сумма произведений не дала знакового переполнения, сохранить компоненту


                EX DE, HL
                LD HL, #0000
                OR A
                SBC HL, DE
                JP PO, @Voxel.RotateBasisVectors.Stage3V2C2                     ; переход, если отрицание переполненной суммы допустимо, сохранить исправленную компоненту


                DEC HL
Stage3V2C2:     LD (#9B10), HL
                RET


                endmodule
                endmodule
