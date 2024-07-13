# -*- coding: utf-8 -*-

import numpy as np
import cv2
import random
import math
import os

# 1. Lena Görüntüsünü Al ve İçine Mesaj Gizle (LSB Yöntemi)

def lsb_embed(image, data):
    binary_data = ''.join([format(ord(i), "08b") for i in data])
    data_len = len(binary_data)
    img_flat = image.flatten()
    
    if data_len > len(img_flat):
        raise ValueError("Veri, görüntüye sığmıyor.")
    
    for i in range(data_len):
        img_flat[i] = (img_flat[i] & ~1) | int(binary_data[i])
    
    stego_image = img_flat.reshape(image.shape)
    return stego_image

def lsb_extract(stego_image, data_len):
    stego_flat = stego_image.flatten()
    binary_data = ''.join([str(stego_flat[i] & 1) for i in range(data_len * 8)])
    
    data = ''.join([chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)])
    return data

# 2. Gizlenen Mesaj olan Stego Görüntüyü Kaydet

def save_image(image, filename):
    cv2.imwrite(filename, image)
    print("Görüntü {} olarak kaydedildi.".format(filename))

# 3. Stego Görüntüyü Mozaik Biçimde Parçalara Ayır ve Kaydet

def split_image(image, parts=4):
    h, w = image.shape[0] // 2, image.shape[1] // 2
    tiles = [image[x:x+h, y:y+w] for x in range(0, image.shape[0], h) for y in range(0, image.shape[1], w)]
    print("Görüntü {} parçaya ayrıldı.".format(len(tiles)))
    return tiles

def save_tiles(tiles, base_filename):
    for i, tile in enumerate(tiles):
        filename = "{}_parca_{}.png".format(base_filename, i+1)
        save_image(tile, filename)

# 4. Anahtar Oluştur ve Parçalara Bölerek Kaydet (Shamir's Secret Sharing)

def shamir_split(secret, n, t):
    coeffs = [secret] + [random.randint(1, 255) for _ in range(t-1)]
    shares = [(i, sum(coeffs[j] * (i ** j) for j in range(t)) % 256) for i in range(1, n+1)]
    print("Anahtar {} parçaya bölündü ve eşik değeri {} olarak belirlendi.".format(n, t))
    save_shares(shares, 'secret_key')  # Parçaları ayrı dosyalara kaydet
    save_key_as_array(shares, 'secret_key')  # Anahtarı bir dizi olarak kaydet
    return shares

def save_key_as_array(keys, base_filename):
    key_array = [key[1] for key in keys]  # Anahtar değerlerini bir dizi olarak al
    filename = "{}_key.txt".format(base_filename)
    with open(filename, 'w') as f:
        f.write(','.join(map(str, key_array)))  # Anahtar değerlerini dosyaya yaz
    print("Anahtar dizi olarak kaydedildi: {}".format(filename))

def save_shares(shares, base_filename):
    for i, share in enumerate(shares):
        filename = "{}_parca_{}.txt".format(base_filename, i+1)
        with open(filename, 'w') as f:
            f.write("Anahtar değeri: {}".format(share[1]))
        print("Anahtar parçası {} {} olarak kaydedildi.".format(i+1, filename))


# 5. Her Parça Görüntüyü Anahtar ile Şifreleme ve Kaydetme

def encrypt_image_with_key(image, key):
    encrypted_image = np.bitwise_xor(image, key)
    return encrypted_image

def save_encrypted_tiles(tiles, keys, base_filename):
    for i, tile in enumerate(tiles):
        encrypted_tile = encrypt_image_with_key(tile, keys[i][1])
        filename = "{}_sifreli_parca_{}.png".format(base_filename, i+1)
        save_image(encrypted_tile, filename)

# 6. Orijinal ve Şifreli Görüntülerin Karşılaştırılması (PSNR ve MSE)

def calculate_mse(original, stego):
    mse = np.mean((original - stego) ** 2)
    return mse

def calculate_psnr(original, stego):
    mse = calculate_mse(original, stego)
    if mse == 0:
        return float('inf')
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr

# Anahtarları dosyadan yükler
def load_keys(base_filename, n):
    keys = []
    for i in range(1, n+1):
        filename = "{}_parca_{}.txt".format(base_filename, i)
        with open(filename, 'r') as f:
            key_str = f.read().strip()
            key = int(key_str.split(',')[1])  # ":" işaretinden sonrasını al ve sayıya dönüştür
            keys.append(key)
    return keys


# Ana Fonksiyon

def main():
    # Lena görüntüsünü yükle
    lena_image = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
    lena_image = cv2.resize(lena_image, (256, 256))
    print("Lena görüntüsü yüklendi ve 256x256 boyutuna yeniden boyutlandırıldı.")

    # Mesajı Lena görüntüsüne LSB yöntemiyle göm
    secret_message = "Bu bir gizli mesajdır."
    stego_image = lsb_embed(lena_image, secret_message)
    print("Gizli mesaj Lena görüntüsüne gömüldü.")

    # Stego görüntüyü kaydet
    save_image(stego_image, 'stego_lena.png')
    
    # Stego görüntüyü 4 parçaya ayır
    tiles = split_image(stego_image)
    save_tiles(tiles, 'stego_lena')

    # Bir gizli anahtar oluştur ve 4 parçaya böl
    secret_key = 321421  # Örnek anahtar
    shares = shamir_split(secret_key, 4, 3)

    # Her görüntü parçasını ilgili anahtar parçasıyla şifrele
    save_encrypted_tiles(tiles, shares, 'stego_lena')

    # MSE ve PSNR hesapla
    reconstructed_image = cv2.imread('stego_lena.png', cv2.IMREAD_GRAYSCALE)
    mse_value = calculate_mse(lena_image, reconstructed_image)
    psnr_value = calculate_psnr(lena_image, reconstructed_image)
    print("MSE hesaplandı:", mse_value)
    print("PSNR hesaplandı:",psnr_value)

if __name__ == "__main__":
    main()
