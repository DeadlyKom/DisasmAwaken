                module Station
                module PrintSecondaryRows
                ; Документация [второй список, общая печать, выбор и события LANG](../../Docs/SecondaryEquipmentRows.md)
                ; -----------------------------------------
                ; Выбор пяти баз второго списка для общего печатателя
                ; исходная запись 4, перенос STATIONF с 05CE в 6322, адреса 7403..741D
                ; In:
                ;   HL полный начальный индекс, CurrentModels.SkimmerIndex доступен
                ;   договоры общей PrintEquipmentRows, окно, отступы и таблицы подготовлены
                ; Out:
                ;   результаты HL, DE, BC, AF и альтернативных пар по PrintEquipmentRows, но адреса относятся ко второму набору
                ;   тело использует 98F6, 95D4, 9632, 9484 и F066, сохранён исходный общий кадр
                ;   IX, IY, I, IM и IFF сохранены, SP обычного возврата увеличен на два, страница не меняется
                ; Corrupt:
                ;   HL, DE, BC, AF, HL', DE', BC', AF', курсор, bitmap и операнды печати
                ; Note:
                ;   первый CR по F066 выбирает строку топлива, следующий CR выбирает подписи доставки
                ;   у строковых баз нет встроенной проверки индекса, модели больших индексов используют конечный подготовленный текст
                ;   общий вход AtNameStream принимает DE индекс, HL текст и пять уже уложенных слов вместе с внешним возвратом
                ; -----------------------------------------
                ; сохранение полного индекса и выбор базы слов цен
Entry:          EX DE, HL
                LD HL, @SecondEquipmentPrices.Row00.Price
                PUSH HL
                ; чтение типа скимера для отметки отсутствующего типа
                LD A, (@CurrentModels.SkimmerIndex)
                PUSH AF
                ; сохранение четырёхбайтовых наборов допустимых типов
                LD HL, @EquipmentSkimmerTypeSets.Row00.Type0
                PUSH HL
                ; сохранение базы пар порога и веса
                LD HL, @SecondWeightFactors.Row00.Threshold
                PUSH HL
                ; сохранение базы количеств и выбор исходного текста
                LD HL, @SecondaryEquipmentData.Quantities
                PUSH HL
                LD HL, @SecondaryEquipmentData.Names
                JP @Station.PrintEquipmentRows.AtNameStream

                endmodule
                endmodule
