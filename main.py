from package.config_loader import set_config, get_config
from package.annotations_parser import AnnotationsParser
from package.data_retriever import RDSDataFetcher
from package.rds_operator import RDSOperator
from package.json_result import build_result
from package.google_ocr import OCRClient
from package.check import is_location
from package.box_utilities import BoxUtilities
from package.image_bucketer import ImageBucketer
from dotenv import load_dotenv
import pymysql
import json
import sys
import cv2
import os

user_id = sys.argv[1]
debug = True if len(sys.argv) > 1 and sys.argv[2] == 'debug' else False
if debug:
    print('Debugging enabled!')
set_config(user_id)
CONFIG = get_config()

load_dotenv('package/.env')

ocr_client = OCRClient()
parser = AnnotationsParser()
data_fetcher = RDSDataFetcher()
rds_operator = RDSOperator()
box_util = BoxUtilities()
bucketer = ImageBucketer()

conn = pymysql.connect(
    host=os.getenv("rds_host"),  # RDS Endpoint
    user=os.getenv("rds_user"),                    # DB username
    password=os.getenv("rds_password"),                # DB password
    database=os.getenv("rds_dbname"),           # Target DB name
    port=int(os.getenv("rds_port", 3306))                                # Default MySQL port
)

curr_location = None

def process_single_image(image_path, report_id):
    global curr_location
    image_name = image_path.split('/')[-1]
    print("Processing: ", image_name)
    image_obj_key_id = rds_operator.store_img_info(image_path, conn)

    #matching_unique_ids = set()
    nearest_box = None
    matching_unique_id = None
    image = cv2.imread(image_path)
    rotation = 0

    annotations = ocr_client.get_annotations(image.copy())
    if is_location(annotations):
        curr_location = parser.get_location(annotations)
        print(f"{curr_location=}")
        return

    while not matching_unique_id and rotation < 360:
        annotated_img = image.copy()
        nearest_box = box_util.get_nearest_box(image_path, annotated_img, rotation, debug)
        if nearest_box is not None:
            cropped_img = box_util.crop_rotated_box(image_path, image.copy(), nearest_box)
            annotations = ocr_client.get_annotations(cropped_img)
        else:
            annotations = None
            print("Alert: No box detected!")

        unique_ids = parser.get_unique_ids(annotations)
        print(unique_ids)
        # matching_unique_id = box_util.find_unique_id(unique_ids, nearest_box)
        matching_unique_id = unique_ids[0][0] if unique_ids else None
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        rotation += 90

    print(rotation - 90, matching_unique_id)
    
    record = data_fetcher.fetch_record(matching_unique_id, user_id)

    area = box_util.calculate_area(nearest_box) if nearest_box is not None else None
    stack_count = box_util.get_stack_count(record, area)
    sticker_count = box_util.check_unique_id_count(annotated_img, nearest_box, image_path)

    bucketer.categorize_and_bucket(annotated_img, image_name, matching_unique_id, record, stack_count, sticker_count)
    
    result = build_result(image_name, record, stack_count, curr_location, sticker_count)
    print(json.dumps(result, indent=4))

    rds_operator.store_data_to_RDS(conn, result, image_obj_key_id, user_id, report_id)



if __name__ == "__main__":
    image_dir = CONFIG['input']['image_dir']
    images = sorted(os.listdir(image_dir))
    report_id = 0
    report_id = rds_operator.create_report(conn, user_id, report_name='testing_block_07')
    
    for image in images:
        # if int(image[5:8]) < 871:
        #     continue
        full_image_path = os.path.join(image_dir, image)
        process_single_image(full_image_path, report_id)
