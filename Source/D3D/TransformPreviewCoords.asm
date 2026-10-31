                module D3D
                module TransformPreviewCoords
                ; Документация [координатное преобразование](../../Docs/PreviewTransform.md)
                ; -----------------------------------------
                ; Три скалярных произведения с переносом знакового умножителя, ранним переполнением и продолжением через IY
                ; исходная запись 6, банк 4, файловые смещения #2B7E..#2C27
                ; In:
                ;   BC - сохраняемый B, младший C становится рабочим нулём умножителя
                ;   IY - адрес продолжения без снятия адреса с CPU-стека
                ;   InputFirst, InputSecond, InputThird содержат три знаковых слова в исходных операндах LD DE,nn
                ;   Coeff11..Coeff33 содержат девять знаковых коэффициентов по договору MultiplyPreviewCoordinate
                ;   банк 4 выбран, рабочие слова результата и ReturnTarget доступны для записи, повторный вход запрещён
                ;   маскируемые прерывания отключены, NMI не возникает, SP во время алгоритма хранит арифметическую сумму
                ; Out:
                ;   HL - последняя принятая сумма либо обёрнутая сумма, вызвавшая ранний выход по переполнению
                ;   DE - выход последнего MultiplyPreviewCoordinate, BC - B входной, C=0
                ;   AF - A знаковый байт последнего умножения, F от последнего ADC HL,SP, P/V=1 означает раннее переполнение
                ;   при отсутствии переполнения ResultFirst, ResultSecond, ResultThird получают три вычисленных слова
                ;   при переполнении записаны только предыдущие завершённые строки, текущая и последующие сохраняют прежние слова
                ;   HL' и BC' сохранены, DE' содержит адрес последнего продолжения RowNFirst, RowNPair либо RowNTotal
                ;   AF' принадлежит последнему умножителю, IX и IY сохранены, I, IFF и IM собственный код не меняет
                ;   SP равен первому произведению либо принятой сумме первых двух в последней обработанной строке, исходный SP не восстанавливается
                ;   финальный JP (IY) передаёт управление без нового адреса возврата, входной CPU-стек не читается
                ;   операнды InputFirst..InputThird и коэффициенты не записываются, ReturnTarget обновляется при каждом умножении
                ; Corrupt:
                ;   HL, DE, BC, AF, DE', AF', SP, завершённые слова результата и ReturnTarget
                ; Note:
                ;   первый результат строки сохраняется в SP, второе произведение складывается с ним через ADC
                ;   после принятия второго результата SP получает частичную сумму, третье произведение снова прибавляется через ADC
                ;   отрицательное ненулевое произведение возвращает Carry=1, эта единица участвует в сложении, обычная матричная сумма неверна
                ;   после каждого из шести ADC P/V немедленно проверяется, на переполнении переход к общему JP (IY) без записи текущей строки
                ;   все три входных координаты читаются заново для каждой строки, единицы и назначение координатных осей здесь не присваиваются
                ;   подтверждённый вызывающий путь устанавливает IY=ED11, локальный договор допускает другой корректный адрес продолжения
                ; -----------------------------------------
                ; чтение первой координаты из изменяемого операнда для первой строки
Entry:          LD DE, #0000
                ; чтение коэффициента первой строки и первой координаты
                LD A, (@PreviewTransformState.Coeff11)
                ; передача координаты в DE' перед назначением основного DE адресом продолжения
                EXX
                ; выбор продолжения первого произведения без CPU-стека
                LD DE, @D3D.TransformPreviewCoords.Row1First
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; сохранение первого произведения в SP как арифметического слова
Row1First:      LD SP, HL
                ; чтение второй исходной координаты для первой строки
                LD DE, #0000
                ; чтение второго коэффициента первой строки
                LD A, (@PreviewTransformState.Coeff12)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row1Pair
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт суммы второго произведения и первого, Carry умножителя участвует
Row1Pair:       ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если сумма первых двух произведений первой строки переполнилась

                ; сохранение принятой суммы двух произведений в SP
                LD SP, HL
                ; чтение третьей исходной координаты для первой строки
                LD DE, #0000
                ; чтение третьего коэффициента первой строки
                LD A, (@PreviewTransformState.Coeff13)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row1Total
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт полной первой строки с переносом третьего умножения
Row1Total:      ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если полная первая строка переполнилась, её результат не записывать

                ; сохранение принятой первой строки в существующем рабочем слове
                LD (@PreviewTransformState.ResultFirst), HL
                ; повторное чтение первой координаты для второй строки
                LD DE, (@PreviewTransformState.InputFirst)
                ; чтение первого коэффициента второй строки
                LD A, (@PreviewTransformState.Coeff21)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row2First
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; сохранение первого произведения второй строки в SP
Row2First:      LD SP, HL
                ; повторное чтение второй координаты
                LD DE, (@PreviewTransformState.InputSecond)
                ; чтение второго коэффициента второй строки
                LD A, (@PreviewTransformState.Coeff22)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row2Pair
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт пары произведений второй строки с переносом умножителя
Row2Pair:       ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если сумма первых двух произведений второй строки переполнилась

                ; сохранение принятой частичной суммы второй строки в SP
                LD SP, HL
                ; повторное чтение третьей координаты
                LD DE, (@PreviewTransformState.InputThird)
                ; чтение третьего коэффициента второй строки
                LD A, (@PreviewTransformState.Coeff23)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row2Total
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт полной второй строки с переносом третьего умножения
Row2Total:      ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если полная вторая строка переполнилась, её результат не записывать

                ; сохранение принятой второй строки
                LD (@PreviewTransformState.ResultSecond), HL
                ; повторное чтение первой координаты для третьей строки
                LD DE, (@PreviewTransformState.InputFirst)
                ; чтение первого коэффициента третьей строки
                LD A, (@PreviewTransformState.Coeff31)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row3First
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; сохранение первого произведения третьей строки в SP
Row3First:      LD SP, HL
                ; повторное чтение второй координаты для третьей строки
                LD DE, (@PreviewTransformState.InputSecond)
                ; чтение второго коэффициента третьей строки
                LD A, (@PreviewTransformState.Coeff32)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row3Pair
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт пары произведений третьей строки с переносом умножителя
Row3Pair:       ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если сумма первых двух произведений третьей строки переполнилась

                ; сохранение принятой частичной суммы третьей строки в SP
                LD SP, HL
                ; повторное чтение третьей координаты для третьей строки
                LD DE, (@PreviewTransformState.InputThird)
                ; чтение третьего коэффициента третьей строки
                LD A, (@PreviewTransformState.Coeff33)
                EXX
                LD DE, @D3D.TransformPreviewCoords.Row3Total
                JP @D3D.MultiplyPreviewCoordinate.Entry

                ; расчёт полной третьей строки с переносом третьего умножения
Row3Total:      ADC HL, SP
                JP PE, @D3D.TransformPreviewCoords.Continue                     ; переход, если полная третья строка переполнилась, её результат не записывать

                ; сохранение принятой третьей строки
                LD (@PreviewTransformState.ResultThird), HL
                ; продолжение по IY с текущими флагами переполнения и рабочим SP
Continue:       JP (IY)

                endmodule
                endmodule
