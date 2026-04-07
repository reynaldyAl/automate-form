# Automate Form

Automasi pengisian Google Form instrumen penelitian:

Pengaruh Sikap Perfeksionisme dan Dukungan Sosial Terhadap Academic Burnout.

Project ini mendukung:
- pengisian data responden dari CSV,
- pembangkitan jawaban sintetis yang konsisten dengan profil,
- mode uji tanpa submit (DRY_RUN),
- analisis hasil ke CSV.

## Struktur Project

- [main.py](main.py): entry point utama.
- [form_filler.py](form_filler.py): automasi Selenium untuk isi form.
- [data_generator.py](data_generator.py): generator jawaban sintetis.
- [result_analyzer.py](result_analyzer.py): scoring, konsistensi, ringkasan statistik.
- [utils.py](utils.py): helper nama, gender, distribusi demografi.
- [config.py](config.py): konfigurasi profile, rule skor, range konsistensi.
- [requirements.txt](requirements.txt): dependency Python.
- [data_nama_mahasiswa_sastra.csv](data_nama_mahasiswa_sastra.csv): sumber nama responden.
- [results/](results/): output analisis (survey_results.csv).

## Setup Environment

1. Buka terminal di folder project.

2. Buat virtual environment:

	py -m venv venv

3. Aktifkan virtual environment (PowerShell):

	.\venv\Scripts\Activate.ps1

4. Install dependency:

	py -m pip install -r requirements.txt

Catatan:
- Jika command python belum dikenali di Windows, gunakan py.
- Jika sudah aktif venv, prompt akan menampilkan (venv).

## Konfigurasi .env

Pastikan file [\.env](.env) berisi minimal:

	FORM_URL=https://forms.gle/h77StnbaaogNoW4x9
	CSV_FILE=data_nama_mahasiswa_sastra.csv
	NUM_SUBMISSIONS=50
	BROWSER_HEADLESS=False
	DRY_RUN=True

Penjelasan:
- FORM_URL: link Google Form target.
- CSV_FILE: file nama responden.
- NUM_SUBMISSIONS: jumlah responden yang dijalankan.
- BROWSER_HEADLESS: True untuk tanpa UI browser, False untuk terlihat.
- DRY_RUN: True untuk isi tanpa klik submit, False untuk submit sungguhan.

## Command Terminal Yang Dipakai

Jalankan script utama:

	python main.py

Atau jika python alias bermasalah:

	py main.py

## Alur Eksekusi

Saat dijalankan, sistem akan:
- load nama dari CSV,
- generate jawaban sesuai profil,
- isi form per halaman,
- jika DRY_RUN=True maka tidak submit,
- simpan analisis ke [results/survey_results.csv](results/survey_results.csv),
- tampilkan summary statistik di terminal.

## Mode Penggunaan

Mode test aman (disarankan):

	DRY_RUN=True
	NUM_SUBMISSIONS=5

Mode produksi (submit real):

	DRY_RUN=False
	NUM_SUBMISSIONS=120

Saran run produksi:
- Uji dulu 3-5 responden dengan DRY_RUN=True.
- Setelah valid, ubah DRY_RUN=False.
- Jalankan bertahap (misal 20 lalu 100) untuk meminimalkan risiko.

## Output

File output utama:
- [results/survey_results.csv](results/survey_results.csv)

Kolom penting:
- profile_assigned
- response_style
- perfectionism_score
- social_support_score
- burnout_score
- burnout_level
- is_consistent
- status

## Troubleshooting Singkat

1. python tidak dikenali:
- gunakan py main.py.

2. Gagal install dependency:
- pastikan venv aktif,
- jalankan ulang py -m pip install -r requirements.txt.

3. Form tidak submit:
- cek nilai DRY_RUN di [\.env](.env),
- DRY_RUN=True memang tidak submit.

4. Hasil tidak muncul:
- cek folder [results/](results/),
- pastikan proses selesai tanpa error terminal.
