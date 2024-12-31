import os
import flask
import hashlib
from flask import request, jsonify, send_file, abort
from epub_service import instantiate_book, instantiate_book_meta, get_manga_record
from shutil import rmtree
from process_scheduler import ProcessScheduler
from manga_translator import Translator
import base64
import cv2

app = flask.Flask(__name__)
manga_store_path = os.path.join(os.environ['APPDATA'], 'DOKUSHArp', 'manga')

@app.route('/manga/<id>/page/<int:pagenumber>', methods=['GET'])
def get_page(id, pagenumber):
    original_image, translated_image, bounding_boxes = process_scheduler.get_page(id, pagenumber)
    _, original_buffer = cv2.imencode(".png", original_image)
    _, translated_buffer = cv2.imencode(".png", translated_image)

    return jsonify({'originalImage': base64.b64encode(original_buffer.tobytes()).decode("utf-8"), 
                    'translatedImage': base64.b64encode(translated_buffer.tobytes()).decode("utf-8"), 
                    'boundingBoxes': bounding_boxes})

@app.route('/mangas', methods=['GET'])
def get_mangas():
    return [get_manga_record(dir.path) for dir in os.scandir(manga_store_path)]

@app.route('/cover/<id>')
def get_cover(id):
    try:
        return send_file(os.path.join(manga_store_path, id, 'page', '0.png'), mimetype='image/png')
    except FileNotFoundError:
        abort(404, description='Cover not found')

@app.route('/upload_begin', methods=['POST'])
def upload_begin():
    title = request.args.get('title')
    cover_page_count = request.args.get('coverPageCount')
    manga_id = request.args.get('id')

    if not title:
        return jsonify({'error': 'Missing required query parameter: title'}), 400
    
    if not cover_page_count:
        return jsonify({'error': 'Missing required query parameter: coverPageCount'}), 400

    if not manga_id:
        return jsonify({'error': 'Missing required query parameter: id'}), 400

    try:
        cover_page_count = int(cover_page_count)
    except ValueError:
        return jsonify({'error': 'coverPageCount must be an integer'}), 400

    manga_directory_path = os.path.join(manga_store_path, f'{manga_id}')

    os.makedirs(manga_directory_path, exist_ok=False)

    with open(os.path.join(manga_directory_path, 'hash'), 'wb') as hash_file:
        hash_file.write(request.data)

    with open(os.path.join(manga_directory_path, 'source.epub'), 'wb'):
        pass

    instantiate_book_meta(manga_directory_path, cover_page_count, title)

    return jsonify({
                'message': 'File upload begun successfully',
                'title': title,
                'id': manga_id,
                'coverPageCount': cover_page_count}), 200

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    manga_id = request.args.get('id')

    if not manga_id:
        return jsonify({'error': 'Missing required query parameter: id'}), 400

    with open(os.path.join(manga_store_path, f'{manga_id}/source.epub'), 'ab') as file_handle:
        file_handle.write(request.data)

    return jsonify({
                'message': 'File chunk appended successfully',
                'id': manga_id}), 200

@app.route('/upload_end', methods=['POST'])
def upload_end():
    manga_id = request.args.get('id')

    if not manga_id:
        return jsonify({'error': 'Missing required query parameter: id'}), 400
    
    manga_directory_path = os.path.join(manga_store_path, f'{manga_id}')
    file_path = os.path.join(manga_directory_path, f'source.epub')
    
    with open(file_path, 'rb') as read_handle:
        actual_hash = hashlib.md5(read_handle.read()).digest()

    with open(os.path.join(manga_directory_path, 'hash'), 'rb') as read_handle:
        expected_hash = read_handle.read()

    if actual_hash != expected_hash:
        rmtree(manga_directory_path)

        return jsonify({'error': 'Actual file hash differs from expected file hash: id'}), 400
    
    instantiate_book(file_path, manga_directory_path)

    return jsonify({
                'message': 'File uploaded successfully',
                'id': manga_id}), 200


if __name__ == '__main__':
    os.makedirs(manga_store_path, exist_ok=True)

    process_scheduler = ProcessScheduler(Translator("model.pt", "font.ttf"), manga_store_path)
    port = int(os.environ.get('PORT', 8111))

    app.run(host='0.0.0.0', port=port)