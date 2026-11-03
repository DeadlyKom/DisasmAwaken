"""Три обмена полных слов изменяемого кода, игровой смысл пар пока неизвестен."""
FUNCTIONS={0xAD1D:('SwapCodePatchWords','Обмен трёх пар полных слов изменяемого кода, включая байты операндов и следующие префиксы')}
PAIRS=((0xCB8B,0xCB54),(0xCBD8,0xCB6F),(0xCBEE,0xCBBC))
CONTRACTS={('Action',0xAD1D):(
 ['HL, DE, BC и AF числовых аргументов не задают',
  'шесть слов ActionPatchSwapState доступны для чтения и записи в окне банка 0',
  'код AD1D находится в общей RAM банка 2, на CPU-стеке внешний возврат, IRQ и потребитель изменяемого кода не вмешиваются'],
 ['HL содержит прежнее слово Pair2A, DE прежнее слово Pair2B, BC и AF сохраняются',
  "HL', DE', BC', AF', IX, IY, I, IM и IFF сохраняются, SP=входной SP+2",
  'слова Pair0A/Pair0B, Pair1A/Pair1B и Pair2A/Pair2B обменены полностью, всего двенадцать байтов RAM записаны ровно по разу',
  'R увеличивается на 19 M1, CPU-стек и порты не записываются, регистр 7FFD сохраняется'],
 ['HL, DE, R, шесть слов изменяемого кода'],
 ['в исходном состоянии младшие байты слов являются операндами LD A,n, старшие захватывают следующие префиксы CB',
  'все шестнадцать битов обмениваются без маски, обмен только младших коэффициентов исходным инструкциям не равнозначен',
  'два вызова без вмешательства между ними восстанавливают двенадцать исходных байтов',
  'в TransformVectorTransposed эти три перестановки транспонируют матрицу ComputePatchedVector, полный игровой смысл матрицы не доказан'])}
COMMENTS={}
for address,index in ((0xAD1D,0),(0xAD2B,1),(0xAD39,2)):
    COMMENTS[address]=(['-----------------------------------------','Обмен полной пары '+str(index),
        'Чтение двух исходных слов перед записью, каждый старший байт также переносится.'],None)
    COMMENTS[address+7]=(['Обновление обеих сторон исходной пары, операнд и следующий байт не разделяются.'],None)


def name_operands(region,function_address,operation):
    if region=='Action' and function_address==0xAD1D:
        for index,pair in enumerate(PAIRS):
            for side,address in zip(('A','B'),pair):
                operation=operation.replace('(#'+format(address,'04X')+')','(@ActionPatchSwapState.Pair'+str(index)+side+')')
    return operation
