from package.config_loader import get_config
import json

def build_result(image_name, record, stack_count, curr_location, sticker_count):
    final_output = []

    output_template = {
        'IMG_ID':                image_name, 
        'BLOCK_LOCATION':        None,  
        'BARCODE_ID':            None,  
        'UNIQUE_ID':             None,  
        'BOXNUMBER':             None,  
        'BOXQUANTITY':           None,  
        'PARTNUMBER':            None,  
        'INVOICE_NUMBER':        None,  
        'EXCLUSION':             None,  
        'STACKCOUNT':            None
    }

    if not curr_location:
        # output_template['EXCLUSION'] = "No Rack ID found"
        # return output_template
        output_template['EXCLUSION'] = "Block Location hasn't set yet"
    elif not record:
        output_template['EXCLUSION'] = "Sticker not found"
    elif record['part_number'] == '':
        output_template['EXCLUSION'] = "LPN number is not scanned"
    elif sticker_count > 1:
        output_template['EXCLUSION'] = "Multiple stickers detected"
    else:
        output_template['EXCLUSION'] = ""

    # for stack_count, record in zip(stack_counts, records):
    tmp = output_template.copy()
    tmp['IMG_ID'] = image_name
    tmp['BLOCK_LOCATION'] = curr_location if curr_location != None else ""
    
    if record:
        tmp['BARCODE_ID'] = record['barcode_number']
        tmp['UNIQUE_ID'] = record['uniqueId']
        tmp['BOXNUMBER'] = record['box_number']
        tmp['BOXQUANTITY'] = record['box_quantity']
        tmp['PARTNUMBER'] = record['part_number']
        tmp['STACKCOUNT'] = stack_count if stack_count > 0 else None
        tmp['INVOICE_NUMBER'] = record['invoice_number']

    final_output.append(tmp)

    return final_output