from manga_translator import Translator
import threading
import os
import cv2

class ProcessScheduler:
    __translator: Translator
    __store_path: str
    __lock = threading.Lock()

    def __init__(self, translator: Translator, manga_store_path: str):
        self.__translator = translator
        self.__store_path = manga_store_path

    def get_page(self, id: str, page_index: int):
        original_image = cv2.imread(os.path.join(self.__store_path, id, 'page', f'{page_index}.png'))
        success, translated_image, bounding_boxes = self.__try_get_existing_translation(id, page_index)

        if not success:
             translated_image, bounding_boxes = self.__wait_page(original_image, id, page_index)

        self.__schedule_preprocess(id, page_index + 1, page_index + 6)

        return original_image, translated_image, bounding_boxes

    def __wait_page(self, cv2_image, id: str, page_index: int):
        with ProcessScheduler.__lock:
            success, translated_image, bounding_boxes = self.__try_get_existing_translation(id, page_index)

            if success:
                return translated_image, bounding_boxes

            translated_image, bounding_boxes = self.__translator.process(cv2_image)
            
            cv2.imwrite(os.path.join(self.__store_path, id, 'translated', f'{page_index}.png'), translated_image)

            with open(os.path.join(self.__store_path, id, 'translated', f'{page_index}.txt'), 'w') as write_handle:
                write_handle.write(ProcessScheduler.__encode_bounding_boxes(bounding_boxes))

            return translated_image, bounding_boxes

    def __schedule_preprocess(self, id: str, from_index: int, to_index: int):
        threading.Thread(target=ProcessScheduler.__schedule_internal, args=[self, id, from_index, to_index]).start()

    def __schedule_internal(self, id: str, from_index: int, to_index: int):
        for page_index in range(from_index, to_index):
            success, _, _ = self.__try_get_existing_translation(id, page_index)
    
            if not success:
                original_image = cv2.imread(os.path.join(self.__store_path, id, 'page', f'{page_index}.png'))
                
                self.__wait_page(original_image, id, page_index)

    def __try_get_existing_translation(self, id: str, page_index: int):
        try:
            translated_image = cv2.imread(os.path.join(self.__store_path, id, 'translated', f'{page_index}.png'))
            
            with open(os.path.join(self.__store_path, id, 'translated', f'{page_index}.txt'), 'r') as read_handle:
                bounding_boxes = ProcessScheduler.__parse_bounding_box_str(read_handle.read)

            return True, translated_image, bounding_boxes
        except:
            return False, None, None

    def __parse_bounding_box_str(raw_boxes: str):
        bounding_boxes = []
        
        for line in raw_boxes.strip().split("\n"):
            bounding_boxes.append([float(n) for n in line.split(";")])

        return bounding_boxes
    
    def __encode_bounding_boxes(bounding_boxes):
        return "\n".join(";".join(map(str, box)) for box in bounding_boxes)