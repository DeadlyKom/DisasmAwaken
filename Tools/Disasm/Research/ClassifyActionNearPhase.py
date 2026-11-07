"""Три физических входа, каждый сохраняется в отдельном исходнике."""
from PublishActionRawFunction import main
import ActionNearPhaseFacts as core
import ActionPhaseNearStateFacts as phase
import ActionLinkedNearStateFacts as linked

if __name__=='__main__':
    main(core,'ActionNearPhase',0xF087,0xF0BE,75008,allow_subrange=True)
    main(phase,'ActionPhaseNearState',0xF07C,0xF081,75008,allow_subrange=True,proof_tag='ActionNearPhase')
    main(linked,'ActionLinkedNearState',0xF081,0xF087,75008,allow_subrange=True,proof_tag='ActionNearPhase')
