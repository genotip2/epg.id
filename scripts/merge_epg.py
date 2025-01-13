import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

# URLs dari penyedia EPG
main_url = 'https://epgshare01.online/epgshare01/epg_ripper_ID1.xml.gz'  # URL utama EPG
additional_url = 'https://github.com/genotip2/epg/raw/refs/heads/master/super.guide.xml.gz'  # URL file EPG tambahan

# Fungsi untuk membaca file .gz dan mengubahnya menjadi XML
def read_gzipped_xml(url):
    response = requests.get(url)
    if response.status_code == 200:
        # Membaca file .gz dari response
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
            # Mendekompresi dan membaca file XML
            return ET.parse(f)  # Kembalikan objek ElementTree
    else:
        raise Exception(f'Gagal mengunduh file: {url}, status code: {response.status_code}')

# Unduh dan proses file utama
main_tree = read_gzipped_xml(main_url)
main_root = main_tree.getroot()  # Akses root dari main_tree (root XML file utama)

# Pastikan main_root adalah objek Element
if not isinstance(main_root, ET.Element):
    raise TypeError("main_root harus berupa objek Element")

# Unduh dan proses file tambahan
additional_tree = read_gzipped_xml(additional_url)
additional_root = additional_tree.getroot()  # Akses root dari additional_tree (root XML file tambahan)

# Pastikan additional_root adalah objek Element
if not isinstance(additional_root, ET.Element):
    raise TypeError("additional_root harus berupa objek Element")

# Channel ID yang ingin dihapus hanya dari file utama
channels_to_remove = ['SCTV.id', 'GTV.id']

# Hapus channel dari file utama
for channel in main_root.findall('channel'):
    if channel.get('id') in channels_to_remove:
        main_root.remove(channel)

# Hapus programme terkait channel yang dihapus
for programme in main_root.findall('programme'):
    if programme.get('channel') in channels_to_remove:
        main_root.remove(programme)

# Gabungkan channel dari file tambahan ke file utama
for channel in additional_root.findall('channel'):
    main_root.append(channel)

# Gabungkan programme dari file tambahan ke file utama (jika ada)
for programme in additional_root.findall('programme'):
    main_root.append(programme)

# Simpan hasil gabungan ke file baru
output_file = 'merged_epg.xml'
main_tree.write(output_file, encoding='utf-8', xml_declaration=True)

print(f"File berhasil disimpan ke {output_file}")
