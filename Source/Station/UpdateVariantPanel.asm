                module Station
                module UpdateVariantPanel
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [установка callback, тактовая маска, геометрия указателя и два банковых контекста](../../Docs/PeriodicVariants.md)
; -----------------------------------------
; Периодическая очистка и банковая анимация панели с отдельной ветвью отложенного обновления
; исходная запись 4, файловые смещения #1B82..#1BF3
; In:
;   VariantPanelState.RefreshPending и CadenceMask являются доступными изменяемыми операндами
;   банк станции 0 выбран, при ненулевом RefreshPending действуют условия RefreshVariantPanel
;   для обычного рисунка последний обработчик списка равен DrawVariantPanel.Entry, ItemIndex задаёт его доступную запись
;   TextWindow ещё соответствует последнему SetupInsetTextWindow этой панели, действуют договоры FillWindowBody и DrawVariantCluster
;   геометрия панели и начала вариантов допускает их фактические записи, указатель имеет допустимые координаты и владельца
;   во время заимствованного SP заливки прерывания запрещены либо обслуживаются доказанным станционным ISR, paging доступен
; Out:
;   при ненулевом RefreshPending исполнение передано в RefreshVariantPanel без поворота CadenceMask
;   иначе маска циклически повёрнута вправо и сохранена, при старом бите 0, равном нулю, экран не меняется, HL, DE, BC сохранены, A содержит повёрнутый байт
;   у этого раннего выхода S=0,Z=1,PV=1 от OR нулевого RefreshPending, биты 5,3 от повёрнутой маски, H,N,C сброшены
;   при старом бите 0, равном единице, проверен последний обработчик, несовпадение возвращает HL=LastDraw-DrawVariantPanel.Entry, DE=адрес панели, BC сохранён, A старший LastDraw и F от SBC
;   для допущенного рисунка получены количество и геометрия, ResumeRequired равен попаданию символьной позиции указателя в [X-1,X+Width) и [Y-1,Y+Height)
;   в зоне указателя фон восстановлен до рисунка, тело залито, в KARTA выполнен DrawVariantCluster, затем восстановлен банк станции 0 и при необходимости возобновлён указатель
;   на обычном рисующем выходе HL, DE, BC соответствуют последнему шагу C677, основной AF=0100 при ResumeRequired=1 либо 0044 при нуле
;   обычный путь сохраняет IX, IY, HL', DE', BC', I и IFF инструкциями, AF' рабочий, отложенная ветвь может изменить IX
;   два временных слова FVariantUpdateFrame сняты до вызова C677, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, AF', IX только на отложенной ветви, bitmap, операнды панели и достигнутые курсоры KARTA
; Note:
;   начальная маска 80 даёт рисунок на каждом восьмом повороте, нулевой байт не создаёт ни одного такта
;   маска является циклической временной последовательностью, её биты не объявлены независимыми флагами
;   соседняя символьная ячейка слева и сверху включена отдельными переходами при нулевой разности, обычное строгое сравнение прямоугольника неэквивалентно
;   нулевое количество не отменяет заливку и вызов C677, его собственная центральная метка и движение первого курсора сохраняются
;   нормальный bitmap проверен независимой композицией, отложенный путь проверен интеграцией настоящих помощников и отдельным сравнением теневого снимка, эти свидетельства различаются
; -----------------------------------------
                ; проверка полного байта запроса отложенного обновления
Entry:          LD A, #00
                OR A
                JR NZ, @Station.RefreshVariantPanel.Entry                       ; переход, если RefreshPending ненулевой, перейти к отложенной перерисовке без поворота маски

                ; чтение и поворот временной маски, старый бит 0 определяет разрешение текущего такта
                LD A, #80
                RRCA
                ; сохранение повёрнутой маски в исходном операнде
                LD (@VariantPanelState.CadenceMask), A
                RET NC                                                          ; выход, если старый бит 0 маски равен нулю, этот такт не рисует

                ; поиск последнего указателя в текущем списке рисования
                CALL @Station.GetLastDraw.Entry
                LD DE, @Station.DrawVariantPanel.Entry
                ; проверка последнего обработчика на совпадение с панелью, OR очищает Carry перед SBC
                OR A
                SBC HL, DE
                RET NZ                                                          ; выход, если последним рисовался другой обработчик, тело панели не менять

                ; получение количества из выбранного ключа до очистки тела
                CALL @Station.GetSelectedVariantCount.Entry
                ; сохранение количества и точных флагов в FVariantUpdateFrame.SavedCountAF
                PUSH AF
                ; получение адреса геометрии панели по её изменяемому индексу и полю X
                XOR A
                LD HL, (@VariantPanelState.ItemIndex)
                CALL @Station.GetItemField.Entry
                ; чтение X,Y,Width,Height в E,D,C,B без изменения записи
                LD E, (HL)
                INC HL
                LD D, (HL)
                INC HL
                LD C, (HL)
                INC HL
                LD B, (HL)
                ; перевод пиксельной позиции указателя в символьные X,Y тремя независимыми сдвигами
                LD HL, (@StationState.PointerXY)
                SRL H
                SRL L
                SRL H
                SRL L
                SRL H
                SRL L
                ; расчёт tileX+1-X с отдельным допуском соседней левой ячейки
                LD A, L
                INC A
                SUB E
                JR C, @Station.UpdateVariantPanel.NoPointerHold                 ; переход, если tileX+1 меньше X, указатель не требует приостановки

                JR Z, @Station.UpdateVariantPanel.CheckPointerY                 ; переход, если tileX=X-1, левая соседняя ячейка допускается к проверке Y

                ; расчёт tileX-X и проверка исключённой правой границы Width
                DEC A
                CP C
                JR NC, @Station.UpdateVariantPanel.NoPointerHold                ; переход, если tileX-X не меньше Width, указатель вне правой границы

                ; расчёт tileY+1-Y с отдельным допуском соседней верхней ячейки
CheckPointerY:  LD A, H
                INC A
                SUB D
                JR C, @Station.UpdateVariantPanel.NoPointerHold                 ; переход, если tileY+1 меньше Y, указатель не требует приостановки

                JR Z, @Station.UpdateVariantPanel.HoldPointer                   ; переход, если tileY=Y-1, верхняя соседняя ячейка требует приостановки

                ; расчёт tileY-Y и проверка исключённой нижней границы Height
                DEC A
                CP B
                JR NC, @Station.UpdateVariantPanel.NoPointerHold                ; переход, если tileY-Y не меньше Height, указатель вне нижней границы

                ; восстановление фона указателя в расширенной зоне перед заливкой
HoldPointer:    CALL @Station.SuspendPointer.Entry
                ; установка полного кода ResumeRequired=1 для последующего возобновления
                LD A, #01
                JR @Station.UpdateVariantPanel.SavePointerHold

                ; сброс ResumeRequired при указателе вне расширенной зоны
NoPointerHold:  XOR A
                ; сохранение решения о возобновлении в операнде завершающего LD A
SavePointerHold:LD (@VariantPanelState.ResumeRequired), A
                ; сохранение исходных X,Y панели в FVariantUpdateFrame.SavedOriginXY на время заливки
                PUSH DE
                ; заливка внутреннего тела исходным помощником с временным использованием SP
                CALL @Station.FillWindowBody.Entry
                ; восстановление символьного начала в DE перед банковым рисунком
                POP DE
                ; выбор KARTA через общий интерфейс paging, текущий бит показа экрана сохраняется
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; восстановление количества и флагов, ранее помещённых в SavedCountAF
                POP AF
                ; рисование центральной метки и достигнутых вариантов исходным C677 банка 1
                CALL @Map.DrawVariantCluster.Entry
                ; возврат банка станции до доступа к обычным обработчикам указателя
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; чтение сохранённого решения ResumeRequired и проверка полного байта
                LD A, #00
                OR A
                CALL NZ, @Station.ResumePointer.Entry                           ; вызов, если ResumeRequired ненулевой, снова нарисовать и разрешить указатель
                RET

                endmodule
                endmodule
