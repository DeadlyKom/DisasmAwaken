"""Публикация двух исходных байтов перед общим умножением E869."""

from ClassifyD3DFragments import apply
import PreviewSquareEntryFacts as facts


if __name__ == '__main__':
    apply(facts, 'PreviewSquareEntry', 'Source/Resources/06_D3D/BeforeFaceProduct.bin', (
        (0x2867, 0x2869, 0xE867, 'Source/D3D/SquarePreviewSignedWord.asm'),
    ), 'PreviewSquareEntryVerification')
