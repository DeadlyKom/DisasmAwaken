                module Station
                module DrawItem32
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [выдача награды внутри рисователя и ограничение рекурсивной перерисовки](../../Docs/MissionCompletion.md)
; -----------------------------------------
; Вывод условий миссии и однократное завершение с наградой при достижении цели
; исходная запись 4, файловые смещения #4A85..#4B65
; In:
;   DrawItemState.Opcode32 равен 21 для исполнения либо C9 для отключения, Index32 содержит индекс FInterfaceItem
;   действует договор DrawCaptionItem с видимой геометрией, готовыми таблицами и свободной индексной парой
;   загружены исходные KARTA в банк 1 и LANG в банк 6, станционный код в банке 0
;   MissionOffer, SignatureInput, MissionState и денежное слово 984E доступны для чтения и записи
;   при завершении дополнительно действуют договоры DrawItem00, GenerateMissionOffer, DrawItem31 и ScreenUpdate
;   генератор должен достигать ROM-байта с ненулевым тоннажем, пробуждение HALT сохраняет контекст
;   стек вне экранов и банкового окна, прерывания не нарушают страницу и промежуточное состояние
; Out:
;   при активном коде регистрирует рамку, выводит требование и награду, затем выбирает ветвь по целому ActiveCode
;   при ActiveCode не равном 1 выполняет хвостовой PrintText приглашения, его HL, DE и AF являются результатом
;   при ActiveCode=1 строит имя предлагаемого пункта и проверяет оба слова текущего ключа
;   при различии ключа, CompletionCode=1 или количестве 9852 меньше требования выполняет хвостовой PrintText напоминания
;   при завершении прибавляет Reward к слову 984E, только при переносе за FFFF заменяет сумму на FDE8
;   уменьшает байт 9852 на прежнее требование, исполняет исходный LANG с событием 11 и дважды пересчитывает 9850
;   перерисовывает статус, генерирует новое предложение, печатает сообщение успеха, пишет CompletionCode=1 и ActiveCode=0
;   после этого один раз вызывает себя внутри обновления экрана, повторный вход не начисляет награду
;   перед конечным EndScreenUpdate HL, DE, BC и AF соответствуют последнему DrawItem00, EndScreenUpdate меняет только A на 10
;   IY, I и IFF сохранены при договоре пробуждения, SP обычного возврата равен входному SP+2
;   IX сохраняется без завершения, при завершении содержит позицию после команды FinishScript исходного LANG
;   без активной миссии HL', DE', BC' сохранены, AF' по DrawCaptionItem
;   активная миссия изменяет HL', DE', BC' через BuildSystemName, при завершении также через LANG и генератор
;   окончательные альтернативные пары на завершении задаются вложенным DrawItem31 и AF' последующими рисователями
;   возврат после завершения выбирает страницу 10 и снимает блокировку указателя, без завершения старшие биты страницы сохраняются
;   при Opcode32=C9 только RET, всё тело и его побочные эффекты пропущены
; Corrupt:
;   HL, DE, BC, AF, HL', DE', BC', AF', IX только при завершении
; Note:
;   это игровая операция внутри рисователя, повторный вызов может завершать миссию при изменившихся условиях
;   Carry перед ADC очищен успешным CP количества, перенос от сравнения ключа туда не доходит
;   FDE8 применяется только при переполнении, суммы FDE9..FFFF без переноса сохраняются
;   CompletionCode и ActiveCode сравниваются как коды 1, назначение прочих значений не приписывается отдельным битам
;   требование 0 допустимо для данного кода, генератор штатно создаёт 1..31, байты алгоритма не исправлены
;   проверка модели включает настоящий сценарий и все вложенные процедуры, HALT пробуждается фикстурой без IRQ
;   ROM модели не сверена с Unreal, сборка и нативное прохождение этим разбором не подтверждены
; -----------------------------------------
                ; чтение изменяемого индекса элемента условий миссии, RET в первом байте отключает всю операцию
Entry:          LD HL, #0000
                ; регистрация прямоугольника, рисование рамки и заголовка
                CALL @Station.DrawCaptionItem.Entry
                ; вывод пояснения перед требуемым количеством свободного тоннажа
                LD HL, @MissionTexts.TonnageCaption
                CALL @Station.PrintText.Entry
                ; печать байтового требования через четырёхразрядное числовое ядро
                LD A, (@MissionOffer.Entry.RequiredTonnage)
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
                ; вывод подписи награды, исходного денежного слова и суффикса
                LD HL, @MissionTexts.RewardCaption
                CALL @Station.PrintText.Entry
                LD BC, (@MissionOffer.Entry.Reward)
                CALL @Station.PrintWord.Entry
                LD HL, @MissionTexts.CurrencySuffix
                CALL @Station.PrintText.Entry
                ; проверка кода активной миссии после общей части условий
                LD A, (@MissionState.ActiveCode)
                CP #01
                JP Z, @Station.DrawItem32.ActiveMission                         ; переход, если ActiveCode равен 1, показать цель и проверить завершение

                ; выбор приглашения к заключению миссии при любом другом коде состояния
                LD HL, @MissionTexts.Invitation
                JP @Station.PrintText.Entry

                ; чтение упакованного ключа цели и выбор KARTA для построения имени
ActiveMission:  LD HL, (@MissionOffer.Entry.FirstWord)
                LD DE, (@MissionOffer.Entry.SecondWord)
                LD A, #11
                CALL @Station.SelectRamBank.Entry
                ; построение имени с обменом основных наборов регистров по BuildSystemName
                CALL @Map.BuildSystemName.Entry
                ; возврат банка станции для печати подписи цели и общего буфера имени
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                LD HL, @MissionTexts.TargetCaption
                CALL @Station.PrintText.Entry
                LD HL, @SystemNameState.Buffer
                CALL @Station.PrintText.Entry
                ; сравнение первого слова текущего пункта с первым словом цели
                LD HL, (@SignatureInput.Entry.FirstWord)
                LD DE, (@MissionOffer.Entry.FirstWord)
                XOR A
                SBC HL, DE
                JP NZ, @Station.DrawItem32.PrintReminder                        ; переход, если первые слова различаются, вывести напоминание без награды

                ; сравнение второго слова текущего пункта с вторым словом цели
                LD HL, (@SignatureInput.Entry.SecondWord)
                LD DE, (@MissionOffer.Entry.SecondWord)
                XOR A
                SBC HL, DE
                JP NZ, @Station.DrawItem32.PrintReminder                        ; переход, если вторые слова различаются, вывести напоминание без награды

                ; проверка защиты от повторного завершения в текущем состоянии
                LD A, (@MissionState.CompletionCode)
                CP #01
                JP Z, @Station.DrawItem32.PrintReminder                         ; переход, если CompletionCode равен 1, вывести напоминание без повторной награды

                ; проверка количества по 9852 против байта требования, старший байт загруженного слова здесь не сравнивается
                LD HL, (@MissionOffer.Entry.RequiredTonnage)
                LD A, (#9852)
                CP L
                JP C, @Station.DrawItem32.PrintReminder                         ; переход, если количества меньше требования, вывести напоминание без награды

                ; расчёт денежной суммы, успешный CP количества оставил Carry равным нулю
                LD HL, (#984E)
                LD DE, (@MissionOffer.Entry.Reward)
                ADC HL, DE
                JP C, @Station.DrawItem32.RewardOverflow                        ; переход, если сумма денег и награды превысила FFFF, заменить её на 65000

                LD (#984E), HL
                ; вычитание прежнего требования из количества до генерации нового предложения
RemoveLoad:     LD A, (#9852)
                LD HL, @MissionOffer.Entry.RequiredTonnage
                SUB (HL)
                LD (#9852), A
                ; выбор полного байта страницы LANG и события 11 для двух пересчётов тоннажа
                LD A, #16
                CALL @Station.SelectMemoryPage.Entry
                LD A, #11
                LD (@ScriptCallState.EventCode), A
                CALL @Text.RunMarketScript.Entry
                ; возврат станции, обновление статуса и замена предложения настоящим генератором
                LD A, #10
                CALL @Station.SelectRamBank.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.GenerateMissionOffer.Entry
                ; вывод исходного сообщения о полученной награде
                LD HL, @MissionTexts.Success
                CALL @Station.PrintText.Entry
                ; установка защиты завершения и снятие активности перед вложенной перерисовкой
                LD A, #01
                LD (@MissionState.CompletionCode), A
                XOR A
                LD (@MissionState.ActiveCode), A
                ; обновление цели, условий и статуса под снимком экрана, вложенный DrawItem32 уже видит ActiveCode=0
                CALL @Station.BeginScreenUpdate.Entry
                CALL @Station.DrawItem31.Entry
                CALL @Station.DrawItem32.Entry
                CALL @Station.DrawItem00.Entry
                CALL @Station.EndScreenUpdate.Entry
                RET

                ; замена только переполнившейся денежной суммы исходным числом 65000
RewardOverflow: LD HL, #FDE8
                LD (#984E), HL
                JP @Station.DrawItem32.RemoveLoad

                ; выбор исходного напоминания при невыполненных условиях завершения
PrintReminder:  LD HL, @MissionTexts.Reminder
                JP @Station.PrintText.Entry

                endmodule
                endmodule
