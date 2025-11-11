# Microsleep Detection 😴

Proyek ini bertujuan untuk mendeteksi **microsleep (kantuk singkat)** secara otomatis menggunakan data dari sensor atau kamera. Sistem ini dapat membantu meningkatkan keselamatan pengemudi dengan memberikan peringatan dini saat tanda-tanda kantuk terdeteksi.
## Support By :
>- Dosen Pengampu : Akhmad Hendriawan ST., MT. (NIP.197501272002121003)
>- Mata kuliah : Pengolahan Citra
>- Program Studi : D4 Teknik Elektronika
>- Politeknik Elektronika Negeri Surabaya<br> 

## Teamwork
> 1. Nur Rohmat Hidayat (2122600012)
> 2. Fadlan Surya Anindita (2122600024)
> 3. Dwi Angga Ramadhani (2122600053)
> 4. Asyraf Sulthan Zaky (2122600060)

## 🚀 Fitur Utama
- Deteksi tanda-tanda kantuk berdasarkan citra wajah atau sinyal fisiologis.  
- Analisis waktu reaksi dan pola kedipan mata.  
- Peringatan otomatis (alarm visual/audio) saat terdeteksi microsleep.  
- Logging data untuk analisis lanjutan.

## 🧠 Teknologi yang Digunakan
- **Python** untuk pemrosesan data dan machine learning  
- **OpenCV / Viola jones Har cascade** untuk deteksi wajah dan mata  
- **Mediapipe** untuk mengukur mata tertutup 

## ⚙️ Diagram Alur 

<img src="Assets/Diagram_Block.png">

## 📷 Output Metode Viola jones Har cascade

**Mode User 👁️🙂**<br>

<div align="center">
<img src="Assets/Harcasecade4.png"><br>
</div>

**Mode User 👁️😴**<br>

<div align="center">
<img src="Assets/Harcasecade3.png" width = 900><br>
</div>

**Mode Engineer 👁️🙂**<br>

<div align="center">
<img src="Assets/Harcasecade1.png" width = 900><br>
</div>

**Mode Engineer 👁️😴**<br>

<div align="center">
<img src="Assets/Harcasecade2.png" width = 900><br>
</div>

## 📷 Output Metode Mediapipe
**Mode User 👁️🙂**<br>

<div align="center">
<img src="Assets/Mediapipe3.png"><br>
</div>

**Mode User 👁️😴**<br>

<div align="center">
<img src="Assets/Mediapipe4.png" width = 900><br>
</div>

**Mode Engineer 👁️🙂**<br>

<div align="center">
<img src="Assets/Mediapipe1.png" width = 900><br>
</div>

**Mode Engineer 👁️😴**<br>

<div align="center">
<img src="Assets/Mediapipe2.png" width = 900><br>
</div>

## Kesimpulan Praktikum Microsleep Detection

### Perbandingan Metode Deteksi Kantuk

Praktikum ini membandingkan dua metode deteksi microsleep pada mata manusia: **Viola-Jones Haar Cascade** dan **MediaPipe Face Mesh**. Kedua metode memiliki pendekatan berbeda dalam mengidentifikasi kondisi kantuk melalui analisis mata.

---

### 1. Viola-Jones Haar Cascade

Metode ini menggunakan **Dark Ratio** sebagai parameter utama untuk mendeteksi kantuk. Dark Ratio mengukur perbandingan area gelap (mata tertutup) terhadap total area deteksi mata.

#### Kelebihan:
- Implementasi relatif sederhana dan komputasi lebih ringan
- Telah terbukti efektif untuk deteksi objek berbasis fitur

#### Kelemahan:
- **Sangat sensitif terhadap perubahan pencahayaan dinamis**
- Akurasi menurun signifikan pada kondisi cahaya tidak stabil
- Memerlukan tuning threshold yang lebih kompleks untuk berbagai kondisi lingkungan
- Rentan terhadap false positive/negative pada pencahayaan rendah atau sangat terang

---

### 2. MediaPipe Face Mesh

Metode ini menggunakan **EAR (Eye Aspect Ratio)** yang menghitung rasio geometris antara jarak vertikal dan horizontal landmark mata.

#### Kelebihan:
- Lebih robust terhadap variasi pencahayaan
- Pengukuran berbasis landmark geometris lebih konsisten
- Akurasi lebih tinggi dalam berbagai kondisi lingkungan
- Deteksi lebih presisi karena menggunakan 468 facial landmarks

#### Kelemahan:
- Komputasi lebih berat dibanding Haar Cascade
- Memerlukan resource hardware yang lebih tinggi

---

### 3. Kesamaan Kedua Metode

- Keduanya menggunakan **threshold** sebagai batas klasifikasi antara mata terbuka dan tertutup
- Memerlukan **tuning parameter** untuk mengoptimalkan performa
- Implementasi pada mode User (sederhana) dan Engineer (detail) untuk fleksibilitas penggunaan

---

### Rekomendasi

Untuk aplikasi **microsleep detection pada pengemudi**, **MediaPipe** lebih direkomendasikan karena:
- Kondisi pencahayaan dalam kendaraan yang dinamis (siang/malam, tunnel, bayangan)
- Kebutuhan akurasi tinggi untuk keselamatan
- Trade-off komputasi dapat diatasi dengan hardware modern

Namun, **Viola-Jones Haar Cascade** tetap dapat menjadi pilihan untuk sistem dengan keterbatasan resource dan kondisi pencahayaan yang terkontrol.

---

### Kesimpulan Akhir

MediaPipe dengan parameter EAR memberikan performa lebih baik dan stabil dibanding Viola-Jones Haar Cascade dengan Dark Ratio, terutama pada kondisi pencahayaan dinamis yang merupakan tantangan utama dalam implementasi sistem deteksi microsleep real-time.