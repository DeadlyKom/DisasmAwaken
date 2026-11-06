"""Границы двухвходового горизонтального рисователя D3DA..D403."""
from SplitControlsVerticalSlice import main


if __name__ == '__main__':
    proof = 'ControlsHorizontalCircleVerification'
    fields = ('two_real_preparations_and_halves', 'upward_half_tail_jump')
    main(0xD340, 0xD3DA, tag='ControlsHorizontalCircleStartSplit', proof_name=proof,
         proof_fields=fields, previous_instruction='RET', previous_address=0xD3D9)
    main(0xD3DA, 0xD404, tag='ControlsHorizontalCircleEndSplit', proof_name=proof,
         proof_fields=fields, previous_instruction='JP @Controls.DrawLeftClippedHalfUp.Entry', previous_address=0xD401)
