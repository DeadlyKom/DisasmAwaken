# Физические слова базиса кадра

Девять слов по `#9B00..#9B11` оформлены именованными
[экземплярами FBasisWord](../Source/Action/Data/RenderBasis.asm).
Поля Low и High занимают по байту, слово имеет размер два байта.
В исходном дисковом содержимом C00, C11 и C22 равны 7FFF, остальные
шесть слов равны нулю. Эти значения сохранены буквально.

| Адрес слова | Экземпляр | Старший байт передаётся в |
|---|---|---|
| 9B00 | C00 | ActionPatchedVectorCoeffs.C00 |
| 9B02 | C10 | ActionPatchedVectorCoeffs.C10 |
| 9B04 | C20 | ActionPatchedVectorCoeffs.C20 |
| 9B06 | C01 | ActionPatchedVectorCoeffs.C01 |
| 9B08 | C11 | ActionPatchedVectorCoeffs.C11 |
| 9B0A | C21 | ActionPatchedVectorCoeffs.C21 |
| 9B0C | C02 | ActionPatchedVectorCoeffs.C02 |
| 9B0E | C12 | ActionPatchedVectorCoeffs.C12 |
| 9B10 | C22 | ActionPatchedVectorCoeffs.C22 |

Названия соответствуют реальному порядку коэффициентов
[подготовителя кадра](../Source/Action/RenderSceneFrame.asm).
Он читает High каждого слова. Значение 80 заменяется на 81, затем байт
записывается в соответствующий операнд вычислителя. Младшие байты
не передаются в восьмибитные коэффициенты.

[RotateBasisVectors](../Source/Voxel/RotateBasisVectors.asm) обновляет
все три вектора по трём последовательным этапам. Используются уже
физически оформленные байты Phase2, Phase0 и Phase1 по 9B14, 9B12 и 9B13.
Нулевой угол копирует соответствующие текущие компоненты через рабочие
операнды. Ненулевой вызывает SignedSeededProduct с исходной зависимостью
от IY. Поэтому слово «базис» здесь описывает установленные потребители,
а не доказательство ортогональности или сохранения длины векторов.

[Банковая обёртка](../Source/Action/RotateBankedBasis.asm) выбирает
страницу 3 и возвращает страницу 0. Её
[1024 композиционных сценария](../Tools/Disasm/Reports/ActionBankedBasisRotationVerification.json)
сверяли регистры и физическую RAM с прямым дочерним исполнением.
Это отдельное свидетельство от типизации восемнадцати байтов и
не независимое доказательство всей математики поворота.

[Публикация](../Tools/Disasm/Research/ClassifyActionRenderBasisData.py)
проверяет исходные значения, поля, адреса, символы и последовательность
инструкций. [Фабрика записей](../Tools/Disasm/Research/ActionRenderBasisData.py)
сохраняет имена при отдельном исследовательском экспорте.
Общая сборка не требует исследовательских сценариев.
Сборка и нативный запуск этого среза не выполнялись.

[NegateOuterBasisRows](../Source/Action/NegateOuterBasisRows.asm) меняет знак C20, C21, C22, C00, C01 и C02 без перестановок, средняя строка сохраняется. Его [66304 сценария](ActionReverseViewBasis.md) отделены от [полного переключателя вида](ActionViewDirectionCommand.md), который дополнительно перестраивает точки и пишет пары опкодов.
