"""Два режима входа тика и доказанная подготовка строки A в исходном банке MUZ1."""
import re
from MusicChannelBRowFacts import FIELDS as B_FIELDS
from MusicSynthesisFacts import OPERANDS as SYNTH_OPERANDS

FUNCTIONS = {0xDE1F: ('TickDispatch', 'Изменяемый вход тика, выбор синтеза либо перенос подготовленных параметров строки A')}
END_OFFSETS = {0xDE1F: 0x390}
DOCUMENT = 'MusicChannelStaging'
CONTINUATIONS = {0xDE1F: ('StageGateAndSampleA', 0xDE90)}
LABELS = {('Music', 0xDE22): 'ApplyRow', ('Music', 0xDE5C): 'ApplyVolume', ('Music', 0xDE72): 'ApplySlide'}
OLD_LABELS = {'TickDispatch.PointDE5C': 'TickDispatch.ApplyVolume', 'TickDispatch.PointDE72': 'TickDispatch.ApplySlide'}
FIELD_MODULE = 'MusicChannelARow'
FIELDS = {'EntryOpcode': (0xDE1F, 'C3 выбирает JP к синтезу, 01 исполняет LD BC и продолжает подготовку строки')}
_addresses = (0xDE2E, 0xDE31, 0xDE48, 0xDE4D, 0xDE52, 0xDE5D, 0xDE61,
              0xDE68, 0xDE6E, 0xDE72, 0xDE75, 0xDE7A, 0xDE82, 0xDE88)
for (name, (_, note)), address in zip(list(B_FIELDS.items())[:14], _addresses):
    FIELDS[name] = address, re.sub(r'\bB\b', 'A', note).replace('E198', 'E098')

CONTRACTS = {('Music', 0xDE1F): (
    ['HL, DE и BC при EntryOpcode=01 переходят в альтернативные пары, исходный BC заменяется адресом DFE3 до EXX',
     "HL', DE' и BC' после EXX становятся рабочими, исходные HL' и DE' затем замещаются подготовкой",
     'AF входных аргументов не задаёт, EntryOpcode содержит C3 либо 01',
     'NoteBlock, OrnamentBlock и SlideBlock содержат 18 либо 06, EnableCode содержит 00 либо 2F, ResetOpcode содержит 22 либо 01',
     'параметры строки уже подготовлены в доступном для записи банке MUZ1, прерывания запрещены'],
    ['при EntryOpcode=C3 выполнен только JP в RenderChannelA, регистры и память до этой границы сохранены',
     'при EntryOpcode=01 выполнен LD BC,DFE3 и EXX, EntryOpcode восстановлен в C3, продолжение в StageGateAndSampleA по DE90',
     'ResetOpcode=22 обнуляет SlideOffset, 01 сохраняет его и устанавливает рабочий BC=E098',
     'VolumeRow всегда переносится в VolumeOffset, NoteBlock=06 сбрасывает курсоры, накопители и счётчики канала A',
     'ветвь ноты задаёт Disabled=0 при NOP либо FF при CPL, CurrentNote, SamplePointer и AmplitudeAdjust=10',
     'OrnamentBlock=06 обнуляет OrnamentCursor, устанавливает OrnamentPointer и EnvelopeMask',
     'SlideBlock=06 устанавливает TargetNote, SlideCounter, SlideReload, SlideStep и SlideBranch, GateCounter=0',
     'HL равен последнему применённому указателю сэмпла, орнамента либо шагу скольжения, иначе HL=0',
     "B изначально равен входному B', либо E0 при ResetOpcode=01, затем 29 после ноты, 0F после орнамента, 1C после скольжения",
     "C равен входному C', либо 98 при ResetOpcode=01, DE=0618",
     'A равен VolumeRow, затем PendingEnvelope при ветви орнамента, затем 0 при ветви скольжения',
     'F=7E только при включённом NoteBlock с CPL и выключенных орнаменте и скольжении, иначе F=44',
     "HL' и DE' равны исходным HL и DE, BC'=DFE3, AF', IX, IY, SP, I, IM и IFF сохранены"],
    ["HL, DE, BC, AF, HL', DE', BC' при подготовке строки, перечисленные поля, EntryOpcode, R",
     'прямой JP не изменяет перечисленные регистры до начала RenderChannelA'],
    ['ApplyRow является внутренним входом после изменяемой трёхбайтовой команды, это не отдельная вызываемая процедура',
     'три кода пропуска блоков здесь не сбрасываются, их меняет декодер паттерна',
     'SlideBranch=00 включает ограничение целевой нотой, 1D обходит его, эта ветвь исполняется позднее в синтезе',
     'собственного RET нет, договор заканчивается перед StageGateAndSampleA либо перед RenderChannelA',
     'алгоритм подготовки и проверка двух режимов описаны в MusicChannelStaging.md'])}

COMMENTS = {
    0xDE1F: (['изменяемый вход, C3 выполняет JP к синтезу, 01 превращает те же байты в LD BC,DFE3'], None),
    0xDE22: (['переключение на подготовленный декодером комплект регистров перед применением строки A'], None),
    0xDE23: (['восстановление прямого входа к синтезу для следующего тика'], None),
    0xDE28: (['подготовка нулевого HL для сбросов и пары DE с кодами пропуска и включения блоков'], None),
    0xDE2E: (['изменяемая команда, 22 обнуляет SlideOffset, 01 загружает BC адресом E098 без записи'], None),
    0xDE31: (['изменяемый JR пропускает сброс ноты, код 06 включает тело и загружает B длиной 29'], None),
    0xDE33: (['сброс курсоров сэмпла и орнамента, накопителей шума и огибающей, счётчиков скольжения и чередования'], None),
    0xDE45: (['сброс накопленной тональной поправки сэмпла'], None),
    0xDE48: (['изменяемый NOP оставляет ноль для включения A, CPL создаёт выключенное состояние FF'], None),
    0xDE4C: (['перенос ожидающего индекса ноты в текущую ноту синтеза A'], None),
    0xDE51: (['перенос ожидающего указателя сэмпла'], None),
    0xDE57: (['возврат поправки уровня к нейтральному значению 10'], None),
    0xDE5C: (['перенос смещения строки громкости независимо от наличия новой ноты'], None),
    0xDE61: (['изменяемый JR пропускает подготовку орнамента, код 06 включает тело'], None),
    0xDE63: (['сброс позиции орнамента перед переносом его нового указателя'], None),
    0xDE67: (['перенос ожидающего указателя орнамента'], None),
    0xDE6D: (['перенос ожидаемой маски огибающей в расчёт амплитуды A'], None),
    0xDE72: (['изменяемый JR пропускает настройку скольжения, код 06 включает тело'], None),
    0xDE74: (['перенос ожидающей целевой ноты ограниченного скольжения'], None),
    0xDE79: (['запуск задержки шага вместе с установкой её перезагрузки'], None),
    0xDE81: (['перенос знакового слова шага скольжения A'], None),
    0xDE87: (['перенос смещения JR, выбирающего ограничение целевой нотой либо его обход'], None),
    0xDE8C: (['отключение текущего чередования разрешения при подготовке скольжения'], None)}


def name_operands(region, address, operation):
    if region == 'Music' and address in FUNCTIONS:
        names = dict(SYNTH_OPERANDS)
        names.update({a: FIELD_MODULE + '.' + name for name, (a, _) in FIELDS.items()})
        names.update({0xDE22: 'Music.TickDispatch.ApplyRow', 0xDE5C: 'Music.TickDispatch.ApplyVolume',
                      0xDE72: 'Music.TickDispatch.ApplySlide', 0xDE90: 'Music.StageGateAndSampleA.Entry',
                      0xDFE3: 'Music.RenderChannelA.Entry'})
        operation = re.sub(r'#([0-9A-F]{4})', lambda m: '@' + names[int(m[1], 16)]
                           if int(m[1], 16) in names else m[0], operation)
    return operation
