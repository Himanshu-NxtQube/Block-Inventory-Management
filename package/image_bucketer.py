import cv2
import os


class ImageBucketer:
    def __init__(self, base_bucket_dir="bucket"):
        os.makedirs(base_bucket_dir, exist_ok=True)
        self.base_bucket_dir = base_bucket_dir
        self.buckets = {
            # 'non_confirmity': os.path.join(base_bucket_dir, 'non confirmity'),
            'sticker_not_found': os.path.join(base_bucket_dir, 'sticker not found'),
            'sticker_decoding_error': os.path.join(base_bucket_dir, 'sticker decoding error'),
            'wrong_unique_id': os.path.join(base_bucket_dir, 'wrong unique id'),
            'dump_data_missing': os.path.join(base_bucket_dir, 'dump data missing'),
            'multiple_stickers': os.path.join(base_bucket_dir, 'multiple stickers'),
            'box_not_found': os.path.join(base_bucket_dir, 'box not found'),
            'part_number_missing_in_block_csv': os.path.join(base_bucket_dir, 'part number missing in block csv')
        }
        
        for bucket_path in self.buckets.values():
            os.makedirs(bucket_path, exist_ok=True)
    
    def save_to_bucket(self, bucket_name, image, image_name):
        cv2.imwrite(os.path.join(self.buckets[bucket_name], image_name), image)
    
    def categorize_and_bucket(self, image, image_name, matching_unique_id, record, stack_count, sticker_count):
        # if not matching_unique_id:
        #     self.save_to_bucket('non_confirmity', image, image_name)
        
        if matching_unique_id and not record:
            self.save_to_bucket('wrong_unique_id', image, image_name)
    
        if sticker_count == 0:
            self.save_to_bucket('sticker_not_found', image, image_name)
        elif sticker_count > 1:
            self.save_to_bucket('multiple_stickers', image, image_name)

        if sticker_count > 0 and not record:
            self.save_to_bucket('sticker_decoding_error', image, image_name)

        if stack_count == -1:
            self.save_to_bucket('box_not_found', image, image_name)
        elif stack_count == -2:
            self.save_to_bucket('dump_data_missing', image, image_name)
        elif stack_count == -3:
            self.save_to_bucket('part_number_missing_in_block_csv', image, image_name)
        
    
    # def get_bucket_path(self, bucket_name):
    #     return self.buckets.get(bucket_name)
