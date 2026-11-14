                module Voxel
                module RotateBasisVectors
                ; Внутренние входы [алгоритм](../../Docs/GraphicsStateInternalLabels.md)
; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
                ; Документация [коэффициенты, порядок произведений и перенос IY](../../Docs/VoxelBasisRotation.md)
; -----------------------------------------
; Последовательное преобразование трёх векторов ориентации #9B00..#9B11 по углам #9B14, #9B12 и #9B13
; исходная запись 20, файловые смещения #2500..#28A0
                ; In:
                ;   #9B00..#9B11 - три исходных вектора по три слова, #9B12..#9B14 - углы
                ;   IY - входное состояние накопителя SignedSeededProduct, подключён банк с VOXAL0
                ;   четыре байта ниже входного SP доступны для временных PUSH и CALL, стек не пересекает базис и изменяемый код, IRQ не вмешиваются
                ; Out:
                ;   исходные девять слов векторов обновлены по трём последовательным преобразованиям
                ;   при хотя бы одном ненулевом угле IY содержит накопитель последнего произведения, при трёх нулевых углах IY сохраняется
                ;   IX, I, IM и IFF сохраняются, SP обычного возврата увеличен на два
                ;   при трёх нулевых углах HL=исходный C22, DE и BC сохраняются, AF=0054, HL', DE', BC' и AF' сохраняются
                ;   девять слов базиса и девять промежуточных слов записываются даже при нулевых углах, R меняется
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', IY при ненулевых углах, R, девять слов базиса, девять слов операндов, байт E913 и четыре временных байта CPU-стека
                ; Note:
                ;   IX кодом этой цепочки не используется, промежуточные слова сохраняются в изменяемых операндах
                ;   при нулевых углах исходные девять слов сохраняются, ненулевые используют две страницы таблицы #EA00 и #EB00
                ;   таблица содержит round(16384 × cos(2π×индекс/256)), индекс угол минус 64 даёт синус
                ;   три вектора занимают девять слов #9B00..#9B11, поля углов являются байтами
                ;   первый этап преобразует первые две компоненты, второй смешивает вторую и третью, третий первую и третью
                ;   промежуточные компоненты сохраняются в непосредственных операндах, сумма проверяется флагом переполнения
                ;   все произведения используют SignedSeededProduct, IY переносится от каждого вызова к следующему
                ;   Carry после второго произведения снят, при переполнении сложения выполняется исходное отрицание с поправкой 8000 в 7FFF
                ;   1800 сценариев сверили всю RAM вне четырёх временных байтов стека и точную кратность остальных записей, максимальная глубина стека равна четырём
                ;   при трёх нулевых углах выполняется 48 M1 без записей CPU-стека и без вызовов произведения, R увеличивает младшие семь битов на 48 modulo 128
                ;   для ненулевых углов R сверялся по M1 исполненных опкодов, независимая общая формула M1, точное время, IRQ и нативный запуск не доказаны
; -----------------------------------------
                ; Физические слова [базис](../../Docs/ActionRenderBasis.md)
                ; проверка первого угла перед изменением первой и второй компонент трёх векторов
Entry:          LD A, (@ActionRenderPhases.Value.Phase2)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateFirst                    ; переход, если первый угол ненулевой, выполнить соответствующее преобразование


                LD HL, (@ActionRenderBasis.C00)
                LD (#E7AF), HL
                LD HL, (@ActionRenderBasis.C01)
                LD (#E801), HL
                LD HL, (@ActionRenderBasis.C02)
                LD (#E853), HL
                LD HL, (@ActionRenderBasis.C10)
                LD (#E67B), HL
                LD HL, (@ActionRenderBasis.C11)
                LD (#E6CD), HL
                LD HL, (@ActionRenderBasis.C12)
                LD (#E71F), HL
                JP @Voxel.RotateBasisVectors.CheckSecond


RotateFirst:    LD L, A
                LD H, @VoxelBasisRotationConst.CosineLowPage
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB @VoxelBasisRotationConst.QuarterTurn
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
                LD HL, (@ActionRenderBasis.C00)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C10)
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
                LD HL, (@ActionRenderBasis.C00)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C10)
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
                LD HL, (@ActionRenderBasis.C01)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C11)
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
                LD HL, (@ActionRenderBasis.C01)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C11)
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
                LD HL, (@ActionRenderBasis.C02)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH BC
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C12)
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
                LD HL, (@ActionRenderBasis.C02)
                CALL @Voxel.SignedSeededProduct.Entry
                PUSH HL
                EXX
                PUSH DE
                EXX
                POP BC
                LD HL, (@ActionRenderBasis.C12)
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
CheckSecond:    LD A, (@ActionRenderPhases.Value.Phase0)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateSecond                   ; переход, если второй угол ненулевой, выполнить соответствующее преобразование


                LD HL, (@ActionRenderBasis.C20)
                LD (#E7BA), HL
                LD HL, (@ActionRenderBasis.C21)
                LD (#E80C), HL
                LD HL, (@ActionRenderBasis.C22)
                LD (#E85E), HL
                LD HL, (#E67B)
                LD (@ActionRenderBasis.C10), HL
                LD HL, (#E6CD)
                LD (@ActionRenderBasis.C11), HL
                LD HL, (#E71F)
                LD (@ActionRenderBasis.C12), HL
                JP @Voxel.RotateBasisVectors.CheckThird


RotateSecond:   LD L, A
                LD H, @VoxelBasisRotationConst.CosineLowPage
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB @VoxelBasisRotationConst.QuarterTurn
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
                LD HL, (@ActionRenderBasis.C20)
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
Stage2V0C1:     LD (@ActionRenderBasis.C10), HL
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
                LD HL, (@ActionRenderBasis.C20)
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
                LD HL, (@ActionRenderBasis.C21)
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
Stage2V1C1:     LD (@ActionRenderBasis.C11), HL
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
                LD HL, (@ActionRenderBasis.C21)
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
                LD HL, (@ActionRenderBasis.C22)
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
Stage2V2C1:     LD (@ActionRenderBasis.C12), HL
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
                LD HL, (@ActionRenderBasis.C22)
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
CheckThird:     LD A, (@ActionRenderPhases.Value.Phase1)
                AND A
                JP NZ, @Voxel.RotateBasisVectors.RotateThird                    ; переход, если третий угол ненулевой, выполнить соответствующее преобразование


                LD HL, (#E7AF)
                LD (@ActionRenderBasis.C00), HL
                LD HL, (#E801)
                LD (@ActionRenderBasis.C01), HL
                LD HL, (#E853)
                LD (@ActionRenderBasis.C02), HL
                LD HL, (#E7BA)
                LD (@ActionRenderBasis.C20), HL
                LD HL, (#E80C)
                LD (@ActionRenderBasis.C21), HL
                LD HL, (#E85E)
                LD (@ActionRenderBasis.C22), HL
                RET


RotateThird:    LD L, A
                LD H, @VoxelBasisRotationConst.CosineLowPage
                LD E, (HL)
                INC H
                LD D, (HL)
                SUB @VoxelBasisRotationConst.QuarterTurn
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
Stage3V0C0:     LD (@ActionRenderBasis.C00), HL
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
Stage3V0C2:     LD (@ActionRenderBasis.C20), HL
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
Stage3V1C0:     LD (@ActionRenderBasis.C01), HL
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
Stage3V1C2:     LD (@ActionRenderBasis.C21), HL
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
Stage3V2C0:     LD (@ActionRenderBasis.C02), HL
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
Stage3V2C2:     LD (@ActionRenderBasis.C22), HL
                RET


                endmodule
                endmodule
