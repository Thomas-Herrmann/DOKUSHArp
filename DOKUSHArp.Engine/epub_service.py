import ebooklib.epub
from ebooklib import epub
import cv2
from PIL import Image
from io import BytesIO
import numpy as np
from os import makedirs
import os

def instantiate_book_meta(epub_directory_path : str, num_cover_pages: int, title: str):
    if num_cover_pages < 0:
        raise ValueError("Number of cover pages must be non-negative")
    
    formatted_title = title.replace("\"", "\\\"")

    with open(os.path.join(epub_directory_path, "meta.txt"), "w") as write_handle:
        write_handle.write(f'"{formatted_title}"\n"{num_cover_pages}"')
    

def instantiate_book(epub_path: str, epub_directory_path : str):
    file = epub.read_epub(epub_path)
    page_directory_path = os.path.join(epub_directory_path, "page")
    page_index = 0

    makedirs(page_directory_path, exist_ok=False)
    makedirs(os.path.join(epub_directory_path, "translated"), exist_ok=False)

    for image in file.get_items_of_type(ebooklib.ITEM_IMAGE):
        pil_image = Image.open(BytesIO(image.content))
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        cv2.imwrite(os.path.join(page_directory_path, f"{page_index}.png"), cv_image)
        
        page_index += 1

def get_manga_record(epub_directory_path: str):
    with open(os.path.join(epub_directory_path, "meta.txt"), "r") as read_handle:
        return {
            'id': os.path.split(epub_directory_path)[1], 
            'title': read_handle.readline()[1:-1].replace("\\\"", "\""), 
            'numCoverPages': int(read_handle.readline()[1:-1])}