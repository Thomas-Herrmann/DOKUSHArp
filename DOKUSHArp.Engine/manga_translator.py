from manga_ocr import MangaOcr
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from gpt_translator import GptTranslator
import textwrap
import numpy as np
import cv2
import math


class Translator:
    model: YOLO
    ocr : MangaOcr
    gpt_translator : GptTranslator
    font_path : str

    def __init__(self, contour_yolo_model_path, font_path):
        self.model = YOLO(contour_yolo_model_path)
        self.ocr = MangaOcr()
        self.gpt_translator = GptTranslator()
        self.font_path = font_path

    def process(self, image):
        bounding_boxes = self.model(image)[0].boxes.data.tolist()
        source_text_list = []
        text_bubble_contours = []

        for bounding_box in bounding_boxes:
            x1, y1, x2, y2, _, _ = bounding_box
            cropped_pixels = image[int(y1):int(y2), int(x1):int(x2)]
            cropped_image = Image.fromarray(np.uint8(cropped_pixels * 255))
            source_text_list.append(self.ocr(cropped_image))
            text_bubble_contours.append(self.__remove_existing_text(cropped_pixels))

        translations = self.gpt_translator.translate(source_text_list)

        im_height, im_width, _ = image.shape
        proposed_line_height = max(im_height, im_width) * 0.01591089896

        for index, bounding_box in enumerate(bounding_boxes):
            x1, y1, x2, y2, _, _ = bounding_box
            cropped_pixels = image[int(y1):int(y2), int(x1):int(x2)]
            self.__add_new_text(cropped_pixels, text_bubble_contours[index], translations[index], proposed_line_height)

        return image, [Translator.__offset_bounding_box(cv2.boundingRect(contour), bounding_boxes[index]) for index, contour in enumerate(text_bubble_contours)]
    
    def __offset_bounding_box(target_box, offset_box):
        offset_x, offset_y, _, _, _, _ = offset_box
        
        return (target_box[0] + offset_x, target_box[1] + offset_y, target_box[2], target_box[3])

    def __remove_existing_text(self, cropped_pixels):
        gray = cv2.cvtColor(cropped_pixels, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(gray)

        cv2.drawContours(mask, [largest_contour], -1, 255, cv2.FILLED)

        cropped_pixels[mask == 255] = (255, 255, 255)

        return largest_contour

    def __map_contour_to_contained_rect(contour):
         x, y, w, h = cv2.boundingRect(contour)
         cx, cy = (x + w // 2, y + h // 2)
         rw = (w // 2) * math.sqrt(2)
         rh = (h // 2) * math.sqrt(2)

         return (int(cx - rw // 2), int(cy - rh // 2), int(rw), int(rh))


    def __add_new_text(self, cropped_pixels, text_bubble_contour, translated_text, proposed_line_height):
        x, y, w, h = Translator.__map_contour_to_contained_rect(text_bubble_contour)
        pil_image = Image.fromarray(cv2.cvtColor(cropped_pixels, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        wrapped_text, font_size, line_height = self.__fit_text(w, h, proposed_line_height, translated_text, draw)

        font = ImageFont.truetype(self.font_path, size=font_size)
        text_y = y + (h - len(wrapped_text) * line_height) // 2
        
        for line in wrapped_text:
            text_length = draw.textlength(line, font=font)
            text_x = x + (w - text_length) // 2
            
            draw.text((text_x, text_y), line, font=font, fill=(0, 0, 0))

            text_y += line_height

        cropped_pixels[:, :, :] = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def __fit_text(self, w, h, proposed_line_height, text, image_draw : ImageDraw):
        line_height = proposed_line_height
        font_size_factor = 0.875
        wrapped_text = []

        while True:
            num_lines = 1

            while num_lines * line_height <= h:
                num_characters_per_line = math.ceil(len(text) // num_lines)

                if num_characters_per_line <= 0:
                    return text, line_height * font_size_factor, line_height

                wrapped_text = textwrap.wrap(text, num_characters_per_line, break_long_words=False)
                font = ImageFont.truetype(self.font_path, size=line_height * font_size_factor)

                if (all([image_draw.textlength(line, font) <= w for line in wrapped_text])):
                    return wrapped_text, line_height * font_size_factor, line_height

                num_lines += 1

            line_height *= 0.95
