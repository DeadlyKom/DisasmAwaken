                module Final
                module PrepareFrame
; Документация [Final](../../Docs/FunctionDetails/Final.md)
                ; Подробный разбор [контракт обёртки построителя](../../Docs/FinalPrepareFrameContract.md)
; -----------------------------------------
; Подготовка изменяемой цепочки команд финальной анимации
; исходная запись 29, файловые смещения #0196..#01DE
                ; In:
                ;   BC задаёт сохраняемый C, остальные регистры входных аргументов не задают
                ;   исходные инструкции, bitmap- и атрибутный образцы доступны для чтения и записи
                ;   8000..A937 доступны для создания цепочки, нужные исходные bitmap уже скопированы в банки
                ;   SP указывает внешний возврат, двенадцать байтов под SP свободны и не перекрывают код, шаблоны и создаваемую цепочку
                ;   NMI исключён, после первой DI маскируемые прерывания не вмешиваются, выполнены договоры BuildDisplayChain
                ; Out:
                ;   HL=A937, DE=8003, B=0, C сохранён, AF=019B, SP увеличен на два при RET
                ;   область 8000..A937 содержит 10552 байта схемы цепочки, включая восемь нетронутых байтов вставок и два байта будущего операнда SP
                ;   8000..8003 содержат ED 73 35 A9, A934 содержит LD SP,nn, A937 содержит RET
                ;   AfterRow10=912A, AfterRow18=9EE6, операнды образцов имеют конечное состояние BuildDisplayChain
                ;   адрес и длина EmitAttributeRow восстановлены на 627D и 0017, прерывания запрещены
                ;   альтернативные пары, IX, IY, I и IM сохранены, R меняется, портовых операций нет
                ; Corrupt:
                ;   HL, DE, BC только B, AF, R, SP снятием возврата, IFF, цепочка вне десяти оставленных байтов, операнды, указатели и двенадцать байтов под входным SP
                ; Note:
                ;   ED 73 35 A9 при исполнении цепочки сохраняет её входной SP в A935..A936, стек вызова PrepareFrame туда не записывается
                ;   будущий операнд восстановления SP сохраняет прежние два байта памяти, до вызова цепочки они не инициализируются
                ;   восемь байтов вставок заполняет основной цикл перед исполнением, этот построитель их не пишет
                ;   собственная рамка хранит слово 8002 и возврат 61D0, BuildDisplayChain добавляет ещё восемь байтов глубины
                ;   512 сценариев проверяют все C и два положения CPU-стека, подготовку, результат дочернего построителя и четыре завершающие записи
                ;   дочерняя геометрия проверена отдельным эталоном, R/T, IRQ, перекрытия и исполнение цепочки этой проверкой не подтверждаются
; -----------------------------------------
                ; создание исполняемой цепочки поверх уже скопированных исходных bitmap
Entry:          DI
                LD HL, #C000
                LD (@FinalTemplates.BitmapLine.Entry + 1), HL
                LD HL, #4010
                LD (@FinalTemplates.BitmapLine.WriteFirstHalf + 1), HL
                LD HL, #C010
                LD (@FinalTemplates.BitmapLine.ReadSecondHalf + 1), HL
                LD HL, #4020
                LD (@FinalTemplates.BitmapLine.WriteLastHalf + 1), HL
                LD HL, #5820
                LD (@FinalTemplates.AttributeRow.AttrStack + 1), HL
                LD HL, @FinalTemplates.AttributeRow.Entry
                LD (@Final.EmitAttributeRow.Entry + 1), HL
                LD HL, #0017
                LD (@Final.EmitAttributeRow.TemplateSize + 1), HL
                ; Запись заголовка исполняемой цепочки по адресу будущего входа.
                LD HL, @FinalDisplayChainConst.GeneratedEntry
                LD (HL), #ED
                INC HL
                LD (HL), #73
                INC HL
                PUSH HL
                INC HL
                INC HL
                CALL @Final.BuildDisplayChain.Entry
                EX DE, HL
                LD (HL), #31
                INC HL
                EX DE, HL
                POP HL
                LD (HL), E
                INC HL
                LD (HL), D
                EX DE, HL
                INC HL
                INC HL
                LD (HL), #C9
                RET


                endmodule
                endmodule
