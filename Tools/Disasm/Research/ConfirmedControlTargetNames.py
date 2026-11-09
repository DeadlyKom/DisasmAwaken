"""Только шесть переходов к существующим доказанным меткам."""
TARGETS={('D3D', 60456): {61166: 'D3D.RestorePreviewStack.Entry'}, ('D3D', 60964): {61166: 'D3D.RestorePreviewStack.Entry'}, ('Voxel', 63977): {63993: 'Voxel.ProjectEffectPoint.ShiftVertical', 64028: 'Voxel.ProjectEffectPoint.ShiftHorizontal'}}

def name_operands(region,function_address,operation):
    if not operation.startswith(("JP ","JR ")):return operation
    for address,name in TARGETS.get((region,function_address),{}).items():operation=operation.replace("#"+format(address,"04X"),"@"+name)
    return operation
