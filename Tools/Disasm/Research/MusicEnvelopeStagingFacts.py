"""Подготовка огибающей, физические границы и изменяемые операнды MUZ1."""
import re
FUNCTIONS={0xDF47:('StageEnvelopeAndNoise','Подготовка формы огибающей и шума, перезапуск её периода и отложенного скольжения'),0xDF70:('CommitEnvelopeSlide','Фиксация шага и задержки скольжения огибающей перед продолжением разбора канала A')}
RENAMES={'UnknownDF47':'StageEnvelopeAndNoise','UnknownDF70':'CommitEnvelopeSlide'}
LABELS={('Music',0xDF61):'PrepareNoise',('Music',0xDF6D):'PendingStep'}
LABEL_RENAMES={'UnknownDF47.PointDF61':'StageEnvelopeAndNoise.PrepareNoise'}
CONTRACTS={('Music',0xDF47):(
 ['HL сохранится только при нулевой форме и выключенном отложенном шаге, DE задаёт E=18 для выключения отложенного шага',
  'BC задаёт сохраняемый C и исходный B для пути без отложенного шага, AF входных аргументов не задаёт',
  'банк MUZ1 доступен для записи, SlideGate содержит JR 18 либо LD B,n 06, Step и Delay подготовлены писателями команд',
  'прерывания запрещены согласно кадровому входу, SP остаётся доступным до дальнейшего AdvancePatternA'],
 ['граница выхода блока находится в AdvancePatternA по DF7F, собственного RET нет',
  'буфер AY13 получает Shape, AY6 получает Noise, Phase=RowTempo готовит отложенный разбор каналов B и C',
  'ненулевой Shape переносит Base в EnvelopeBase, очищает Shape и SlideOffset, сбрасывает SlideCounter',
  'при SlideGate=06 дополнительно выполняется CommitEnvelopeSlide, HL=Step, B=12, A=18',
  'при SlideGate=18 A=Noise, B сохранён, HL=0 при ненулевом Shape, иначе входной HL',
  'C и DE сохранены, F=44, нулевая форма даёт OR 0, ненулевая ветвь завершается XOR A',
  'альтернативные пары, IX, IY, SP, I, IM и IFF сохранены до границы DF7F'],
 ['HL, BC, AF по условному договору, Shape, буфер AY6 и AY13, Phase, EnvelopeBase, SlideOffset, SlideCounter',
  'при включённом отложенном шаге также SlideStep, SlideReload и SlideGate, R продвигается'],
 ['Shape=0 означает отсутствие нового запроса формы, общий вывод AY отдельно пропускает запись AY13 при нуле',
  'Phase является числовым счётчиком от RowTempo до 0, а не битовой маской микшера, исходный байт темпа 03 изменяем',
  'этот блок не выводит порты, синтез и портовый вывод выполняются после продолжения кадрового пути',
  'полный тиковый возврат и независимое аудио не следуют из проверки границы DF7F']),
 ('Music',0xDF70):(
 ['HL=шаг скольжения огибающей, DE задаёт E=18 в штатном пути после LD DE,0618',
  'BC и AF не задают иных аргументов, Delay содержит байт задержки команды',
  'банк MUZ1 доступен для записи, прерывания запрещены согласно кадровому входу'],
 ['HL записан в SlideStep, Delay записан одновременно в SlideCounter и SlideReload',
  'SlideGate получает E, штатное 18 восстанавливает JR и выключает повторное применение команды',
  'HL, DE, BC сохранены, A=входной E, F сохранён, альтернативные пары, IX, IY, SP, I, IM и IFF сохранены',
  'исполнение последовательно продолжается в AdvancePatternA по DF7F без снятия адреса со стека'],
 ['AF только A, SlideStep, SlideCounter, SlideReload, SlideGate, R'],
 ['при E, отличном от 18, записывается именно этот байт, корректность будущего музыкального кода тогда не предполагается',
  'задержка ноль сохраняется без исправления, последующий DEC счётчика определяет её поведение',
  'контракт задан на границе блока, общего возвращаемого значения тика он не определяет'])}
COMMENTS={
 0xDF47:(['чтение ожидающей формы огибающей, ноль не запрашивает новую запись AY13'],None),
 0xDF49:(['перенос ожидающей формы в однократный буфер аппаратного регистра'],None),
 0xDF4C:(['проверка наличия новой формы для перезапуска периода и его скольжения'],None),
 0xDF4D:([],'переход, если Shape равен нулю, сохранить текущий период и накопленное скольжение'),
 0xDF4F:(['чтение нового базового периода огибающей из изменяемого операнда Base'],None),
 0xDF52:(['обновление базового периода для последующего суммирования огибающей'],None),
 0xDF55:(['сброс однократной формы, накопленного смещения и счётчика скольжения'],None),
 0xDF61:(['чтение изменяемого темпа строки для счётчика распределённого разбора каналов B и C'],None),
 0xDF66:(['чтение базового шума и перенос в буфер AY6 до добавления текущего вклада сэмплов'],None),
 0xDF6B:(['изменяемый JR пропускает отложенную команду, байт 06 превращает его в LD B,12'],None),
 0xDF6D:(['чтение отложенного шага скольжения после включения команды писателем'],None),
 0xDF70:(['обновление шага, который последующие кадры прибавляют к смещению огибающей'],None),
 0xDF73:(['чтение задержки и одновременный запуск счётчика с подготовкой его перезагрузки'],None),
 0xDF7B:(['выключение однократной команды восстановлением JR из штатного E=18'],None)}
TARGETS={0xDF61:'Music.StageEnvelopeAndNoise.PrepareNoise',0xDF7F:'Music.AdvancePatternA.Entry',
 0xDC0D:'MusicEnvelopeState.AyShape',0xDC06:'MusicEnvelopeState.AyNoise',0xE2F1:'MusicEnvelopeState.EnvelopeBase',
 0xDF48:'MusicEnvelopeState.Shape',0xE2EE:'MusicEnvelopeState.SlideOffset',0xE2FA:'MusicEnvelopeState.SlideCounter',
 0xE37D:'MusicEnvelopeState.Phase',0xE302:'MusicEnvelopeState.SlideStep',0xE309:'MusicEnvelopeState.SlideReload',0xDF6B:'MusicEnvelopeState.SlideGate'}


def name_operands(region,address,operation):
 if region=='Music' and address in FUNCTIONS:
  return re.sub(r'#([0-9A-F]{4})',lambda m:'@'+TARGETS[int(m[1],16)] if int(m[1],16) in TARGETS else m[0],operation)
 return operation
