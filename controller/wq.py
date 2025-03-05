from flask import request, session, redirect, url_for
from PIL import Image
import numpy as np
import os
import time

class SteganoController:
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png'}  # Hanya mendukung PNG

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in SteganoController.ALLOWED_EXTENSIONS

    @staticmethod
    def hide_message_in_image():
        if request.method == 'POST':
            try:
                if 'image' not in request.files:
                    raise ValueError('No image file uploaded')

                image_file = request.files['image']
                encrypted_message = request.form['encryptedMessage']

                if image_file.filename == '':
                    raise ValueError('No selected file')

                if not SteganoController.allowed_file(image_file.filename):
                    raise ValueError('Invalid file format')

                # Ukuran file asli (dalam KB)
                image_file.seek(0)  # Reset file pointer setelah membaca ukuran
                original_file_size = len(image_file.read()) / 1024  # Convert to KB
                image_file.seek(0)  # Reset file pointer kembali ke awal

                # Load dan proses gambar
                start_time = time.time()  # Mulai waktu encoding
                image = Image.open(image_file)
                image = image.convert('RGB')
                data = np.array(image)

                # Convert pesan ke biner
                binary_message = ''.join(format(ord(i), '08b') for i in encrypted_message)
                if len(binary_message) > data.size:
                    raise ValueError('Message too large for this image')

                # Sembunyikan pesan di LSB
                data_flat = data.flatten()
                for i in range(len(binary_message)):
                    data_flat[i] = (data_flat[i] & ~1) | int(binary_message[i])

                # Reshape dan simpan gambar yang dimodifikasi
                modified_data = data_flat.reshape(data.shape)
                modified_image = Image.fromarray(modified_data.astype(np.uint8))

                # Generate nama file unik
                timestamp = int(time.time())
                filename = f'stegano_image{timestamp}.png'  # Hanya PNG yang digunakan
                filepath = os.path.join(SteganoController.UPLOAD_FOLDER, filename)

                # Simpan gambar dalam format PNG (tanpa kompresi)
                modified_image.save(filepath, format="PNG", compress_level=0)  # Nonaktifkan kompresi

                # Ukuran file gambar yang dimodifikasi (dalam KB)
                modified_file_size = os.path.getsize(filepath) / 1024  # Convert to KB

                # Simpan informasi ke session
                session['modified_image'] = f'/static/uploads/{filename}'
                session['original_file_size'] = round(original_file_size, 2)  # Dibulatkan ke 2 desimal
                session['modified_file_size'] = round(modified_file_size, 2)  # Dibulatkan ke 2 desimal
                session['encoding_time'] = round(time.time() - start_time, 2)  # Waktu encoding dalam detik

                return redirect(url_for('web.index'))

            except Exception as e:
                session['error'] = str(e)
                return redirect(url_for('web.index'))

        return redirect(url_for('web.index'))

    @staticmethod
    def extract_message_from_image():
        if request.method == 'POST':
            try:
                if 'image' not in request.files:
                    raise ValueError('No image file uploaded')

                image_file = request.files['image']
                if image_file.filename == '':
                    raise ValueError('No selected file')

                if not SteganoController.allowed_file(image_file.filename):
                    raise ValueError('Invalid file format')

                # Load dan simpan gambar yang di-upload
                image = Image.open(image_file)
                timestamp = int(time.time())
                uploaded_filename = f'uploaded_image_{timestamp}.png'  # Hanya PNG
                uploaded_filepath = os.path.join(SteganoController.UPLOAD_FOLDER, uploaded_filename)
                image.save(uploaded_filepath, format="PNG", compress_level=0)  # Simpan tanpa kompresi
                session['uploaded_image'] = f'/static/uploads/{uploaded_filename}'

                # Extract pesan dari LSB
                data = np.array(image)
                binary_message = ""
                data_flat = data.flatten()

                # Ekstrak pesan hingga terminator null atau panjang maksimum
                for i in range(min(len(data_flat), 1000 * 8)):  # Maksimal 1000 karakter
                    binary_message += str(data_flat[i] & 1)

                # Convert biner ke teks
                message = ""
                for i in range(0, len(binary_message), 8):
                    if i + 8 <= len(binary_message):
                        byte = binary_message[i:i+8]
                        char = chr(int(byte, 2))
                        if ord(char) < 128:  # Hanya karakter ASCII
                            message += char
                        else:
                            break

                session['extracted_ciphertext'] = message
                return redirect(url_for('web.decryption'))

            except Exception as e:
                session['error'] = str(e)
                return redirect(url_for('web.decryption'))

        return redirect(url_for('web.decryption'))
