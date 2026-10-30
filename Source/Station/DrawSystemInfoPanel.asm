                module Station
                module DrawSystemInfoPanel
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [порядок полей, два ключа, список до шести вариантов и банковые договоры](../../Docs/SystemInfoPanel.md)
; -----------------------------------------
; Рисование дальности топлива, расстояния, выбранной и текущей систем с перечнем планет
; исходная запись 4, файловые смещения #193B..#1AE3
; In:
;   SystemInfoState.ItemIndex задаёт FInterfaceItem панели с допустимым размещением по DrawCaptionItem, банк станции 0 выбран
;   SignatureInput.Entry и MapSelection содержат читаемые текущий и выбранный пятибайтовые ключи, RangeSource читаем
;   в банке 1 доступен KARTA, шрифт, тексты, адресные и индексные таблицы готовы, paging разрешён, тень порта согласована с устройством
;   для обычного полного рисунка текстовое окно вмещает позиции вплоть до Y=168 и все три строки PrintSystemTraits
;   действуют договоры DrawCaptionItem и его HALT, печатателей, MeasureCoordinateDistance, BuildSystemName, ClassifyKeyRegion, PrintVariantLabel и DescribeKeyBanked
;   указатель защищён вызывающим окружением, CPU-стек вне переключаемого окна и областей рисунка
; Out:
;   нарисованы рамка и заголовок, Style=0, затем подписи и значения дальности топлива, расстояния, выбранной и текущей систем
;   показываемая дальность равна старшему байту RangeSource, если он ненулевой, иначе младшему байту, делённому на два без округления
;   расстояние вычислено между ключами выбранной и текущей точек, код FF показан дефисом, остальные коды десятичным числом
;   у обеих систем показаны политическая область, имя и подпись варианта, BuildSystemName дважды переиспользует Buffer, после выхода там имя текущей системы
;   нулевой счётчик выбранного ключа печатает Планет нет., ненулевой печатает признаки системы и ровно N подписей планет с индексами 0..N-1
;   перечень размещён тремя колонками X=0,32,64 на Y=96,104, N=1..6, обе исходные развёрнутые строки сохранены
;   при нулевом счётчике текущего ключа возвращаются HL, DE, BC и AF от DescribeCurrentKey, новых строк его признаков нет
;   при ненулевом счётчике текущего ключа возвращается результат PrintSystemTraits в HL, DE и AF, BC содержит сохранённые AF характеристики, B=N, C=F
;   для полностью успешного текста последнего пути HL=A822, DE содержит D=область и E=экономика текущей системы, AF=0045
;   альтернативные HL, DE, BC соответствуют последнему BuildSystemName и сохраняются последующими помощниками, AF' соответствует возвращаемой странице DescribeCurrentKey
;   IX, IY, I и IFF сохраняются инструкциями при договоре HALT, SP обычного возврата равен входному SP+2
;   итоговая страница равна (входная CurrentPage AND F8) OR 10, прежний номер банка не восстанавливается
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', экран, текстовое окно, рабочий ключ, Buffer и LastDistance
; Note:
;   имя, политическая область и признаки используют разные алгоритмы, политическая область не равна коду строя H
;   начальный Style всегда заменяется нулём и не восстанавливается, отказы печати не прекращают последующие поля
;   PUSH AF вокруг PrintSystemTraits снимается в BC, итоговый AF прежнего DescribeKey не восстанавливается
;   для первых пяти подписей вариантов сохраняются AF и BC на стеке, шестая вызывается без этих сохранений
;   модель проверила 192 полных вызова и аргументы реальных помощников, независимый oracle всего bitmap панели не заявлен
; -----------------------------------------
                ; чтение изменяемого индекса панели для регистрации рамки, заголовка и внутреннего окна
Entry:          LD HL, #0000
                CALL @Station.DrawCaptionItem.Entry
                ; установка политики печати без автоматического переноса и вывод исходных подписей полей
                XOR A
                LD (@TextWindow.Style), A
                LD HL, @SystemInfoText.Template
                CALL @Station.PrintText.Entry
                ; выбор позиции дальности топлива X=49,Y=8 внутри окна панели
                LD HL, #0831
                LD (@TextWindow.CursorX), HL
                ; чтение слова запаса дальности, тот же источник участвует в геометрии дуги карты
                LD HL, (@SystemInfoState.RangeSource)
                ; проверка старшего байта, ненулевой байт используется напрямую как показываемая дальность
                LD A, H
                AND A
                JR NZ, @Station.DrawSystemInfoPanel.PrintFuel                   ; переход, если старший байт RangeSource ненулевой, вывести его без деления

                ; расчёт половины младшего байта при нулевом старшем, Carry сброшен предшествующим AND
                LD A, L
                RRA
                ; расширение показываемой дальности в BC и десятичный вывод без ведущих нулей
PrintFuel:      LD C, A
                LD B, #00
                XOR A
                CALL @Station.PrintWord.Entry
                ; загрузка слов выбранной точки в основной набор для MeasureCoordinateDistance
                LD DE, (@MapSelection.FirstWord)
                LD BC, (@MapSelection.SecondWord)
                ; загрузка слов текущей точки в альтернативный набор того же измерителя
                EXX
                LD DE, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD BC, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                EXX
                ; выбор банка карты с сохранением управляющих битов отображаемого экрана
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; измерение полного расстояния с записью байта результата в LastDistance
                CALL @Map.MeasureCoordinateDistance.Entry
                ; сохранение измеренного кода в C до возврата станционного банка
                LD C, A
                LD B, #00
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; выбор позиции расстояния X=49,Y=16 и проверка кода переполнения FF
                LD HL, #1031
                LD (@TextWindow.CursorX), HL
                LD A, #FF
                CP C
                JR NZ, @Station.DrawSystemInfoPanel.PrintDistance               ; переход, если расстояние не равно коду FF, вывести число вместо дефиса

                ; вывод дефиса при недоступном полном расстоянии
                LD A, #2D
                CALL @Station.DrawGlyph.Entry
                JR @Station.DrawSystemInfoPanel.DrawSelected

                ; десятичный вывод допустимого байта расстояния без дополнительных нулей
PrintDistance:  XOR A
                CALL @Station.PrintWord.Entry
                ; чтение ключа выбранной системы для построения имени в общем Buffer
DrawSelected:   LD HL, (@MapSelection.FirstWord)
                LD DE, (@MapSelection.SecondWord)
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                CALL @Map.BuildSystemName.Entry
                ; повторное чтение первого слова после меняющего наборы BuildSystemName, классификация политической области
                LD HL, (@MapSelection.FirstWord)
                CALL @Map.ClassifyKeyRegion.Entry
                ; сохранение кода политической области в AF альтернативного набора на время смены банка
                EX AF, AF'
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; выбор первой строки выбранной системы X=0,Y=40 и списка политических областей
                LD HL, #2800
                LD (@TextWindow.CursorX), HL
                LD HL, @SystemInfoText.PoliticalAreas
                EX AF, AF'
                CALL @Station.PrintAfterLF.Entry
                ; выбор строки имени выбранной системы X=0,Y=48 и печать общего Buffer
                LD HL, #3000
                LD (@TextWindow.CursorX), HL
                LD HL, @SystemNameState.Buffer
                CALL @Station.PrintText.Entry
                ; выбор KARTA для печати подписи выбранного варианта X=34,Y=56
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                LD HL, #3822
                LD (@TextWindow.CursorX), HL
                LD HL, (@MapSelection.FirstWord)
                LD DE, (@MapSelection.SecondWord)
                LD A, (@MapSelection.Variant)
                CALL @Map.PrintVariantLabel.Entry
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; чтение пятибайтового выбранного ключа для признаков и количества планет
                LD A, (@MapSelection.Variant)
                LD HL, (@MapSelection.FirstWord)
                LD DE, (@MapSelection.SecondWord)
                CALL @Station.DescribeKeyBanked.Entry
                ; проверка числа планет выбранной системы, нулю соответствует отдельная текстовая ветвь
                AND A
                JR NZ, @Station.DrawSystemInfoPanel.HasPlanets                  ; переход, если у выбранного ключа есть планеты, вывести признаки и перечень

                ; вывод исходной фразы Планет нет. в начале первой строки перечня
                LD HL, #6000
                LD (@TextWindow.CursorX), HL
                LD HL, @SystemInfoText.NoPlanets
                CALL @Station.PrintText.Entry
                JP @Station.DrawSystemInfoPanel.DrawCurrent

                ; установка позиции признаков X=25,Y=64 в альтернативном наборе без потери результата характеристики
HasPlanets:     EXX
                LD HL, #4019
                LD (@TextWindow.CursorX), HL
                EXX
                ; сохранение числа планет и F на стеке до трёх строк признаков
                PUSH AF
                CALL @Station.PrintSystemTraits.Entry
                ; перенос сохранённого числа планет в B, флагов характеристики в C
                POP BC
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; выбор первой планеты с порядковым индексом ноль
                LD A, #00
                ; выбор первой колонки первой строки перечня X=0,Y=96
                LD HL, #6000
                LD (@TextWindow.CursorX), HL
                ; сохранение индекса планеты и оставшегося количества вокруг банковой подписи
                PUSH AF
                PUSH BC
                CALL @Map.PrintSelectedVariantLabel.Entry
                POP BC
                POP AF
                ; расчёт следующего индекса планеты и уменьшение количества ещё не напечатанных
                INC A
                DEC B
                JR Z, @Station.DrawSystemInfoPanel.LeaveMapBank                 ; переход, если напечатана последняя планета, вернуть станционный банк

                ; выбор второй колонки первой строки перечня X=32,Y=96
                LD HL, #6020
                LD (@TextWindow.CursorX), HL
                ; сохранение индекса и остатка перед второй подписью
                PUSH AF
                PUSH BC
                CALL @Map.PrintSelectedVariantLabel.Entry
                POP BC
                POP AF
                ; расчёт следующего индекса и остатка после второй подписи
                INC A
                DEC B
                JR Z, @Station.DrawSystemInfoPanel.LeaveMapBank                 ; переход, если после второй подписи планет больше нет, вернуть станционный банк

                ; выбор третьей колонки первой строки перечня X=64,Y=96
                LD HL, #6040
                LD (@TextWindow.CursorX), HL
                ; сохранение индекса и остатка перед третьей подписью
                PUSH AF
                PUSH BC
                CALL @Map.PrintSelectedVariantLabel.Entry
                POP BC
                POP AF
                ; расчёт следующего индекса и остатка после третьей подписи
                INC A
                DEC B
                JR Z, @Station.DrawSystemInfoPanel.LeaveMapBank                 ; переход, если после третьей подписи планет больше нет, вернуть станционный банк

                ; выбор первой колонки второй строки перечня X=0,Y=104
                LD HL, #6800
                LD (@TextWindow.CursorX), HL
                ; сохранение индекса и остатка перед четвёртой подписью
                PUSH AF
                PUSH BC
                CALL @Map.PrintSelectedVariantLabel.Entry
                POP BC
                POP AF
                ; расчёт следующего индекса и остатка после четвёртой подписи
                INC A
                DEC B
                JR Z, @Station.DrawSystemInfoPanel.LeaveMapBank                 ; переход, если после четвёртой подписи планет больше нет, вернуть станционный банк

                ; выбор второй колонки второй строки перечня X=32,Y=104
                LD HL, #6820
                LD (@TextWindow.CursorX), HL
                ; сохранение индекса и остатка перед пятой подписью
                PUSH AF
                PUSH BC
                CALL @Map.PrintSelectedVariantLabel.Entry
                POP BC
                POP AF
                ; расчёт следующего индекса и остатка после пятой подписи
                INC A
                DEC B
                JR Z, @Station.DrawSystemInfoPanel.LeaveMapBank                 ; переход, если после пятой подписи планет больше нет, вернуть станционный банк

                ; выбор шестой и последней колонки X=64,Y=104 без нового сохранения счётчиков
                LD HL, #6840
                LD (@TextWindow.CursorX), HL
                CALL @Map.PrintSelectedVariantLabel.Entry
                ; возврат станционного банка после непустого перечня
LeaveMapBank:   LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; чтение текущего ключа для второго прохода имени и политической области
DrawCurrent:    LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD DE, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                CALL @Map.BuildSystemName.Entry
                ; повторное чтение первого слова после построителя имени текущей системы
                LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                CALL @Map.ClassifyKeyRegion.Entry
                ; сохранение политической области в альтернативном AF вокруг возврата банка
                EX AF, AF'
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; выбор строки текущей политической области X=0,Y=128
                LD HL, #8000
                LD (@TextWindow.CursorX), HL
                LD HL, @SystemInfoText.PoliticalAreas
                EX AF, AF'
                CALL @Station.PrintAfterLF.Entry
                ; выбор строки имени текущей системы X=0,Y=136 и печать переиспользованного Buffer
                LD HL, #8800
                LD (@TextWindow.CursorX), HL
                LD HL, @SystemNameState.Buffer
                CALL @Station.PrintText.Entry
                ; выбор KARTA для подписи текущего варианта X=34,Y=144
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                LD HL, #9022
                LD (@TextWindow.CursorX), HL
                LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD DE, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                LD A, (@SignatureInput.Entry + FSignatureInput.Variant)
                CALL @Map.PrintVariantLabel.Entry
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; получение характеристик текущего пятибайтового ключа
                CALL @Station.DescribeCurrentKey.Entry
                JR Z, @Station.DrawSystemInfoPanel.Return                       ; переход, если количество планет текущего ключа равно нулю, строки признаков не печатать

                ; установка позиции текущих признаков X=25,Y=152 без потери HL и DE характеристики
                EXX
                LD HL, #9819
                LD (@TextWindow.CursorX), HL
                EXX
                ; сохранение AF характеристики и вывод строя, экономики и уровня текущей системы
                PUSH AF
                CALL @Station.PrintSystemTraits.Entry
                ; перенос сохранённых AF характеристики в BC, возврат AF последней печати
                POP BC
Return:         RET

                endmodule
                endmodule
