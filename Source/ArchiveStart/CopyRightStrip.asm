                module ArchiveStart
                module CopyRightStrip
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; зеркальный перенос шести байтов каждой строки правой полосы
                ; In:
                ;   HL - адрес байта ненулевой высоты, далее строки растра
                ;   DE - исходный адрес экрана из заголовка
                ; Out:
                ;   растр записан справа налево с обращением битов, HL указывает за данные
                ;   DE указывает на следующую строку у правого края
                ; Corrupt:
                ;   HL, DE, BC, AF, AF'
                ; Note:
                ;   к младшему байту адреса прибавляется 31 без переноса в старший
                ; -----------------------------------------
                ; вычисление правого края и подготовка таблицы обращения битов
Entry:          LD A, E
                ADD A, @ArchiveStartConst.RightEdge
                LD E, A
                LD A, (HL)
                INC HL
                LD B, HIGH(@ArchiveStartMirrorTable.Value)

                ; сохранение адреса строки и вывод шести обращённых байтов
CopyRow:        EX AF, AF'
                PUSH DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE
                LD C, (HL)
                LD A, (BC)
                LD (DE), A
                INC HL
                DEC DE

                ; переход к следующей строке и проверка оставшейся высоты
                POP DE
                CALL @ArchiveStart.NextStripRow.Entry
                EX AF, AF'
                DEC A
                JR NZ, @ArchiveStart.CopyRightStrip.CopyRow                     ; переход, если остались строки правой полосы

                RET

                endmodule
                endmodule
