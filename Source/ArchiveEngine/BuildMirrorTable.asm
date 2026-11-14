                module ArchiveEngine
                module BuildMirrorTable
                ; Документация [зеркальное наложение](../../Docs/FighterAssets.md#вывод-и-чтение-секторов)
                ; -----------------------------------------
                ; создание таблицы обращения битов для зеркального вывода кадров
                ; In:
                ;   параметров нет, RAM #7600..#76FF доступна для записи
                ; Out:
                ;   HL - начало таблицы, после обхода младший байт снова равен нулю
                ;   RAM #7600..#76FF - в каждой записи биты 7..0 соответствуют битам 0..7 индекса
                ; Corrupt:
                ;   HL, DE, AF
                ; Note:
                ;   E сохраняется, Carry на входе не влияет на восемь извлечённых битов
                ; -----------------------------------------
Entry:          LD HL, @ArchiveEngineConst.MirrorTable

                ; обращение порядка восьми битов индекса в D через Carry
ReverseByte:    LD A, L
                LD D, A
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                RL A
                RR D
                ; сохранение результата и проверка обхода всей страницы
                LD (HL), D
                INC L
                JR NZ, @ArchiveEngine.BuildMirrorTable.ReverseByte              ; переход, если младший байт адреса ещё не обернулся, построить следующую запись

                RET

                endmodule
                endmodule
