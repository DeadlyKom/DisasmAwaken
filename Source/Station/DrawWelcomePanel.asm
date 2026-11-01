                module Station
                module DrawWelcomePanel
                ; Документация [четыре части шаблона, три возврата по коду 01, текущий ключ и почасовая ставка](../../Docs/WelcomePanel.md)
                ; -----------------------------------------
                ; Вывод приветствия станции, её модели, имени системы и почасовой ставки 5×L
                ; исходная запись 4, файловые смещения #1C01..#1C68
                ; In:
                ;   Entry содержит активный LD HL с подготовленным WelcomePanelState.ItemIndex, штатно 45, либо временный C9
                ;   при активном коде банк станции 0 выбран, действует договор DrawCaptionItem с готовыми таблицами и шрифтом
                ;   SignatureInput.Entry содержит пятибайтовый текущий ключ, KARTA доступна в банке 1, реальные переключения банка разрешены
                ;   WelcomeText.ModelLabels и Template доступны, действуют договоры поиска LF, PrintText, Print4DigitCore, BuildSystemName и PrintVariantLabel
                ;   указатель защищён, HALT рамки получает корректное пробуждение с сохранением контекста, стек вне экранов и банкового окна
                ; Out:
                ;   при активном коде зарегистрированы рамка и заголовок, Style=1, последовательно выведены части приветствия и вставки
                ;   L характеристики текущего ключа выбирает одну из 16 подписей модели станции, ставка равна 5×L, диапазон 5..80
                ;   HL содержит продолжение последнего PrintText, DE содержит код области в D и младший двухбитовый признак характеристики в E
                ;   BC соответствует последнему Print4DigitCore, AF статусу последнего PrintText, при полном тексте HL=CE19, BC=10, AF=0A4A
                ;   HL'=FirstWord AND F0FF, DE'=SecondWord AND FFF0, BC'=входной BC, AF' содержит восстановленную страницу и флаги её OR
                ;   IX, IY, I, IFF и IM сохранены при договоре пробуждения, SP обычного возврата равен входному+2
                ;   SystemNameState.Buffer содержит имя текущей системы, рабочий ключ после второго DescribeCurrentKey соответствует текущему ключу
                ;   итоговая страница равна входной для 10 и 18, прежний произвольный номер банка не восстанавливается
                ;   при временном C9 весь контекст, память и страницы сохранены, тело рисователя не исполняется
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', bitmap, окно, курсор, Buffer, рабочий ключ и порт страницы при активном коде
                ; Note:
                ;   L имеет числовой диапазон 1..16, здесь текст доказывает его использование как номера модели орбитальной станции
                ;   три разделителя 01 возвращают управление PrintText для вставок, только последняя часть шаблона заканчивается LF
                ;   после отказа вывода HL может остаться внутри фразы, последующие POP HL продолжают именно от этого адреса без отката
                ;   арифметика двух ADD A,A и ADD A,L даёт 5×L без переполнения, запись денег или списание платы здесь отсутствуют
                ;   независимый oracle всего bitmap не заявлен, проверены исходные помощники, аргументы, регистры и IM2 только у HALT рамки
                ; -----------------------------------------
                ; чтение изменяемого индекса приветственного окна для рамки и заголовка
Entry:          LD HL, #0000
                CALL @Station.DrawCaptionItem.Entry
                ; обновление режима текста, приветствие использует автоматический перенос
                LD A, #01
                LD (@TextWindow.Style), A
                ; чтение первой части шаблона до разделителя вставки 01
                LD HL, @WelcomeText.Template
                CALL @Station.PrintText.Entry
                ; создание FWelcomeTextFrame.Continuation, в том числе после отказа печати
                PUSH HL
                ; расчёт характеристики текущей системы для выбора модели станции
                CALL @Station.DescribeCurrentKey.Entry
                ; расчёт нулевого индекса подписи модели из диапазона L=1..16
                LD A, L
                DEC A
                ; поиск и печать модели станции по исходным LF-записям
                LD HL, @WelcomeText.ModelLabels
                CALL @Station.PrintAfterLF.Entry
                ; восстановление продолжения шаблона после вставки модели
                POP HL
                CALL @Station.PrintText.Entry
                PUSH HL
                ; чтение двух физических слов текущего ключа для имени системы
                LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD DE, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                ; выбор банка KARTA для формирования имени и подписи варианта
                LD A, @SystemNameConst.MapPage
                CALL @Station.SelectRamBank.Entry
                ; создание имени текущей системы в переиспользуемом буфере bootstrap
                CALL @Map.BuildSystemName.Entry
                ; чтение сформированного имени для настоящей печати
                LD HL, @SystemNameState.Buffer
                CALL @Station.PrintText.Entry
                ; расчёт четырёхпиксельного промежутка перед подписью варианта
                LD A, (@TextWindow.CursorX)
                ADD A, #04
                LD (@TextWindow.CursorX), A
                ; чтение текущего ключа и его варианта для подписи после имени
                LD HL, (@SignatureInput.Entry + FSignatureInput.FirstWord)
                LD DE, (@SignatureInput.Entry + FSignatureInput.SecondWord)
                LD A, (@SignatureInput.Entry + FSignatureInput.Variant)
                CALL @Map.PrintVariantLabel.Entry
                ; возврат банка станции перед продолжением приветственного шаблона
                LD A, @StationIrqConst.StationPage
                CALL @Station.SelectRamBank.Entry
                ; восстановление части приветствия перед почасовой ставкой
                POP HL
                CALL @Station.PrintText.Entry
                ; создание FWelcomeTextFrame.Continuation перед вставкой числовой ставки
                PUSH HL
                ; повторный расчёт характеристики текущего ключа, подпись варианта меняла рабочий ключ
                CALL @Station.DescribeCurrentKey.Entry
                ; расчёт ставки 5×L двумя удвоениями и прибавлением исходного L
                LD A, L
                ADD A, A
                ADD A, A
                ADD A, L
                ; подготовка беззнаковой ставки 5..80 для числового печатателя
                LD C, A
                LD B, #00
                CALL @Station.Print4DigitCore.Entry
                ; восстановление заключительной части приветствия после вставки ставки
                POP HL
                CALL @Station.PrintText.Entry
                RET

                endmodule
                endmodule
