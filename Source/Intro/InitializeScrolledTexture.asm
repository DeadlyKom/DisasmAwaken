                module Intro
                module InitializeScrolledTexture
                ; Документация [прокручиваемая текстура](../../Docs/IntroScrolledFrame.md)
; Документация [Intro](../../Docs/FunctionDetails/Intro.md)
; -----------------------------------------
; Создание 64 развёрнутых выборок по шаблону #6722, подготовка текстуры и экранной раскладки
; исходная запись 3, файловые смещения #03FB..#0421
                ; In:
                ;   банк 4 содержит 64 строки текстуры по 64 байта, память кода, таблиц и назначения доступна
                ;   IM 1 и IFF разрешены, действуют условия PresentAttributes для ПЗУ и клавиатуры
                ;   CPU-стек и рамка IRQ лежат вне разворачиваемой текстуры и генерируемых цепочек
                ; Out:
                ;   подготовлены цепочка 7E00, писатель 68A9, развёрнутая текстура и таблицы атрибутов
                ;   HL содержит последнее слово выбранной матрицы, DE=#6100, BC=#699B, AF содержит фазу и флаги OR
                ;   HL'=#6929, DE'=#8888, BC'=0, AF' сохранён, IX=0, IYL получает младшую тетраду байта #69A2
                ;   выбрана страница #11, SP после RET равен входному SP+2
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', IX, IYL, R, генерируемые цепочки, таблицы, экранный буфер, стек и 7FFD
                ; Note:
                ;   24 композиционных сценария с настоящим ROM сверили вывод, регистры кроме R и два переключения
                ;   HALT требует IRQ, нативный запуск, прочие ROM и произвольная периодика не проверены
; -----------------------------------------
Entry:          LD DE, #7E00
                LD HL, #6722
                LD BC, #4007
                CALL @Intro.RepeatPattern.Entry
                LD DE, @Intro.NextSampledRow.Entry
                CALL @Intro.WriteJump.Entry
                LD IXL, #80
                CALL @Intro.ExpandTextureRows.Entry
                LD IXL, #80
                LD DE, #80C0
                LD BC, #0100
                CALL @Intro.BuildAttributeWriter.Entry
                JP @Intro.PresentAttributes.Entry


                endmodule
                endmodule
