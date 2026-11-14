                module ArchiveStart
                module ScanRightKeys
                ; Документация [клавиши и селекторы](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; опрос четырёх клавиш правой стороны в порядке приоритета
                ; In:
                ;   доступна матрица клавиатуры и подключён аппаратный селектор страниц
                ; Out:
                ;   при нажатии выбран обработчик первой клавиши, иначе фиксатор сброшен
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, при изменении селектора отображение страницы
                ; -----------------------------------------
                ; проверка клавиши I, увеличивающей младший индекс правой стороны
Entry:          LD IX, @ArchiveStartKeys.KeyI
                LD BC, #DFFE
                IN A, (C)
                BIT 2, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша I

                ; проверка клавиши Y, уменьшающей младший индекс правой стороны
                LD IX, @ArchiveStartKeys.KeyY
                LD BC, #DFFE
                IN A, (C)
                BIT 4, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша Y

                ; проверка клавиши U, увеличивающей старший индекс правой стороны
                LD IX, @ArchiveStartKeys.KeyU
                LD BC, #DFFE
                IN A, (C)
                BIT 3, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша U

                ; проверка клавиши 7, уменьшающей старший индекс правой стороны
                LD IX, @ArchiveStartKeys.Key7
                LD BC, #EFFE
                IN A, (C)
                BIT 3, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша 7

                ; сброс фиксатора после отпускания всех четырёх клавиш группы
                XOR A
                LD (@ArchiveStartData.Frame.RightKeyLatch), A
                RET

                endmodule
                endmodule
