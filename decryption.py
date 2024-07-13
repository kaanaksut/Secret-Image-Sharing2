import numpy as np
import cv2
import random
import math
import os

# 1. Anahtar dosyalarını yükle
def load_keys(base_filename, n):
    keys = []
    for i in range(n):
        filename = "{}_parca_{}.txt".format(base_filename, i+1)
        try:
            with open(filename, 'r') as f:
                key_str = f.read().strip()
                key_value = int(key_str.split(':')[1].strip())
                keys.append(key_value)
        except FileNotFoundError:
            print("Hata: Anahtar dosyası '{}' bulunamadı.".format(filename))
            return None
        except (IndexError, ValueError):
            print("Hata: Anahtar dosyası '{}' beklenen formatta değil.".format(filename))
            return None
    print("Anahtarlar başarıyla yüklendi.")
    return keys

# 2. Şifreli parçaları deşifre et
def decrypt_tiles(encrypted_tiles, keys):
    decrypted_tiles = []
    for i, tile in enumerate(encrypted_tiles):
        decrypted_tile = decrypt_image_with_key(tile, keys[i])
        if decrypted_tile is not None:
            decrypted_tiles.append(decrypted_tile)
        else:
            print("Hata: Parça {} deşifrelenirken bir hata oluştu.".format(i+1))
            return None
    print("Tüm parçalar başarıyla deşifre edildi.")
    return decrypted_tiles

# 3. Anahtar ile görüntüyü deşifre et
def decrypt_image_with_key(image, key):
    try:
        decrypted_image = np.bitwise_xor(image, key)
        return decrypted_image
    except Exception as e:
        print("Hata:", e)
        return None

# 4. Deşifre edilmiş parçaları birleştir ve kaydet
def merge_tiles(tiles):
    h, w = tiles[0].shape
    rows = len(tiles) // 2
    cols = 2
    merged_image = np.zeros((h * rows, w * cols), dtype=np.uint8)
    for i, tile in enumerate(tiles):
        r = i // cols
        c = i % cols
        merged_image[r * h: (r + 1) * h, c * w: (c + 1) * w] = tile
    return merged_image

def save_merged_image(merged_image, filename):
    cv2.imwrite(filename, merged_image)
    print("Birleştirilmiş görüntü {} olarak kaydedildi.".format(filename))

# 5. Yardımcı fonksiyonlar
def save_image(image, filename):
    cv2.imwrite(filename, image)
    print("Görüntü {} olarak kaydedildi.".format(filename))
    
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


# 6. Ana fonksiyon
def main():
    # Şifreli parçaları yükle
    encrypted_tiles = []
    for i in range(4):
        filename = "stego_lena_sifreli_parca_{}.png".format(i+1)
        try:
            tile = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
            encrypted_tiles.append(tile)
        except FileNotFoundError:
            print("Hata: Şifreli parça '{}' bulunamadı.".format(filename))
            return

    # Anahtarları yükle
    keys = load_keys('secret_key', 4)
    if keys is None:
        return

    # Şifreli parçaları deşifre et
    decrypted_tiles = decrypt_tiles(encrypted_tiles, keys)
    if decrypted_tiles is None:
        return

    # Deşifre edilmiş parçaları birleştir
    merged_image = merge_tiles(decrypted_tiles)

    # Birleştirilmiş görüntüyü kaydet
    save_merged_image(merged_image, 'merged_image.png')
    
 # Yüklenen dosyaları oku ve boyutlarını ayarla
    lena = cv2.imread('lena.png', cv2.IMREAD_GRAYSCALE)
    lena_resized = cv2.resize(lena, (256, 256))

    stego_lena = cv2.imread('stego_lena.png', cv2.IMREAD_GRAYSCALE)

    merged_image = cv2.imread('merged_image.png', cv2.IMREAD_GRAYSCALE)

    # MSE ve PSNR hesapla
    mse_lena_stego = calculate_mse(lena_resized, stego_lena)
    psnr_lena_stego = calculate_psnr(lena_resized, stego_lena)

    mse_lena_merged = calculate_mse(lena_resized, merged_image)
    psnr_lena_merged = calculate_psnr(lena_resized, merged_image)

    mse_stego_merged = calculate_mse(stego_lena, merged_image)
    psnr_stego_merged = calculate_psnr(stego_lena, merged_image)

    # Sonuçları yazdır
    print("Lena ve Stego Lena arasındaki MSE:", mse_lena_stego)
    print("Lena ve Stego Lena arasındaki PSNR:", psnr_lena_stego)
    print("Lena ve Merged Image arasındaki MSE:", mse_lena_merged)
    print("Lena ve Merged Image arasındaki PSNR:", psnr_lena_merged)
    print("Stego Lena ve Merged Image arasındaki MSE:", mse_stego_merged)
    print("Stego Lena ve Merged Image arasındaki PSNR:", psnr_stego_merged)

if __name__ == "__main__":
    main()
