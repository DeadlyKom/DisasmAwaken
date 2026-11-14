                module ArchiveStart
                module HandleBankFrame
                ; Документация [меню BANK](../../Docs/BankStripArchiveConsumer.md)
                ; -----------------------------------------
                ; кадровый выбор видимого экрана, слой фона и одна из четырёх полос
                ; In:
                ;   рабочая страница меню выбрана, динамические слои и маршруты подготовлены
                ; Out:
                ;   следующий экран, фазы слоя и полосы продвинуты, изменены bitmap и атрибуты
                ;   при Enter управление передано LoadEngine без возврата в IRQ
                ; Corrupt:
                ;   HL, DE, BC, AF, отображение памяти и экран
                ; -----------------------------------------
                ; показ текущего экрана и подготовка противоположного для следующего кадра
Entry:          LD A, (@ArchiveStartData.Page.NextVisible)
                CALL @ArchiveStart.ShowScreen.Entry
                LD A, (@ArchiveStartData.Page.NextVisible)
                XOR #01
                LD (@ArchiveStartData.Page.NextVisible), A

                ; проверка Enter перед рисованием
                LD BC, #BFFE
                IN A, (C)
                BIT 0, A
                JP Z, @ArchiveStart.LoadEngine.Entry                            ; переход, если нажат Enter, передать управление загрузчику ENGINE

                ; продвижение фазы фона по трём слоям
                LD A, (@ArchiveStartData.Frame.LayerPhase)
                INC A
                CP #03
                JR C, @ArchiveStart.HandleBankFrame.StoreLayer                  ; переход, если фаза ещё меньше трёх, сохранить её

                XOR A
StoreLayer:     LD (@ArchiveStartData.Frame.LayerPhase), A

                ; выбор одного из трёх динамических слоёв
                CP #00
                JR Z, @ArchiveStart.HandleBankFrame.FirstLayer                  ; переход, если фаза 0, вывести первый слой

                CP #01
                JR Z, @ArchiveStart.HandleBankFrame.SecondLayer                 ; переход, если фаза 1, вывести второй слой

                CP #02
                JR Z, @ArchiveStart.HandleBankFrame.ThirdLayer                  ; переход, если фаза 2, вывести третий слой

                ; продвижение фазы вывода полос по четырём проходам
AdvanceStrip:   LD A, (@ArchiveStartData.Frame.StripPhase)
                INC A
                CP #04
                JR NZ, @ArchiveStart.HandleBankFrame.StoreStrip                 ; переход, если фаза полосы ещё не достигла четырёх, сохранить её

                XOR A
StoreStrip:     LD (@ArchiveStartData.Frame.StripPhase), A

                ; проверка разрешения левой полосы и выбор прямого или буферного вывода
SkipLeft:       LD A, #00
                OR A
                JR NZ, @ArchiveStart.HandleBankFrame.SkipRight                  ; переход, если левая полоса отключена, перейти к правой

                LD A, (@ArchiveStartData.Frame.StripPhase)
                CP #00
                CALL Z, @ArchiveStart.DrawLeftDirect.Entry                      ; вызов, если фаза 0, вывести левую полосу напрямую
                LD A, (@ArchiveStartData.Frame.StripPhase)
                CP #03
                CALL Z, @ArchiveStart.DrawLeftStaged.Entry                      ; вызов, если фаза 3, вывести левую полосу из буфера

                ; проверка разрешения правой полосы и выбор прямого или буферного вывода
SkipRight:      LD A, #00
                OR A
                JR NZ, @ArchiveStart.HandleBankFrame.Done                       ; переход, если правая полоса отключена, завершить кадр

                LD A, (@ArchiveStartData.Frame.StripPhase)
                CP #02
                CALL Z, @ArchiveStart.DrawRightDirect.Entry                     ; вызов, если фаза 2, вывести правую полосу напрямую
                LD A, (@ArchiveStartData.Frame.StripPhase)
                CP #01
                CALL Z, @ArchiveStart.DrawRightStaged.Entry                     ; вызов, если фаза 1, вывести правую полосу из буфера
Done:           RET

                ; заполнение атрибутов первым цветом и вывод первого слоя
FirstLayer:     LD A, #01
                CALL @ArchiveStart.FillLayerAttributes.Entry
                CALL @ArchiveStart.DrawFirstLayer.Entry
                JR @ArchiveStart.HandleBankFrame.AdvanceStrip

                ; заполнение атрибутов вторым цветом и вывод второго слоя
SecondLayer:    LD A, #02
                CALL @ArchiveStart.FillLayerAttributes.Entry
                CALL @ArchiveStart.DrawSecondLayer.Entry
                JR @ArchiveStart.HandleBankFrame.AdvanceStrip

                ; заполнение атрибутов третьим цветом и вывод третьего слоя
ThirdLayer:     LD A, #04
                CALL @ArchiveStart.FillLayerAttributes.Entry
                CALL @ArchiveStart.DrawThirdLayer.Entry
                JR @ArchiveStart.HandleBankFrame.AdvanceStrip

                endmodule
                endmodule
