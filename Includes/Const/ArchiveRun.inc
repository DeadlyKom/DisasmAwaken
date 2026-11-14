                module ArchiveRunConst
StackTop        equ #6000                                                       ; верхняя граница стека архивного меню
Window          equ #C000                                                       ; окно страниц экранов
ScreenBytes     equ #1B00                                                       ; растр и атрибуты
BitmapBytes     equ #1800                                                       ; размер растра без атрибутов
AttributeBytes  equ #0300                                                       ; длина атрибутов
BlankAttribute  equ #07                                                         ; белые чернила на чёрном фоне
VectorBase      equ #5E00                                                       ; начало таблицы IM2
VectorTail      equ #0100                                                       ; число байтов после первого
VectorFill      equ #5F                                                         ; одинаковые байты адреса переходника
VectorJump      equ #5F5F                                                       ; код команды перехода к IRQ
VectorOperand   equ #5F60                                                       ; слово адреса IRQ
VectorPage      equ #5E                                                         ; старший байт таблицы IM2
MemoryMode      equ #5F5E                                                       ; настройка для START и ENGINE
LoadPage        equ #10                                                         ; базовая страница и ROM перед передачей в TR-DOS
LoadByName      equ #FF                                                         ; поиск ключа и загрузка через TR-DOS
MenuTop         equ #C8CE                                                       ; первый байт строки заголовка меню в экранном окне
ModeCaption     equ #C8EE                                                       ; адрес подписи режима памяти
FirstItem       equ #01                                                         ; заголовок имеет индекс 0 и не выбирается
PrevKeyCode     equ #01                                                         ; код движения к предыдущему пункту
NextKeyCode     equ #02                                                         ; код движения к следующему пункту
ConfirmKeyCode  equ #03                                                         ; код подтверждения пункта
GlyphBaseCode   equ #20                                                         ; первый код в шрифте
GlyphHeight     equ #08                                                         ; восемь строк знакоместа
PagingBase      equ #15                                                         ; ROM 48K и страница 5 при нулевом селекторе
MarkerBaseY     equ #70                                                         ; строка заголовка перед первым пунктом
MarkerPixelX    equ #69                                                         ; пиксельная координата стрелки выбора
                endmodule
