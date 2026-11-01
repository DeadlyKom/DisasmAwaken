                module Music
                module StageChannelBRow
                ; Документация [отложенные состояния каналов](../../Docs/MusicChannelStaging.md)
                ; -----------------------------------------
                ; Сброс накопленного скольжения, подготовка ноты, орнамента и параметров скольжения строки B
                ; исходная запись 10, файловые смещения #03B9..#041D
                ; In:
                ;   HL и AF входных аргументов не задают, DE и C сохраняются, B сохраняется при всех выключенных блоках
                ;   NoteBlock, OrnamentBlock и SlideBlock содержат 18 либо 06, EnableCode содержит 00 либо 2F, ResetOpcode содержит 22 либо 01
                ;   ожидающие параметры подготовлены в доступном для записи банке MUZ1, прерывания запрещены согласно кадровому входу
                ; Out:
                ;   граница блока находится в StageGateB по DF1E, собственного RET нет
                ;   при ResetOpcode=22 SlideOffset обнуляется, при 01 сохраняется и BC получает E198, VolumeRow всегда переносится в VolumeOffset
                ;   при NoteBlock=06 обнуляются курсоры, шумовой, тональный и огибающий накопители, счётчики скольжения и чередования
                ;   та же ветвь устанавливает Disabled=0 при NOP либо FF при CPL, CurrentNote, SamplePointer и AmplitudeAdjust=10
                ;   при OrnamentBlock=06 обнулён OrnamentCursor, установлены OrnamentPointer и EnvelopeMask
                ;   при SlideBlock=06 установлены TargetNote, SlideCounter, SlideReload, SlideStep и SlideBranch, GateCounter=0
                ;   HL равен последнему применённому указателю сэмпла, орнамента либо слову шага, при всех выключенных блоках HL=0
                ;   B равен 29 после сброса ноты, 0F после орнамента, 1C после скольжения, последняя включённая ветвь имеет приоритет
                ;   при ResetOpcode=01 C=98 и начальный B=E1, иначе C и начальный B сохраняются
                ;   A равен VolumeRow, затем PendingEnvelope при ветви орнамента, затем 0 при ветви скольжения
                ;   F=7E только при включённом NoteBlock с CPL и выключенных остальных блоках, иначе F=44
                ;   DE, альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы следующего блока
                ; Corrupt:
                ;   HL, BC, AF, SlideOffset при ResetOpcode=22, VolumeOffset и перечисленные поля включённых ветвей, R
                ; Note:
                ;   коды трёх пропускаемых блоков здесь не сбрасываются, их последующее изменение задаётся разбором паттерна
                ;   EnableCode и ResetOpcode являются изменяемыми инструкциями, их нельзя считать обычными битовыми флагами
                ;   в проверке SlideBranch принимает 00 для ограничения целевой нотой и 1D для обхода этого ограничения
                ;   задержки, указатели и слова шага копируются без проверки, исполнение синтеза за DF1E не входит в локальный договор
                ; -----------------------------------------
                ; подготовка нулевого HL перед изменяемой командой сброса либо сохранения скольжения B
Entry:          XOR A
                LD L, A
                LD H, A
                ; изменяемая команда, 22 записывает нулевой HL в SlideOffset, 01 загружает BC адресом E198 без записи
                LD (@MusicChannelBRow.SlideOffset), HL
                ; изменяемый JR пропускает полный сброс ноты, код 06 включает его тело
                JR @Music.StageChannelBRow.ApplyVolume

                ; сброс позиции сэмпла, накопителей шума и огибающей, позиции орнамента и счётчиков
                LD (@MusicChannelBRow.SampleCursor), A
                LD (@MusicChannelBRow.NoiseAccum), A
                LD (@MusicChannelBRow.EnvelopeAccum), A
                LD (@MusicChannelBRow.OrnamentCursor), A
                LD (@MusicChannelBRow.SlideCounter), A
                LD (@MusicChannelBRow.GateCounter), A
                ; сброс накопленной тональной поправки сэмпла
                LD (@MusicChannelBRow.ToneAccum), HL
                ; изменяемая инструкция, NOP оставляет ноль для включения B, CPL создаёт FF для выключения
                CPL
                LD (@MusicChannelBRow.Disabled), A
                ; чтение ожидающей ноты и запись её текущего индекса
                LD A, #00
                LD (@MusicChannelBRow.CurrentNote), A
                ; перенос ожидающего указателя сэмпла в синтез B
                LD HL, #0000
                LD (@MusicChannelBRow.SamplePointer), HL
                ; сброс направленного изменения амплитуды значением 10
                LD A, #10
                LD (@MusicChannelBRow.AmplitudeAdjust), A
                ; перенос смещения строки громкости независимо от наличия новой ноты
ApplyVolume:    LD A, #00
                LD (@MusicChannelBRow.VolumeOffset), A
                ; изменяемый JR пропускает настройку орнамента, код 06 включает её тело
                JR @Music.StageChannelBRow.ApplySlide

                ; сброс позиции орнамента перед сменой его указателя
                XOR A
                LD (@MusicChannelBRow.OrnamentCursor), A
                ; перенос ожидающего указателя орнамента в синтез B
                LD HL, #0000
                LD (@MusicChannelBRow.OrnamentPointer), HL
                ; перенос ожидающей маски огибающей в расчёт амплитуды B
                LD A, #00
                LD (@MusicChannelBRow.EnvelopeMask), A
                ; изменяемый JR пропускает настройку скольжения, код 06 включает её тело
ApplySlide:     JR @Music.StageGateB.Entry

                ; перенос ожидающей целевой ноты для ограничения скольжения
                LD A, #00
                LD (@MusicChannelBRow.TargetNote), A
                ; запуск счётчика задержки вместе с установкой его перезагрузки
                LD A, #00
                LD (@MusicChannelBRow.SlideCounter), A
                LD (@MusicChannelBRow.SlideReload), A
                ; перенос слова шага скольжения B
                LD HL, #0000
                LD (@MusicChannelBRow.SlideStep), HL
                ; перенос смещения JR, выбирающего ограничение целевой нотой либо его обход
                LD A, #00
                LD (@MusicChannelBRow.SlideBranch), A
                ; отключение текущего чередования разрешения канала при подготовке скольжения
                XOR A
                LD (@MusicChannelBRow.GateCounter), A
                ; JP @Music.StageGateB.Entry, продолжение в StageGateB.asm

                endmodule
                endmodule
