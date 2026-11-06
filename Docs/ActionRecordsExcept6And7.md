# Поиск класса вне пары 6 и 7

[FindRecordExcept6And7](../Source/Action/FindRecordExcept6And7.asm), E70D..E728,
возвращает индекс первого активного класса, отличного от 6 и 7.
[Общий алгоритм, контракты, точный R и проверка](ActionFilteredRecords.md).
Найденный класс FF возвращает Z после INC E, эта особенность сохранена.
