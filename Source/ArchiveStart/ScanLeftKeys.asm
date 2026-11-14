                module ArchiveStart
                module ScanLeftKeys
                ; Документация [клавиши и селекторы](../../Docs/BankArchiveTileLayers.md)
                ; -----------------------------------------
                ; опрос четырёх клавиш левой стороны в порядке приоритета
                ; In:
                ;   доступна матрица клавиатуры и подключён аппаратный селектор страниц
                ; Out:
                ;   при нажатии выбран обработчик первой клавиши, иначе фиксатор сброшен
                ; Corrupt:
                ;   HL, DE, BC, AF, AF', IX, при изменении селектора отображение страницы
                ; -----------------------------------------
                ; проверка клавиши D, увеличивающей младший индекс левой стороны
Entry:          LD IX, @ArchiveStartKeys.KeyD
                LD BC, #FDFE
                IN A, (C)
                BIT 2, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша D

                ; проверка клавиши A, уменьшающей младший индекс левой стороны
                LD IX, @ArchiveStartKeys.KeyA
                LD BC, #FDFE
                IN A, (C)
                BIT 0, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша A

                ; проверка клавиши S, увеличивающей старший индекс левой стороны
                LD IX, @ArchiveStartKeys.KeyS
                LD BC, #FDFE
                IN A, (C)
                BIT 1, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша S

                ; проверка клавиши W, уменьшающей старший индекс левой стороны
                LD IX, @ArchiveStartKeys.KeyW
                LD BC, #FBFE
                IN A, (C)
                BIT 1, A
                JP Z, @ArchiveStart.ApplySelectorKey.Entry                      ; переход, если нажата клавиша W

                ; сброс фиксатора после отпускания всех четырёх клавиш группы
                XOR A
                LD (@ArchiveStartData.Frame.LeftKeyLatch), A
                RET

                endmodule
                endmodule
