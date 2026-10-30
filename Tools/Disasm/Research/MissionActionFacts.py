"""Действие элемента миссии и ветвь расторжения на общей сохранённой рамке."""
from MissionActionNotes import COMMENTS
FUNCTIONS={0x6E9C:('ProcessMissionAction','Проверка селектора и строки, принятие либо расторжение миссии с общей перерисовкой'),
 0x6F5D:('CancelMission','Расторжение миссии на сохранённом кадре, пересчёт загрузки и денежный штраф')}
DOCUMENTS={('Station',address):('MissionAction','условия принятия, старшие байты отмены и общий стековый хвост') for address in FUNCTIONS}
LABELS={('Station',0x6EA9):'SaveContext',('Station',0x6ED6):'TestActive',('Station',0x6F14):'FinishAction',
 ('Station',0x6F34):'WarnTonnage',('Station',0x6F73):'RecomputeLoad',('Station',0x6F94):'PrintCancelled',
 ('Station',0x6FA5):'ClearQuantity',('Station',0x6FAC):'ClearCredits'}
COMMON_OUT=[
 'общий хвост вызывает BeginScreenUpdate, DrawItem31, DrawItem32, DrawItem00 и EndScreenUpdate',
 'HL, DE, B, IX и IY восстановлены из FMissionActionFrame перед CloseMenuOnRow',
 'C равен PointerY SHR 3, A=FF, F от CloseMenuOnRow, MissionHoverState.Row=FF',
 'при совпадении строк CloseMenuOnRow удаляет выбранный элемент через DropItemDraw, иначе список не меняется этим вызовом',
 "HL', DE', BC', AF' не восстанавливаются общим кадром и соответствуют вложенным игровым и графическим вызовам",
 'конечная страница 10, блокировка указателя снята EndScreenUpdate, I и IFF собственным кодом не меняются']
CONTRACTS={('Station',0x6E9C):(
 ['HL - запасная обёртка, DE - выбранный индекс, BC - контекст по RepaintAndFlag',
  'AF - A исходный селектор, действуют договоры RepaintAndFlag, callback и интерактивной геометрии',
  'для собственного действия выполнены договоры DrawItem31, DrawItem32, DrawItem00 и экранного обновления',
  'Row хранится в исходном операнде 6F54, текущий ключ и MissionOffer доступны',
  'для предупреждения и отмены GenerateMissionOffer завершает поиск ненулевого ROM-тоннажа, LANG доступен в банке 6',
  'стек вне экранов и банкового окна, HALT пробуждается с сохранением контекста'],
 ['при Carry после RepaintAndFlag немедленный возврат с его регистровыми результатами',
  'при возвращённом A не равном 1 только DEC A и CloseMenuOnRow, результат по его договору',
  'при возвращённом A=1 сохраняет шесть пар в FMissionActionFrame, дальнейшее восстановление относится к этому моменту',
  'при Row не равном 1 или совпавших ключах пропускает собственное принятие и отмену, но выполняет общий хвост',
  'при Row=1 и разных ключах ActiveCode=1 ведёт в CancelMission на этом же кадре',
  'при прочих кодах ActiveCode сравнивает вместимость с младшим байтом суммы используемого и требуемого тоннажа',
  'успех пишет ActiveCode=1, CompletionCode=0, байтовые суммы в 9852 и 9850, значение 0A в 9853',
  'отказ печатает предупреждение, ждёт два HALT, заменяет предложение генератором и выполняет общий хвост',
  *COMMON_OUT,
  'SP обычного возврата равен входному SP+2 при выполнении договоров вызываемых обработчиков'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY по RepaintAndFlag, собственный кадр сохраняет шесть пар"],
 ['собственный FinishAction требует кадр от SaveContext, обычный CALL к этому хвосту недопустим',
  'на ветви принятия сравнивается обёрнутая байтовая сумма, перенос выше 255 не вызывает отдельного отказа',
  'пропуск собственного изменения не запрещает завершение миссии в DrawItem32 при уже достигнутой цели',
  'результаты дочернего DrawItem32 могут включать деньги, новое предложение и сценарий, это часть общего хвоста',
  'полная модель включает RepaintAndFlag при последнем обработчике списка и без интерактивного действия',
  'модель не исполняет IRQ и не подтверждает аппаратный ввод, ROM Unreal или нативное прохождение']),
 ('Station',0x6F5D):(
 ['HL - H старший байт разности слов ключей, DE - D старший байт слова предлагаемого ключа',
  '9852 содержит байтовое количество, RequiredTonnage байтовое требование, их запись заменит только L и E',
  'SP у SavedIY готового FMissionActionFrame, ниже сохранены IX, AF, BC, HL, DE и исходный возврат',
  'действуют договоры LANG, GenerateMissionOffer, DrawItem00 и общего FinishAction родительской процедуры'],
 ['ActiveCode=0, количество 9852 обнулено при полном займе изменённых HL-DE, иначе получает младший байт разности',
  'выполнен исходный LANG с событием 11, оба T пересчитали используемый тоннаж 9850',
  'денежное слово 984E получает max(прежние деньги-1000,0)',
  'выведено сообщение отмены, выполнены два HALT, новое предложение и дополнительный DrawItem00',
  *COMMON_OUT,
  'SP после исходного возврата равен входному SP+14, двенадцать байтов сохранений и два байта PC сняты'],
 ["HL, DE, BC, AF, HL', DE', BC', AF', IX, IY до восстановления из FMissionActionFrame"],
 ['это продолжение через JP, собственного кадра CALL и собственных POP до FinishAction нет',
  'снятие количества не является насыщенным байтовым вычитанием, H и D участвуют в проверке полного займа',
  'при H больше D младший заём может дать обёрнутый результат, при H меньше D возможно обнуление достаточного количества',
  'CompletionCode сама ветвь не меняет, генератор изменяет только свои доказанные поля состояния предложения',
  'смысл старших байтов требования не выдумывается, только младший участвует в замене E',
  'модель полного действия проверяет настоящий LANG, рисователи и обе ветви CloseMenuOnRow'])}


def name_operands(region,address,operation):
 if region=='Station' and address in FUNCTIONS:
  for raw,name in ((0x6F54,'MissionHoverState.Row'),(0x99A3,'MissionState.ActiveCode'),(0x99A4,'MissionState.CompletionCode'),
   (0x983F,'SignatureInput.Entry.FirstWord'),(0x9841,'SignatureInput.Entry.SecondWord'),
   (0x98B0,'MissionOffer.Entry.FirstWord'),(0x98B2,'MissionOffer.Entry.SecondWord'),(0x98BE,'MissionOffer.Entry.RequiredTonnage')):
   operation=operation.replace('(#'+format(raw,'04X')+')','(@'+name+')')
 return operation
