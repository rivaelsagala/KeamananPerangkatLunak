from flask import render_template, request, session, redirect, url_for
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import time

class CriptoController:

    @staticmethod
    def encrypt_message():
        if request.method == 'POST':
            session.pop('encrypted_message', None)
            session.pop('plaintext_length', None)  # Reset panjang plaintext
            session.pop('encoding_time', None)  # Reset waktu enkripsi

            message = request.form['message']
            key = request.form['key']

            start_time = time.time()  # Mulai penghitungan waktu
            encrypted_message = CriptoController.aes_encrypt(message, key)
            encoding_time = time.time() - start_time  # Hitung waktu enkripsi

            # Hitung panjang plaintext dan simpan di session
            session['plaintext_length'] = len(message)
            session['encrypted_message'] = encrypted_message
            session['encoding_time'] = round(encoding_time, 2)  # Simpan waktu enkripsi

            return redirect(url_for('web.index'))

        return redirect(url_for('web.index'))

    @staticmethod
    def aes_encrypt(message: str, key: str) -> str:
        # Memastikan panjang kunci adalah 16 byte
        key = key.ljust(16)[:16].encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + ':' + ct

    @staticmethod
    def decrypt_message():
        if request.method == 'POST':
            session.pop('decrypted_message', None)
            session.pop('decoding_time', None)  # Reset waktu dekripsi

            # Check if the 'ciphertext' key is present in the form data
            if 'ciphertext' in request.form:
                encrypted_message = request.form['ciphertext']
                key = request.form['key']

                start_time = time.time()  # Mulai penghitungan waktu
                decrypted_message = CriptoController.aes_decrypt(encrypted_message, key)
                decoding_time = time.time() - start_time  # Hitung waktu dekripsi

                session['decrypted_message'] = decrypted_message
                session['decoding_time'] = round(decoding_time, 2)  # Simpan waktu dekripsi

                return redirect(url_for('web.decryption'))

            return redirect(url_for('web.decryption'))

        return redirect(url_for('web.decryption'))

    @staticmethod
    def aes_decrypt(encrypted_message: str, key: str) -> str:
        # Memastikan panjang kunci adalah 16 byte
        key = key.ljust(16)[:16].encode('utf-8')
        iv, ct = encrypted_message.split(':')
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted.decode('utf-8')
