"""Публикация исходных инструкций продолжения 6DD1 без запуска сборки."""
import ActionVisualEffectResumeFacts as facts
from PublishActionRawFunction import main


if __name__ == '__main__':
    main(facts, 'ActionVisualEffectResume', 0x6DD1, 0x6E2B, 8846, proof_tag='ActionVisualEffectTransfer')
