                module Station
                module BeginScreenUpdate
; Документация [Station](../../Docs/FunctionDetails/Station.md)
; Подробный разбор [два физических экрана и указатель](../../Docs/ScreenUpdate.md)
; -----------------------------------------
; Копирование старого экрана в банк 7 перед восстановлением фона указателя и скрытым обновлением
; исходная запись 4, файловые смещения #449F..#46C3
; In:
;   HL, DE, BC - сохраняемый контекст, AF - A рабочий, исходные S,Z,Carry участвуют в итоговых флагах
;   аппаратная блокировка #7FFD.bit5 снята, действуют стандартные фиксированные банки 5 и 2 Spectrum 128
;   базовый экран по #4000 и банк 7 доступны, состояние указателя удовлетворяет SuspendPointer
;   стек вне экранных 6912 байтов и выполняемых участков, ISR не меняет контекст и выбранную страницу во время переноса
; Out:
;   HL, DE и BC сохранены, A=#18, F=(входной F AND #C1) OR ((#17+последний_байт_снимка) AND #08) OR (((#17+последний_байт_снимка) AND #02)<<4)
;   тень CurrentPage=#18, окно #C000 выбирает банк 0, отображается экран банка 7
;   6912 байтов старого базового экрана скопированы в банк 7 до восстановления фона указателя
;   UpdateBlocked=1, активный указатель удалён из банка 5, его снимок в банке 7 сохраняется
; Corrupt:
;   AF
; Note:
;   альтернативные и индексные регистры, I и IFF сохраняются, SP восстанавливается
;   FScreenUpdateFrame хранит SavedBC, SavedDE, SavedHL, ReturnAddress
;   256 исходных LDI копируют блок 256 байтов, JP PE повторяет его до BC=0, всего 27 блоков
;   первый OUT=#17 выбирает окно банка 7 и показ банка 5, последний OUT=#18 возвращает окно банка 0 и показ банка 7
;   если фон уже восстановлен, прежнее ненулевое RestoredFlag не нормализуется, при активном рисунке становится 1
;   прежняя страница, ROM и выбор экрана не восстанавливаются, итог задаётся фиксированным #18
;   обычный вызывающий путь начинает с базового отображаемого экрана, временная видимость произвольных входных режимов моделью не проверяется
; -----------------------------------------
                ; создание FScreenUpdateFrame с исходными HL, DE, BC
Entry:          PUSH HL
                PUSH DE
                PUSH BC
                ; запрет периодического обновления указателя до снимка и восстановления фона
                LD A, #01
                LD (@PointerState.UpdateBlocked), A
                ; выбор банка 7 в окне #C000 при ещё отображаемом экране банка 5
                LD A, @ScreenUpdateConst.CopyPage
                CALL @Station.SelectMemoryPage.Entry
                ; подготовка переноса 6912 байтов пикселей и атрибутов из базового экрана
                LD HL, @ScreenUpdateConst.BaseScreen
                LD DE, @ScreenUpdateConst.BankWindow
                LD BC, @ScreenUpdateConst.ScreenBytes
                ; 256 развёрнутых LDI копируют один блок, BC уменьшается на 256, A остаётся #17
Copy256:        LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                LDI
                ; проверка оставшегося BC через P/V последнего LDI
                JP PE, @Station.BeginScreenUpdate.Copy256                       ; переход, если BC ненулевой, скопировать следующий блок 256 байтов

                ; восстановление фона указателя в банке 5 после того, как его рисунок уже попал в снимок банка 7
                CALL @Station.SuspendPointer.Entry
                ; снятие FScreenUpdateFrame с восстановлением исходных BC, DE и HL
                POP BC
                POP DE
                POP HL
                ; возврат окна банка 0 и показ старого снимка из банка 7 на время скрытого рисования
                LD A, @ScreenUpdateConst.HiddenPage
                CALL @Station.SelectMemoryPage.Entry
                RET

                endmodule
                endmodule
