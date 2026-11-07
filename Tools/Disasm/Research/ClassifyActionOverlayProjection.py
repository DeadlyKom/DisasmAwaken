"""Публикация исходных 80 байтов ADC5, соседние 15 байтов остаются явно неизвестными."""
from PublishActionRawFunction import main
import ActionOverlayProjectionFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionOverlayProjection', 0xADC5, 0xAE15, 8192, allow_subrange=True)
