"""Публикация полной композиции CB23..CEE2 с девятью существующими выходными операндами."""
from ClassifyActionRegionType import main
import ActionRenderMatrixFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionRenderMatrix', 'ActionRenderMatrix', tuple(
        ('Coeff' + str(row + 1) + str(column + 1), facts.OUTPUTS[row][column], 'непосредственный байт LD A,n следующего преобразования')
        for row in range(3) for column in range(3)))
