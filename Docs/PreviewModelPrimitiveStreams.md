# Грани и линии моделей предпросмотра

После нулевой маски каждой из десяти [групп вершин](PreviewModelGroups.md)
начинается поток положительных заголовков граней и отрицательных
заголовков линий. Нулевой заголовок завершает поток точно перед
следующим исходным блоком. Все смещения относятся к записи D3D в банке 4.

| Модель | Смещения, конец без включения | Грани | Линии |
|---|---|---:|---:|
| [Orsan](../Source/D3D/Data/ModelPrimitives/Orsan.asm) | 306D..30F6 | 28 | 0 |
| [Memfis](../Source/D3D/Data/ModelPrimitives/Memfis.asm) | 3109..3163 | 19 | 0 |
| [Dominion и Karen](../Source/D3D/Data/ModelPrimitives/Dominion.asm) | 3192..31F6 | 19 | 2 |
| [Baros](../Source/D3D/Data/ModelPrimitives/Baros.asm) | 320D..3271 | 21 | 0 |
| [Firs](../Source/D3D/Data/ModelPrimitives/Firs.asm) | 328C..32C0 | 11 | 0 |
| [Sofist](../Source/D3D/Data/ModelPrimitives/Sofist.asm) | 32E3..333F | 19 | 2 |
| [Kridon](../Source/D3D/Data/ModelPrimitives/Kridon.asm) | 3356..33AB | 18 | 0 |
| [Algol](../Source/D3D/Data/ModelPrimitives/Algol.asm) | 33CA..3467 | 32 | 0 |
| [Protos](../Source/D3D/Data/ModelPrimitives/Protos.asm) | 347A..34D1 | 18 | 0 |
| [Fervest](../Source/D3D/Data/ModelPrimitives/Fervest.asm) | 34F0..3581 | 34 | 0 |

Младшая тетрада заголовка задаёт длину списка. В грани биты 6..4
задают материал, в линии бит 6 связывает её с ориентацией предыдущей
грани, биты 5..4 выбирают пиксельную операцию. Индексы кратны пяти.
После деления на пять каждый индекс меньше числа вершин, получаемых из
битов масок соответствующей модели. Размеры физических записей совпадают
с уже существующими FActionModelPrimitiveN.

13 изменяемых заголовков из [переключателя заполнения](PreviewFaceFill.md)
связаны утверждениями размещения с физическими экземплярами. Это
семь четырёхугольников и шесть треугольников. Обе ветви
[рисователя](PreviewFaceStream.md) читали эти адреса при исполнении
исходных кадров, [отчёт кадров](../Tools/Disasm/Reports/D3DFrameProbe.json).

[Проверка формата](../Tools/Disasm/Research/PreviewModelPrimitiveStreams.py)
сверяет все 1045 байтов, 219 граней, четыре линии, 10 ограничителей
и границы записи. [Отчёт](../Tools/Disasm/Reports/PreviewModelPrimitiveStreamsVerification.json).
