# Форматы данных

Объявления находятся в `Includes/Structs/Include.inc`.

| Тип | Размер | Подтверждённое назначение |
| --- | --- | --- |
| FTrDosEntry | #10 | исходная запись каталога |
| FPackedHeader | #06 | HR, распакованная и упакованная длины |
| FPackedFinalBytes | #06 | три пары финальных байтов, [20 физических экземпляров](PackedResourcePrefix.md) |
| FMusicEffectTarget | #02 | поле Handler, [21 физический указатель отложенных музыкальных команд](MusicEffects.md) |
| FMusicDeferredPairFrame | #06 | [динамическая рамка двух отложенных обработчиков и внешнего возврата](MusicEffects.md) |
| FMusicLoopHeader | #02 | LoopPosition и Length исходных сэмплов и орнаментов, [порядок обхода](MusicSynthesis.md) |
| FMusicSampleStep | #04 | ShiftControl, LevelModes и ToneDelta, [алгоритм синтеза и схема битов](MusicSynthesis.md) |
| FMusicDataPointer | #02 | [48 физических указателей сэмплов и орнаментов](MusicPlayerData.md) |
| FMusicAyRegisters | #0E | [единственный буфер регистров AY](MusicPlayerData.md) |
| FMusicRowCounter | #01 | [три физических счётчика строк](MusicPlayerData.md) |
| FMusicVolumeRow | #10 | [15 физических строк громкости, нулевая строка наложена на AY](MusicPlayerData.md) |
| FMusicNotePeriod | #02 | [96 физических слов периодов](MusicPlayerData.md) |
| FMusicModuleHeader | #69 | [физический заголовок композиции, включая Unknown63](MusicComposition.md) |
| FMusicRelativePointer | #02 | [48 физических относительных адресов](MusicComposition.md) |
| FMusicPositionByte | #01 | [28 позиций и отдельный маркер FF](MusicComposition.md) |
| FMusicPatternPointers | #06 | [19 физических троек указателей A/B/C](MusicComposition.md) |
| FMusicOrnamentStep | #01 | [57 физических поправок индекса ноты](MusicComposition.md) |
| FVisualEffect | #12 | запись эффекта, свободное состояние +7 |
| FInterfaceItem | #10 | прямоугольник, флаги и два обработчика интерфейса |
| FProjectedPoint | #05 | X, Y и составной код отсечения вершины |
| FScriptToken | #03 | символ и указатель обработчика, 102 физических экземпляра |
| FExpressionCall | #06 | левый операнд, адрес операции и правый операнд на стеке выражений |
| FTexturePhase | #06 | фаза, её приращение и изменение приращения, три физических экземпляра |
| FGlyphRoute | #04 | два адреса участков глифа, 128 физических экземпляров |
| FGlyphFrame | #10 | семь сохранённых пар регистров и адрес возврата на CPU-стеке |

Поля Unknown сохраняют неустановленное назначение. Объявление структуры
само по себе не выделяет новую область памяти.

В [исходной композиции](MusicComposition.md) оформлены 26 физических FMusicLoopHeader
и 77 FMusicSampleStep. Смещения полей и потребление исходным ядром проверены.

В данных интерфейса сохранены 46 физических инициализаторов, затем #80.
В `Source/Screens` сохранены 20 упакованных блоков с заголовками и хвостами.
Физические экземпляры FScriptToken находятся в
[TokenBindings.asm](../Source/Text/Data/TokenBindings.asm), а записи FExpressionCall
создаются во время выполнения языка. Форматы и потребители разобраны в
[ScriptLanguage](ScriptLanguage.md).
Таблица [Squares.bin](../Source/Map/Resources/Squares.bin) хранит младшие
и старшие байты 256 квадратов в двух последовательных страницах,
подробности в [MapMath](MapMath.md).
Ресурсы [FontWidths.bin](../Source/Station/Resources/FontWidths.bin) и
[FontGlyphs.bin](../Source/Station/Resources/FontGlyphs.bin) содержат
256 ширин и 256 восьмибайтовых глифов, подробности в [Font](Font.md).
Остальные неклассифицированные диапазоны нельзя считать автоматически ресурсами
или автоматически кодом, даже если они находятся в Source/Resources.

| Запись | Имя | Параметр | Длина | Секторов | Хвост |
| --- | --- | --- | ---: | ---: | ---: |
| 0 | _XTime15.B (удалена) | #0147 | 327 | 237 | 60345 |
| 1 | _xt.char.t (удалена) | #05C7 | 8205 | 33 | 243 |
| 2 | _L->TXT.H (удалена) | #0000 | 521 | 3 | 247 |
| 3 | AWAKEN.B | #0077 | 119 | 45 | 11401 |
| 4 | STATIONF.C | #6000 | 40960 | 160 | 0 |
| 5 | LANG.C | #C000 | 3864 | 16 | 232 |
| 6 | D3D.C | #C000 | 15978 | 63 | 150 |
| 7 | KARTA.C | #C000 | 11776 | 46 | 0 |
| 8 | HELP.C | #DB00 | 5921 | 24 | 223 |
| 9 | stscr.C | #C000 | 3230 | 239 | 57954 |
| 10 | MUZ1.C | #DB00 | 7209 | 29 | 215 |
| 11 | SAVE1.s | #6000 | 512 | 2 | 0 |
| 12 | SAVE2.s | #6000 | 512 | 2 | 0 |
| 13 | SAVE3.s | #6000 | 512 | 2 | 0 |
| 14 | SAVE4.s | #6000 | 512 | 2 | 0 |
| 15 | SAVE5.s | #6000 | 512 | 2 | 0 |
| 16 | SAVE0.s | #6000 | 512 | 2 | 0 |
| 17 | ACTION.C | #6000 | 40960 | 160 | 0 |
| 18 | DATAS.C | #8C00 | 7213 | 29 | 211 |
| 19 | 3DPART.C | #C000 | 8224 | 33 | 224 |
| 20 | VOXAL0.C | #C000 | 11264 | 44 | 0 |
| 21 | VOXAL.C | #EC00 | 3784 | 15 | 56 |
| 22 | CONTROL0.C | #C000 | 6878 | 27 | 34 |
| 23 | CONTROL.C | #DADE | 6474 | 26 | 182 |
| 24 | OBJECT3D.C | #C000 | 10580 | 42 | 172 |
| 25 | PANEL.C | #6373 | 1463 | 6 | 73 |
| 26 | PANELF.C | #2020 | 1436 | 6 | 100 |
| 27 | PANELMET.C | #2020 | 1423 | 6 | 113 |
| 28 | PANELFF.C | #7263 | 1543 | 7 | 249 |
| 29 | FINALF.C | #6000 | 19114 | 75 | 86 |
| 30 | scene1po.s | #7270 | 18676 | 73 | 12 |
| 31 | choose1.C | #2020 | 6912 | 27 | 0 |
| 32 | choose2.C | #2020 | 6912 | 27 | 0 |
| 33 | BANK0.C | #C000 | 16384 | 64 | 0 |
| 34 | BANK1.C | #C000 | 16384 | 64 | 0 |
| 35 | BANK2.C | #C000 | 16384 | 64 | 0 |
| 36 | BANK3.C | #C000 | 16384 | 64 | 0 |
| 37 | BANK4.C | #C000 | 16384 | 64 | 0 |
| 38 | BANK5.C | #C000 | 16384 | 64 | 0 |
| 39 | BAR.C | #8000 | 3076 | 13 | 252 |
| 40 | BD0.C | #C000 | 16268 | 64 | 116 |
| 41 | BD1.C | #C000 | 16152 | 64 | 232 |
| 42 | BD2.C | #C000 | 16248 | 64 | 136 |
| 43 | BD3.C | #C000 | 12048 | 48 | 240 |

FCenteredItemFrame описывает десятибайтовый динамический CPU-стек обработчика,
см. [CenteredItem](CenteredItem.md). Статический экземпляр и новая память не создаются.

FCaptionItemFrame и FBandWaitFrame описывают динамические кадры 12 и 8 байтов,
см. [CaptionItem](CaptionItem.md). Их создают исходные PUSH, статической памяти нет.

FDrawListEntry описывает двухбайтовый указатель runtime-списка обработчиков.
Его старший байт 1 является ограничителем, см. [DrawAdapters](DrawAdapters.md).

FDrawMoveFrame, FDrawShiftFrame и FRestoreBoundsFrame описывают динамические
кадры изменения списка и восстановления геометрии, см. [MoveDrawItem](MoveDrawItem.md) и [InterfaceBounds](InterfaceBounds.md).

## Строки указателя

[PointerSprites](../Source/Station/Data/PointerSprites.asm) содержит 192 физических FPointerRasterRow по четыре байта, MaskLeft, XorLeft, MaskRight, XorRight. Три страницы по восемь фаз сдвига и восемь строк каждой фазы сохраняют исходные #6000..#62FF. [PointerBackground](../Source/Station/Data/PointerBackground.asm) содержит восемь физических FPointerSavedRow по два байта Left, Right по #6575..#6584. Инициализаторы сохранены побайтно, во время работы заменяются сохранёнными экранными байтами. Динамический FPointerGuardFrame размером 12 байтов создаётся на CPU-стеке обёртками, отдельного статического экземпляра не имеет. Подробности и ограничения приведены в [Pointer](Pointer.md).
