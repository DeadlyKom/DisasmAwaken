                module Voxel
                module Multiply7BitWord
                ; Внутренние входы [алгоритм](../../Docs/ArithmeticFinalInternalLabels.md)
                ; Документация [арифметика и R](../../Docs/VoxelSmallArithmetic.md)
                ; Документация [Voxel](../../Docs/FunctionDetails/Voxel.md)
                ; -----------------------------------------
                ; Умножение младших семи битов A на BC с результатом HL modulo #10000
                ; исходная запись 21, файловые смещения #0D31..#0D56
                ; In:
                ;   BC - беззнаковое слово, AF - A множитель, учитываются только биты 6..0
                ;   код VOXAL доступен, CPU-стек содержит внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL - ((A AND #7F) * BC) modulo #10000
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP после RET равен входному SP+2, записей в память нет
                ; Corrupt:
                ;   HL, AF, R
                ; Note:
                ;   R меняется за 22 + popcount(A AND #7F) + (A AND #01) M1, бит 7 сохраняется
                ;   старший бит A пропускается двумя первыми RLA, это не полное умножение восьмибитного A
                ;   DE, BC, альтернативные и индексные регистры сохраняются
                ;   развёрнутый сдвиговый алгоритм содержит семь условных добавлений BC
                ;   результат ограничен 16 битами, переносы сверх HL в результат не включаются
                ; -----------------------------------------
                ; расчёт произведения по битам 6..0 A, старший бит множителя пропускается
Entry:          LD HL, #0000
                RLA
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit5                         ; переход, если бит 6 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit5:       ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit4                         ; переход, если бит 5 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit4:       ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit3                         ; переход, если бит 4 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit3:       ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit2                         ; переход, если бит 3 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit2:       ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit1                         ; переход, если бит 2 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit1:       ADD HL, HL
                RLA
                JR NC, @Voxel.Multiply7BitWord.NextBit0                         ; переход, если бит 1 исходного A нулевой, слагаемое BC пропускается


                ADD HL, BC
NextBit0:       ADD HL, HL
                RLA
                RET NC                                                          ; выход, если бит 0 исходного A нулевой, произведение уже готово

                ADD HL, BC
                RET


                endmodule
                endmodule
