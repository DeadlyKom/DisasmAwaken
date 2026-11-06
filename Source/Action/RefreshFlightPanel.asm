                module Action
                module RefreshFlightPanel
                ; Документация [алгоритм и проверка](../../Docs/ActionRefreshPanel.md)
                ; -----------------------------------------
                ; Принудительное обновление шести шкал и четырёх пар счётчика панели полёта
                ; исходная запись 17, банк 5, перенесённое ядро ACTION 6000..7F8E, смещения #0382..#03AE
                ; In:
                ;   HL, DE, BC и AF числовых аргументов не задают, прежние шесть запросов будут заменены единицами
                ;   ActionPanelGaugesState и ActionPreferredByteState задают источники шести шкал, ControlsBcdCounterState задаёт четыре байта счётчика
                ;   7FFD не заблокирован, банк 0 содержит ACTION, банк 1 CONTROL и шрифт, экран доступен через общий банк 5
                ;   CPU-стек в общей RAM содержит внешний возврат и допускает восемь временных байтов, IRQ не вмешиваются
                ; Out:
                ;   HL содержит LowPairs, DE содержит HighPairs, BC=FF26 после вывода всех восьми знаков
                ;   AF соответствует последнему пиксельному OR в старшей тетраде экранного байта 5613
                ;   HL'=5613, DE' указывает последнюю строку пары знаков старшей тетрады D, B' содержит сохранённую соседнюю тетраду, C'=F0, AF'=1330
                ;   IX, IY, I, IM и IFF сохранены, SP=входной SP+2
                ;   перерисованы все шесть шкал и восемь знаков, SecondRequest=1, пять остальных запросов равны нулю
                ;   байты счётчика и источники шкал не изменены, после 14 записей в 7FFD итоговая конфигурация равна 11
                ;   R увеличен на стоимость обоих рисователей и 29 M1 самой обёртки с двумя вызовами селектора
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', R, экранные байты панели, шесть запросов, восемь байтов CPU-стека и 7FFD
                ; Note:
                ;   хвостовой JP в DrawBcdCounter использует внешний возврат, лишнего CALL и нового слова стека нет
                ;   FPanelRefreshGaugeFrame описывает самый глубокий участок вызова шкалы и выбора банка, новая память не выделяется
                ;   не-BCD тетрады выводятся как исходные знаки пунктуации, арифметического изменения счётчика нет
                ;   6624 сценария композиционной проверки сверяют регистры включая R, восемь физических банков, каждую запись и OUT
                ;   исходно заблокированный порт, полное произведение всех полей, IRQ, точные такты, сборка и нативный запуск вне проверки
                ; -----------------------------------------
                ; Выбор верхнего банка ACTION перед чтением источников шкал, экран остаётся в общем банке 5.
Entry:          LD A, @ActionBankPage.Runtime
                CALL @Action.SelectMemoryPage.Entry
                ; Создание шести запросов в существующих операндах UpdatePanelGauges, старые коды заменяются.
                LD A, @ActionPanelRefreshConst.RequestAll
                LD (@ActionPanelGaugesState.SixthRequest), A
                LD (@ActionPanelGaugesState.ThirdRequest), A
                LD (@ActionPanelGaugesState.FirstRequest), A
                LD (@ActionPanelGaugesState.FifthRequest), A
                LD (@ActionPanelGaugesState.FourthRequest), A
                LD (@ActionPanelGaugesState.SecondRequest), A
                ; Обновление всех шести шкал, второй запрос сохраняется, остальные потребляются.
                CALL @Action.UpdatePanelGauges.Entry
                ; Выбор CONTROL и его шрифта для последующего вывода четырёх пар счётчика.
                LD A, @ActionBankPage.Controls
                CALL @Action.SelectMemoryPage.Entry
                ; Чтение младших и старших BCD-пар в исходном физическом порядке, счётчик не изменяется.
                LD HL, (@ControlsBcdCounterState.LowPairs)
                LD DE, (@ControlsBcdCounterState.HighPairs)
                ; Разрешение всей цепочки старших пар, значимы только биты 0..2 исходной маски FF.
                LD B, @ActionPanelRefreshConst.AllCounterPairs
                ; Хвостовая передача к рисователю цифр, его RET использует уже существующий внешний возврат.
                JP @Controls.DrawBcdCounter.Entry

                endmodule
                endmodule
