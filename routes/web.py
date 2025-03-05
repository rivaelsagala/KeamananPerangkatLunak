from flask import Blueprint
from controller.IndexController import IndexController
from controller.CriptoController import CriptoController
from controller.SteganoController import SteganoController

web = Blueprint('web', __name__)

@web.route('/')
def index():
    return IndexController.index()

@web.route('/decryption')
def decryption():
    return IndexController.decryption()

@web.route('/encrypt', methods=['POST'])
def encrypt_message():
    return CriptoController.encrypt_message()

@web.route('/decrypt', methods=['POST'])
def decrypt_message():
    return CriptoController.decrypt_message()

@web.route('/steganography', methods=['POST'])
def hide_message_in_image():
    return SteganoController.hide_message_in_image()

@web.route('/extract', methods=['POST'])
def extract_message():
    return SteganoController.extract_message_from_image()

@web.route('/restart')
def restart_app():
    return IndexController.restart_program()

