                module Action
                module ClassifyCoordinateRegion
                ; Документация [алгоритм и проверка](../../Docs/ActionRegionType.md)
                ; -----------------------------------------
                ; Классификация пары H,L по трём непересекающимся прямоугольникам с кодом 3 вне них
                ; исходная запись 17, перенесённое ядро 6000..7F8E, смещения #1068..#10A8
                ; In:
                ;   HL задаёт независимые байтовые координаты H и L, DE и BC сохраняются, входной AF не влияет на результат
                ;   ядро ACTION перенесено из файлового смещения 023D в RAM 6000, на CPU-стеке внешний возврат, IRQ не вмешиваются
                ; Out:
                ;   HL, DE и BC сохраняются, A содержит числовой код области 0, 1, 2 или 3
                ;   код 0 при 4A<=H<4E и 36<=L<3A, код 1 при 47<=H<4A и 34<=L<38
                ;   код 2 при 47<=H<4A и 38<=L<3B, во всех остальных случаях код 3
                ;   F соответствует последнему CP выбранного пути, загрузка кода в A флаги не меняет, Z не проверяет возвращаемый код
                ;   HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2
                ;   R получает от 10 до 32 M1 по выбранным границам, точные варианты описаны в документации
                ; Corrupt:
                ;   AF, R
                ; Note:
                ;   области не пересекаются, сравнения беззнаковые, верхние границы исключены
                ;   код является числовым результатом, независимые флаговые биты ему не приписываются
                ;   RAM, порты и код не записываются, дополнительная рамка CPU-стека не создаётся
                ;   игровой смысл областей ещё не установлен, потребитель BuildSeededIndices описан отдельно
                ; -----------------------------------------
                ; проверка нижней границы H первой области
Entry:          LD A, H
                CP @ActionRegionTypeConst.HMiddle
                JR C, @Action.ClassifyCoordinateRegion.CheckSecond              ; переход, если H меньше HMiddle, проверить вторую область

                ; проверка исключённой верхней границы H первой области
                CP @ActionRegionTypeConst.HUpper
                JR NC, @Action.ClassifyCoordinateRegion.CheckSecond             ; переход, если H не меньше HUpper, проверить вторую область

                ; проверка нижней границы L первой области
                LD A, L
                CP @ActionRegionTypeConst.LInset
                JR C, @Action.ClassifyCoordinateRegion.CheckSecond              ; переход, если L меньше LInset, проверить вторую область

                ; проверка исключённой верхней границы L первой области, код загружается без изменения F
                CP @ActionRegionTypeConst.LInsetEnd
                LD A, @ActionRegionTypeConst.Code0
                RET C                                                           ; выход, если L меньше LInsetEnd при уже проверенных остальных границах, вернуть Code0

                ; проверка нижней границы H второй области
CheckSecond:    LD A, H
                CP @ActionRegionTypeConst.HLower
                JR C, @Action.ClassifyCoordinateRegion.CheckThird               ; переход, если H меньше HLower, проверить третью область

                ; проверка исключённой верхней границы H второй области
                CP @ActionRegionTypeConst.HMiddle
                JR NC, @Action.ClassifyCoordinateRegion.CheckThird              ; переход, если H не меньше HMiddle, проверить третью область

                ; проверка нижней границы L второй области
                LD A, L
                CP @ActionRegionTypeConst.LLower
                JR C, @Action.ClassifyCoordinateRegion.CheckThird               ; переход, если L меньше LLower, проверить третью область

                ; проверка исключённой верхней границы L второй области
                CP @ActionRegionTypeConst.LMiddle
                LD A, @ActionRegionTypeConst.Code1
                RET C                                                           ; выход, если L меньше LMiddle при уже проверенных остальных границах, вернуть Code1

                ; проверка нижней границы H третьей области, вне неё возвращается OutsideCode
CheckThird:     LD A, H
                CP @ActionRegionTypeConst.HLower
                LD A, @ActionRegionTypeConst.OutsideCode
                RET C                                                           ; выход, если H меньше HLower, вернуть OutsideCode

                ; проверка исключённой верхней границы H третьей области
                LD A, H
                CP @ActionRegionTypeConst.HMiddle
                LD A, @ActionRegionTypeConst.OutsideCode
                RET NC                                                          ; выход, если H не меньше HMiddle, вернуть OutsideCode

                ; проверка нижней границы L третьей области
                LD A, L
                CP @ActionRegionTypeConst.LMiddle
                LD A, @ActionRegionTypeConst.OutsideCode
                RET C                                                           ; выход, если L меньше LMiddle, вернуть OutsideCode

                ; проверка исключённой верхней границы L третьей области
                LD A, L
                CP @ActionRegionTypeConst.LUpper
                LD A, @ActionRegionTypeConst.Code2
                RET C                                                           ; выход, если L меньше LUpper при уже проверенных остальных границах, вернуть Code2

                ; выбор OutsideCode после отказа всех трёх областей, F от последнего CP сохраняется
                LD A, @ActionRegionTypeConst.OutsideCode
                RET

                endmodule
                endmodule
