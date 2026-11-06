"""Граница двух полноширинных рисователей после RET D38B."""
from SplitControlsVerticalSlice import main


if __name__ == '__main__':
    main(0xD340, 0xD38C, tag='ControlsFullWidthCircleSplit', proof_name='ControlsFullWidthCircleVerification',
         proof_fields=('all_real_children_without_stubs', 'profiles_from_verified_D236_boundary'),
         previous_address=0xD38B)
