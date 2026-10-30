                module Map
                module ReadStoredMapVariant
; Документация [Map](../../Docs/FunctionDetails/Map.md)
; Подробный разбор [пятибайтовые записи, пустоты FF и отрицательный ограничитель](../../Docs/StoredMapPoints.md)
; -----------------------------------------
; Поиск выбранного ключа в первом списке и запись пятого байта либо нуля
; исходная запись 7, файловые смещения #040F..#0449
; In:
;   MapSelection.FirstWord и SecondWord задают искомый ключ, первый список начинается по 990A
;   достижим отрицательный первый байт записи, отличный от FF, либо полное совпадение ключа
;   до ограничителя каждая запись имеет пять читаемых байтов, положительный первый байт является частью FirstWord
; Out:
;   A и MapSelection.Variant получают пятый байт первой совпавшей записи, при отсутствии получают 0
;   при совпадении HL=0, DE=MapSelection.FirstWord, BC=5, F=42, IX у начала найденной записи
;   при конце списка DE=MapSelection.SecondWord, BC=5, F=44, IX у начала ограничителя
;   при конце HL остаётся от последнего сравнения, если сравнений не было, сохраняется входной HL
;   нулевой пятый байт найденной записи отличается от отсутствия по F, а не по A
;   все альтернативные регистры, IY, I и IFF сохранены, SP обычного возврата равен входному SP+2
; Corrupt:
;   HL, DE, BC, AF, IX
; Note:
;   первым сравнивается SecondWord, затем FirstWord, при новом внешнем проходе DE перезагружается
;   FF пропускается, 80..FE завершает поиск, первый байт 00..7F считается допустимым младшим байтом ключа
;   новая область памяти не выделяется, исходный IX=9905 с последующим ADD IX,5 даёт первую запись 990A
;   Variant используется как порядковый вариант ключа в SelectVariantResource и характеристике ключа, это не независимые биты
; -----------------------------------------
                ; подготовка указателя перед первой физической записью, шаг добавляется в начале поиска
Entry:          LD IX, @StoredMapPointsA.Point00 - @FStoredMapPoint
                LD BC, @FStoredMapPoint
                ; чтение второго слова искомого ключа перед новым внешним проходом
ReloadSecond:   LD DE, (@MapSelection.SecondWord)
                ; поиск следующей записи размером FStoredMapPoint
NextPoint:      ADD IX, BC
                ; проверка младшего байта FirstWord как маркера пустоты или конца списка
                LD A, (IX + @FStoredMapPoint.FirstWord)
                AND A
                JP M, @Map.ReadStoredMapVariant.TestMarker                      ; переход, если первый байт отрицательный, различить пустоту FF и конец списка

                ; сравнение второго слова физической записи с выбранным SecondWord
                LD L, (IX + @FStoredMapPoint.SecondWord)
                LD H, (IX + @FStoredMapPoint.SecondWord + 1)
                OR A
                SBC HL, DE
                JR NZ, @Map.ReadStoredMapVariant.NextPoint                      ; переход, если вторые слова различаются, проверить следующую запись

                ; сравнение первого слова с сохранённым в A младшим байтом физической записи
                LD L, A
                LD H, (IX + @FStoredMapPoint.FirstWord + 1)
                LD DE, (@MapSelection.FirstWord)
                OR A
                SBC HL, DE
                JR NZ, @Map.ReadStoredMapVariant.ReloadSecond                   ; переход, если первые слова различаются, восстановить SecondWord перед следующей записью

                ; чтение порядкового варианта совпавшей записи
                LD A, (IX + @FStoredMapPoint.Variant)
                JR @Map.ReadStoredMapVariant.StoreVariant

                ; проверка специального маркера пустой записи среди отрицательных байтов
TestMarker:     CP #FF
                JP Z, @Map.ReadStoredMapVariant.NextPoint                       ; переход, если первый байт равен FF, пропустить пустую запись

                ; выбор нулевого значения при достижении отрицательного не-FF ограничителя
                XOR A
                ; сохранение найденного пятого байта либо нуля без изменения различающих флагов
StoreVariant:   LD (@MapSelection.Variant), A
                RET

                endmodule
                endmodule
