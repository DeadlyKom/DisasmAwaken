"""Публикация 15 исходных байтов перед настоящим последовательным продолжением AE24."""
from PublishActionRawFunction import main
import ActionDeltaRatioFacts as facts


if __name__ == '__main__':
    main(facts, 'ActionDeltaRatio', 0xAE15, 0xAE24, 8192)
