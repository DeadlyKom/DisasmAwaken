                module Map
                module SelectVariantResource
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [приоритет категорий, второй список и количество от одного до шести](../../Docs/VariantResources.md)
; -----------------------------------------
; Выбор ресурса текущего, выбранного, сохранённого либо прочего варианта
; исходная запись 7, файловые смещения #07B4..#0826
; In:
;   BC - B остаток количества, C сохраняемый контекст, порядковый вариант равен (MapVariantState.Count-B) modulo 256
;   два слова MapSelection и SignatureInput доступны, байты 9848 и 9843 задают выбранный и текущий варианты
;   второй список StoredMapPointsB содержит достижимый первый отрицательный байт либо полное совпадение
;   банк KARTA выбран, изменяемый операнд MapVariantState.Wanted доступен для записи
; Out:
;   HL у одного из четырёх исходных ресурсов, их внутренний формат этой процедурой не читается
;   при совпавшем текущем ключе и текущем варианте HL=MapVariantResources.Current
;   иначе при совпавшем выбранном варианте HL=MapVariantResources.Selected
;   иначе при совпавшей пятибайтовой записи второго списка HL=MapVariantResources.Stored, при конце HL=MapVariantResources.Default
;   BC сохранён, IY и все альтернативные пары сохранены
;   на ранних текущем или выбранном результатах IX сохранён, DE содержит последнее сравниваемое слово текущего ключа
;   на совпадении в списке IX у записи, DE=MapSelection.FirstWord, A искомый вариант, F от успешного CP пятого байта
;   при конце списка IX у отрицательного маркера, DE=MapSelection.SecondWord, A равен маркеру, F от OR A
;   при поиске MapVariantState.Wanted получает искомый вариант, на ранних результатах этот операнд не меняется
;   AF ранних результатов содержит искомый вариант и флаги CP текущего либо выбранного байта с вариантом
;   I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, AF, IX только на ветви поиска
; Note:
;   текущий ресурс имеет приоритет над выбранным, выбранный над сохранённым, все проверки выполняются в исходном порядке
;   второй список здесь сканируется до любого отрицательного байта, FF не пропускается в отличие от FindSecondaryMapPoint
;   код читает пять полей записи, но никакие дополнительные значения отрицательных маркеров не интерпретирует
;   Count и Wanted находятся внутри операндов двух LD A, новый буфер не создаётся
; -----------------------------------------
                ; расчёт порядкового варианта как Count-B с байтовым оборачиванием
Entry:          LD L, B
                LD A, #00
                SUB L
                ; сравнение вторых слов выбранного и текущего ключей
                LD HL, (@MapSelection.SecondWord)
                LD DE, (@SignatureInput.Entry.SecondWord)
                OR A
                SBC HL, DE
                JR NZ, @Map.SelectVariantResource.TestSelected                  ; переход, если вторые слова ключей различаются, проверить выбранный вариант

                ; сравнение первых слов при совпавших вторых
                LD HL, (@MapSelection.FirstWord)
                LD DE, (@SignatureInput.Entry.FirstWord)
                OR A
                SBC HL, DE
                JR NZ, @Map.SelectVariantResource.TestSelected                  ; переход, если первые слова ключей различаются, проверить выбранный вариант

                ; сравнение текущего порядкового варианта при совпавшем ключе
                LD L, A
                LD A, (@SignatureInput.Entry.Variant)
                CP L
                LD A, L
                JR NZ, @Map.SelectVariantResource.TestSelected                  ; переход, если текущий вариант отличается от искомого, проверить выбранный

                ; выбор ресурса текущего варианта с высшим приоритетом
                LD HL, @MapVariantResources.Current
                RET

                ; проверка выбранного варианта после отказа категории текущего
TestSelected:   LD L, A
                LD A, (@MapSelection.Variant)
                CP L
                LD A, L
                LD HL, @MapVariantResources.Selected
                RET Z                                                           ; выход, если выбранный вариант равен искомому, HL у выбранного ресурса

                ; сохранение искомого варианта в операнде сравнения второго списка
                LD (@MapVariantState.Wanted), A
                ; сохранение остатка количества и C вокруг поиска пятибайтовых записей
                PUSH BC
                ; подготовка указателя перед первой записью второго списка и физического шага 5
                LD IX, @StoredMapPointsB.Point00 - @FStoredMapPoint
                LD BC, @FStoredMapPoint
                ; чтение второго слова выбранного ключа перед внешним проходом
ReloadSecond:   LD DE, (@MapSelection.SecondWord)
                ; поиск следующей записи второго списка
NextStored:     ADD IX, BC
                ; проверка первого отрицательного байта, в этом поиске FF тоже завершает список
                LD A, (IX + @FStoredMapPoint.FirstWord)
                OR A
                JP M, @Map.SelectVariantResource.UseDefault                     ; переход, если первый байт отрицательный, выбрать обычный ресурс без пропуска FF

                ; сравнение второго слова записи с выбранным ключом
                LD L, (IX + @FStoredMapPoint.SecondWord)
                LD H, (IX + @FStoredMapPoint.SecondWord + 1)
                OR A
                SBC HL, DE
                JR NZ, @Map.SelectVariantResource.NextStored                    ; переход, если вторые слова различаются, проверить следующую запись

                ; сравнение первого слова записи после совпадения второго
                LD L, A
                LD H, (IX + @FStoredMapPoint.FirstWord + 1)
                LD DE, (@MapSelection.FirstWord)
                OR A
                SBC HL, DE
                JR NZ, @Map.SelectVariantResource.ReloadSecond                  ; переход, если первые слова различаются, восстановить SecondWord и продолжить поиск

                ; чтение сохранённого искомого варианта и сравнение с пятым байтом записи
                LD A, #00
                CP (IX + @FStoredMapPoint.Variant)
                JR NZ, @Map.SelectVariantResource.ReloadSecond                  ; переход, если порядковый вариант записи отличается от искомого, продолжить поиск

                ; выбор ресурса варианта, найденного во втором списке
                LD HL, @MapVariantResources.Stored
                POP BC
                RET

                ; выбор обычного ресурса при первом отрицательном байте второго списка
UseDefault:     LD HL, @MapVariantResources.Default
                POP BC
                RET

                endmodule
                endmodule
