from datetime import datetime
import os
from package.s3_operator import upload_images

class RDSOperator:
    def create_report(self, conn, user_id, operator_name='test', report_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        with conn.cursor() as cursor:
            # Generate timestamp-based report name
            # report_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_image_captured = datetime.now().date()

            # Insert the new report
            insert_query = """
            INSERT INTO `block-reports` (userId, report_name, operator_name, date_image_captured)
            VALUES (%s, %s, %s, %s)
            """
            values = (user_id, report_name, operator_name, date_image_captured)
            cursor.execute(insert_query, values)
            conn.commit()

            # Fetch the full inserted row
            report_id = cursor.lastrowid

            return report_id
        
    def store_img_info(self, image_path, conn):
        s3_key, s3_url = upload_images(image_path)
        image_name = os.path.basename(image_path)

        with conn.cursor() as cursor:
            try:
                insert_query = "INSERT INTO `image-obj-keys` (originalName, s3Key, s3Url) VALUES (%s, %s, %s)"
                values = (image_name, s3_key, s3_url)  # match the number of columns
                cursor.execute(insert_query, values)
                conn.commit()
                image_obj_key_id = cursor.lastrowid
                # print(f"{image_obj_key_id = }")
                # print(f"{s3_key = }")
                # print(f"{s3_url = }\n")
                # print("Insert successful to image-obj-keys.")
                return image_obj_key_id
            except:
                print("Insert unsuccessful to image-obj-keys.")
        
        
    def store_data_to_RDS(self, conn, result, image_obj_key_id, user_id, report_id):
        for row in result:
            try:
                with conn.cursor() as cursor:
                    # --- Check for existing record ---
                    if row['UNIQUE_ID'] == None or row['UNIQUE_ID'] == "":
                        check_query = """
                        SELECT id FROM blockinferances
                        WHERE uniqueId = %s AND userId = %s AND barcode_number = %s
                        """
                        check_values = (row['UNIQUE_ID'], user_id, row['BARCODE_ID'])  # userId is hardcoded to 3

                        cursor.execute(check_query, check_values)
                        existing = cursor.fetchone()
                    else:
                        existing = False

                    # is_non_conformity = True if row['EXCLUSION'][:5] == "There" else False
                    is_non_conformity = row['EXCLUSION'] not in ("empty rack", "")
                    status = None if 'STATUS' not in row.keys() else 'filled' if row['STATUS'] == 'full' else row['STATUS']

                    if existing:
                        # --- Update existing record ---
                        update_query = """
                        UPDATE blockinferances
                        SET
                            image_name = %s, block_location = %s, box_number = %s, invoice_number = %s,
                            box_quantity = %s, part_number = %s, exclusion = %s, status = %s, stack_count = %s,
                            is_non_conformity = %s, isDispatched = %s, isDeleted = %s,
                            isReplishment = %s, reportId = %s, imageObjKeyId = %s
                        WHERE id = %s
                        """
                        update_values = (
                            row['IMG_ID'], 
                            row['BLOCK_LOCATION'] if not row['BLOCK_LOCATION'] else "", 
                            row['BOXNUMBER'] if not row['BOXNUMBER'] else "", 
                            row['INVOICE_NUMBER'] if not row['INVOICE_NUMBER'] else "",
                            row['BOXQUANTITY'] if not row['BOXQUANTITY'] else "", 
                            row['PARTNUMBER'] if not row['PARTNUMBER'] else "", 
                            row['EXCLUSION'], 
                            status,
                            row['STACKCOUNT'],
                            is_non_conformity, 
                            False, 
                            False, 
                            False, 
                            report_id, 
                            image_obj_key_id, 
                            existing[0]
                        )
                        cursor.execute(update_query, update_values)
                        print(f"Updated record with id = {existing[0]}")
                    else:
                        # --- Insert new record ---
                        insert_query = """
                        INSERT INTO blockinferances (
                            uniqueId, barcode_number, image_name, block_location, box_number,
                            invoice_number, box_quantity, part_number, exclusion, status, stack_count,
                            is_non_conformity, isDispatched, isDeleted, isReplishment,
                            reportId, imageObjKeyId, userId
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s
                        )
                        """
                        insert_values = (
                            row['UNIQUE_ID'] if row['UNIQUE_ID'] else "", 
                            row['BARCODE_ID'] if row['BARCODE_ID'] else "", 
                            row['IMG_ID'],
                            row['BLOCK_LOCATION'] if row['BLOCK_LOCATION'] else "", 
                            row['BOXNUMBER'] if row['BOXNUMBER'] else "", 
                            row['INVOICE_NUMBER'] if row['INVOICE_NUMBER'] else "",
                            row['BOXQUANTITY'] if row['BOXQUANTITY'] else "", 
                            row['PARTNUMBER'] if row['PARTNUMBER'] else "",
                            row['EXCLUSION'], 
                            status,
                            row['STACKCOUNT'],
                            is_non_conformity, 
                            False, 
                            False, 
                            False,
                            report_id, 
                            image_obj_key_id, 
                            user_id
                        )
                        cursor.execute(insert_query, insert_values)
                        print("Inserted new record.")

                    conn.commit()

            except Exception as e:
                print("Insert/Update unsuccessful:", e)

        # for i in range(len(final_output)):
        #     try:
        #         with conn.cursor() as cursor:
        #             # --- Insert Query ---
        #             query = """
        #             INSERT INTO inferances (
        #                 uniqueId, barcode_number, image_name, rack_id, box_number,
        #                 invoice_number, box_quantity, part_number, exclusion, status,
        #                 is_non_conformity, isDispatched, isDeleted, isReplishment,
        #                 reportId, imageObjKeyId, userId
        #             ) VALUES (
        #                 %s, %s, %s, %s, %s,
        #                 %s, %s, %s, %s, %s,
        #                 %s, %s, %s, %s,
        #                 %s, %s, %s
        #             )
        #             """
        #             if final_output[i]['EXCLUSION'] != "":
        #                 is_non_conformity = True
        #             else:
        #                 is_non_conformity = False
        #             # --- Values to Insert ---
        #             values = (
        #                 final_output[i]['UNIQUE_ID'],            # uniqueId
        #                 final_output[i]['BARCODE_ID'],         # barcode_number
        #                 final_output[i]['IMG_ID'],        # image_name
        #                 final_output[i]['RACK_ID'],           # rack_id
        #                 final_output[i]['BOXNUMBER'],              # box_number
        #                 final_output[i]['INVOICE_NUMBER'],            # invoice_number
        #                 final_output[i]['BOXQUANTITY'],                  # box_quantity
        #                 final_output[i]['PARTNUMBER'],             # part_number
        #                 final_output[i]['EXCLUSION'],                # exclusion
        #                 final_output[i]['STATUS'],              # status ('empty', 'partial', 'filled')
        #                 is_non_conformity,                 # is_non_conformity
        #                 False,                 # isDispatched
        #                 False,                 # isDeleted
        #                 False,                 # isReplishment
        #                 report_id,                     # reportId (integer) # to be removed
        #                 s3_key,                     # imageObjKeyId (integer or None)
        #                 user_id                      # userId (integer)
        #             )

        #             # --- Execute and Commit ---
        #             cursor.execute(query, values)
        #             conn.commit()
        #             print("Insert successful.")
        #     except:
        #         print("Insert unsuccessful")
            

            
        

            
'''
userId, 

report_name,

operator_name,

date_image_captured,

rack_number
'''