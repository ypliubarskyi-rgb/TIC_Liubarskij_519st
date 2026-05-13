import os
import math
import numpy as np
from scipy import fftpack
from PIL import Image
import heapq
from collections import Counter


class HuffmanTree:
    class _Node:
        def __init__(self, symbol, freq):
            self.symbol = symbol
            self.freq = freq
            self.left = None
            self.right = None
        def __lt__(self, other):
            return self.freq < other.freq

    def __init__(self, data):
        freq = Counter(data)
        heap = [self._Node(sym, cnt) for sym, cnt in freq.items()]
        heapq.heapify(heap)
        if len(heap) == 1:
            node = heapq.heappop(heap)
            root = self._Node(None, node.freq)
            root.left = node
            heapq.heappush(heap, root)
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            merged = self._Node(None, a.freq + b.freq)
            merged.left = a
            merged.right = b
            heapq.heappush(heap, merged)
        self._root = heap[0] if heap else None
        self._table = {}
        if self._root:
            self._build_table(self._root, '')

    def _build_table(self, node, code):
        if node is None:
            return
        if node.symbol is not None:
            self._table[node.symbol] = code if code else '0'
            return
        self._build_table(node.left, code + '0')
        self._build_table(node.right, code + '1')

    def value_to_bitstring_table(self):
        return dict(self._table)


def bits_required(n):
    n = abs(n)
    result = 0
    while n > 0:
        n >>= 1
        result += 1
    return result

def flatten(lst):
    return [item for sublist in lst for item in sublist]

def binstr_flip(binstr):
    return ''.join('0' if c == '1' else '1' for c in binstr)

def uint_to_binstr(number, size):
    return bin(number)[2:][-size:].zfill(size)

def int_to_binstr(n):
    if n == 0:
        return ''
    binstr = bin(abs(n))[2:]
    return binstr if n > 0 else binstr_flip(binstr)


def dct_2d(image):
    return fftpack.dct(fftpack.dct(image.T, norm='ortho').T, norm='ortho')

def idct_2d(image):
    return fftpack.idct(fftpack.idct(image.T, norm='ortho').T, norm='ortho')

def load_quantization_table(component, table_id=1):
    if component == 'lum':
        if table_id == 1:
            return np.array([
                [2,  2,  2,  2,  3,  4,  5,  6],
                [2,  2,  2,  2,  3,  4,  5,  6],
                [2,  2,  2,  2,  4,  5,  7,  9],
                [2,  2,  2,  4,  5,  7,  9, 12],
                [3,  3,  4,  5,  8, 10, 12, 12],
                [4,  4,  5,  7, 10, 12, 12, 12],
                [5,  5,  7,  9, 12, 12, 12, 12],
                [6,  6,  9, 12, 12, 12, 12, 12],
            ])
        else:
            return np.array([
                [16, 11, 10, 16, 24, 40, 51, 61],
                [12, 12, 14, 19, 26, 48, 60, 55],
                [14, 13, 16, 24, 40, 57, 69, 56],
                [14, 17, 22, 29, 51, 87, 80, 62],
                [18, 22, 37, 56, 68, 109, 103, 77],
                [24, 35, 55, 64, 81, 104, 113, 92],
                [49, 64, 78, 87, 103, 121, 120, 101],
                [72, 92, 95, 98, 112, 100, 103, 99],
            ])
    elif component == 'chrom':
        if table_id == 1:
            return np.array([
                [3,  3,  5,  9, 13, 15, 15, 15],
                [3,  4,  6, 11, 14, 12, 12, 12],
                [5,  6,  9, 14, 12, 12, 12, 12],
                [9, 11, 14, 12, 12, 12, 12, 12],
                [13, 14, 12, 12, 12, 12, 12, 12],
                [15, 12, 12, 12, 12, 12, 12, 12],
                [15, 12, 12, 12, 12, 12, 12, 12],
                [15, 12, 12, 12, 12, 12, 12, 12],
            ])
        else:
            return np.array([
                [17, 18, 24, 47, 99, 99, 99, 99],
                [18, 21, 26, 66, 99, 99, 99, 99],
                [24, 26, 56, 99, 99, 99, 99, 99],
                [47, 66, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
                [99, 99, 99, 99, 99, 99, 99, 99],
            ])
    else:
        raise ValueError("component має бути 'lum' або 'chrom'")

def quantize(block, component, table_id=1):
    q = load_quantization_table(component, table_id)
    return (block / q).round().astype(np.int32)

def dequantize(block, component, table_id=1):
    q = load_quantization_table(component, table_id)
    return block * q


def zigzag_points(rows, cols):
    UP, DOWN, RIGHT, LEFT, UP_RIGHT, DOWN_LEFT = range(6)

    def move(direction, point):
        return {
            UP:        lambda p: (p[0]-1, p[1]),
            DOWN:      lambda p: (p[0]+1, p[1]),
            LEFT:      lambda p: (p[0], p[1]-1),
            RIGHT:     lambda p: (p[0], p[1]+1),
            UP_RIGHT:  lambda p: move(UP, move(RIGHT, p)),
            DOWN_LEFT: lambda p: move(DOWN, move(LEFT, p)),
        }[direction](point)

    def inbounds(point):
        return 0 <= point[0] < rows and 0 <= point[1] < cols

    point = (0, 0)
    move_up = True
    for _ in range(rows * cols):
        yield point
        if move_up:
            if inbounds(move(UP_RIGHT, point)):
                point = move(UP_RIGHT, point)
            else:
                move_up = False
                if inbounds(move(RIGHT, point)):
                    point = move(RIGHT, point)
                else:
                    point = move(DOWN, point)
        else:
            if inbounds(move(DOWN_LEFT, point)):
                point = move(DOWN_LEFT, point)
            else:
                move_up = True
                if inbounds(move(DOWN, point)):
                    point = move(DOWN, point)
                else:
                    point = move(RIGHT, point)

def block_to_zigzag(block):
    return np.array([block[point] for point in zigzag_points(*block.shape)])

def zigzag_to_block(zigzag):
    rows = cols = int(math.sqrt(len(zigzag)))
    block = np.empty((rows, cols), np.int32)
    for i, point in enumerate(zigzag_points(rows, cols)):
        block[point] = zigzag[i]
    return block


def run_length_encode(arr):
    last_nonzero = -1
    for i, elem in enumerate(arr):
        if elem != 0:
            last_nonzero = i
    symbols, values = [], []
    run_length = 0
    for i, elem in enumerate(arr):
        if i > last_nonzero:
            symbols.append((0, 0))
            values.append(int_to_binstr(0))
            break
        elif elem == 0 and run_length < 15:
            run_length += 1
        else:
            size = bits_required(elem)
            symbols.append((run_length, size))
            values.append(int_to_binstr(elem))
            run_length = 0
    return symbols, values


def rgb_to_ycbcr(img_rgb):
    arr = np.array(img_rgb, dtype=np.float32)
    R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    Y  = np.clip( 0.299*R    + 0.587*G    + 0.114*B,           0, 255)
    Cb = np.clip(-0.168736*R - 0.331264*G + 0.5*B    + 128,    0, 255)
    Cr = np.clip( 0.5*R      - 0.418688*G - 0.081312*B + 128,  0, 255)
    return np.stack([Y, Cb, Cr], axis=2).astype(np.uint8)

def ycbcr_to_rgb(npmat):
    Y  = npmat[:,:,0].astype(np.float32)
    Cb = npmat[:,:,1].astype(np.float32) - 128
    Cr = npmat[:,:,2].astype(np.float32) - 128
    R = np.clip(Y               + 1.402   * Cr,           0, 255).astype(np.uint8)
    G = np.clip(Y - 0.344136*Cb - 0.714136* Cr,           0, 255).astype(np.uint8)
    B = np.clip(Y + 1.772   *Cb,                          0, 255).astype(np.uint8)
    return np.stack([R, G, B], axis=2)


def write_to_file(filepath, dc, ac, blocks_count, tables):
    f = open(filepath, 'w')
    for table_name in ['dc_y', 'ac_y', 'dc_c', 'ac_c']:
        f.write(uint_to_binstr(len(tables[table_name]), 16))
        for key, value in tables[table_name].items():
            if table_name in {'dc_y', 'dc_c'}:
                f.write(uint_to_binstr(key, 4))
                f.write(uint_to_binstr(len(value), 4))
                f.write(value)
            else:
                f.write(uint_to_binstr(key[0], 4))
                f.write(uint_to_binstr(key[1], 4))
                f.write(uint_to_binstr(len(value), 8))
                f.write(value)
    f.write(uint_to_binstr(blocks_count, 32))
    for b in range(blocks_count):
        for c in range(3):
            dc_table = tables['dc_y'] if c == 0 else tables['dc_c']
            ac_table = tables['ac_y'] if c == 0 else tables['ac_c']
            category = bits_required(dc[b, c])
            f.write(dc_table[category])
            f.write(int_to_binstr(dc[b, c]))
            symbols, values = run_length_encode(ac[b, :, c])
            for i in range(len(symbols)):
                f.write(ac_table[tuple(symbols[i])])
                f.write(values[i])
    f.close()


class JPEGFileReader:
    TABLE_SIZE_BITS      = 16
    BLOCKS_COUNT_BITS    = 32
    DC_CODE_LENGTH_BITS  = 4
    CATEGORY_BITS        = 4
    AC_CODE_LENGTH_BITS  = 8
    RUN_LENGTH_BITS      = 4
    SIZE_BITS            = 4

    def __init__(self, filepath):
        self.__file = open(filepath, 'r')

    def read_int(self, size):
        if size == 0:
            return 0
        bin_num = self.__read_str(size)
        if bin_num[0] == '1':
            return self.__int2(bin_num)
        else:
            return self.__int2(binstr_flip(bin_num)) * -1

    def read_dc_table(self):
        table = {}
        table_size = self.__read_uint(self.TABLE_SIZE_BITS)
        for _ in range(table_size):
            category    = self.__read_uint(self.CATEGORY_BITS)
            code_length = self.__read_uint(self.DC_CODE_LENGTH_BITS)
            code        = self.__read_str(code_length)
            table[code] = category
        return table

    def read_ac_table(self):
        table = {}
        table_size = self.__read_uint(self.TABLE_SIZE_BITS)
        for _ in range(table_size):
            run_length  = self.__read_uint(self.RUN_LENGTH_BITS)
            size        = self.__read_uint(self.SIZE_BITS)
            code_length = self.__read_uint(self.AC_CODE_LENGTH_BITS)
            code        = self.__read_str(code_length)
            table[code] = (run_length, size)
        return table

    def read_blocks_count(self):
        return self.__read_uint(self.BLOCKS_COUNT_BITS)

    def read_huffman_code(self, table):
        prefix = ''
        while prefix not in table:
            prefix += self.__read_char()
        return table[prefix]

    def __read_uint(self, size):
        if size <= 0:
            raise ValueError("розмір повинен бути більшим за 0")
        return self.__int2(self.__read_str(size))

    def __read_str(self, length):
        return self.__file.read(length)

    def __read_char(self):
        return self.__read_str(1)

    def __int2(self, bin_num):
        return int(bin_num, 2)


def read_image_file(filepath):
    reader = JPEGFileReader(filepath)
    tables = {}
    for table_name in ['dc_y', 'ac_y', 'dc_c', 'ac_c']:
        if 'dc' in table_name:
            tables[table_name] = reader.read_dc_table()
        else:
            tables[table_name] = reader.read_ac_table()
    blocks_count = reader.read_blocks_count()
    dc = np.empty((blocks_count, 3), dtype=np.int32)
    ac = np.empty((blocks_count, 63, 3), dtype=np.int32)
    for block_index in range(blocks_count):
        for component in range(3):
            dc_table = tables['dc_y'] if component == 0 else tables['dc_c']
            ac_table = tables['ac_y'] if component == 0 else tables['ac_c']
            category = reader.read_huffman_code(dc_table)
            dc[block_index, component] = reader.read_int(category)
            cells_count = 0
            while cells_count < 63:
                run_length, size = reader.read_huffman_code(ac_table)
                if (run_length, size) == (0, 0):
                    while cells_count < 63:
                        ac[block_index, cells_count, component] = 0
                        cells_count += 1
                else:
                    for _ in range(run_length):
                        ac[block_index, cells_count, component] = 0
                        cells_count += 1
                    if size == 0:
                        ac[block_index, cells_count, component] = 0
                    else:
                        value = reader.read_int(size)
                        ac[block_index, cells_count, component] = value
                    cells_count += 1
    return dc, ac, tables, blocks_count


def prepare_image(input_file, max_side=512):
    img = Image.open(input_file).convert('RGB')
    w, h = img.size
    side = min(w, h, max_side)
    side = (side // 8) * 8
    img = img.crop((0, 0, side, side))
    return img


def encode(input_file, output_file, table_id=1):
    image = prepare_image(input_file)
    npmat = rgb_to_ycbcr(image)
    rows, cols = npmat.shape[0], npmat.shape[1]
    if rows % 8 != 0 or cols % 8 != 0:
        raise ValueError("Ширина і висота зображення мають бути кратними 8")
    blocks_count = rows // 8 * cols // 8
    dc = np.empty((blocks_count, 3), dtype=np.int32)
    ac = np.empty((blocks_count, 63, 3), dtype=np.int32)
    block_index = 0
    for i in range(0, rows, 8):
        for j in range(0, cols, 8):
            for k in range(3):
                block        = npmat[i:i+8, j:j+8, k].astype(np.float32) - 128
                dct_matrix   = dct_2d(block)
                comp         = 'lum' if k == 0 else 'chrom'
                quant_matrix = quantize(dct_matrix, comp, table_id)
                zigzag       = block_to_zigzag(quant_matrix)
                dc[block_index, k]    = zigzag[0]
                ac[block_index, :, k] = zigzag[1:]
            block_index += 1
    H_DC_Y = HuffmanTree(np.vectorize(bits_required)(dc[:, 0]))
    H_DC_C = HuffmanTree(np.vectorize(bits_required)(dc[:, 1:].flat))
    H_AC_Y = HuffmanTree(
        flatten(run_length_encode(ac[i, :, 0])[0] for i in range(blocks_count)))
    H_AC_C = HuffmanTree(
        flatten(run_length_encode(ac[i, :, j])[0]
                for i in range(blocks_count) for j in [1, 2]))
    tables = {
        'dc_y': H_DC_Y.value_to_bitstring_table(),
        'ac_y': H_AC_Y.value_to_bitstring_table(),
        'dc_c': H_DC_C.value_to_bitstring_table(),
        'ac_c': H_AC_C.value_to_bitstring_table(),
    }
    write_to_file(output_file, dc, ac, blocks_count, tables)
    size_input  = os.path.getsize(input_file)
    size_output = os.path.getsize(output_file)
    print(f"  Закодовано. Вхідний файл: {size_input} байт | Файл потоку: {size_output} байт")
    return size_input, rows, cols


def decoder(output_file, jpeg_filename, size_input, table_id=1):
    dc, ac, tables, blocks_count = read_image_file(output_file)
    block_side      = 8
    image_side      = int(math.sqrt(blocks_count)) * block_side
    blocks_per_line = image_side // block_side
    npmat = np.zeros((image_side, image_side, 3), dtype=np.float32)
    for block_index in range(blocks_count):
        i = block_index // blocks_per_line * block_side
        j = block_index % blocks_per_line * block_side
        for c in range(3):
            zigzag       = [dc[block_index, c]] + list(ac[block_index, :, c])
            quant_matrix = zigzag_to_block(zigzag)
            comp         = 'lum' if c == 0 else 'chrom'
            dct_matrix   = dequantize(quant_matrix, comp, table_id)
            block        = idct_2d(dct_matrix)
            npmat[i:i+8, j:j+8, c] = block + 128
    npmat = np.clip(npmat, 0, 255).astype(np.uint8)
    rgb   = ycbcr_to_rgb(npmat)
    image = Image.fromarray(rgb, 'RGB')
    image.save(jpeg_filename, 'JPEG', quality=95)
    size_jpeg     = os.path.getsize(jpeg_filename)
    width, height = image.size
    ratio         = size_input / size_jpeg if size_jpeg else 0
    print(f"  Збережено: {jpeg_filename}  ({width}×{height})  "
          f"JPEG-розмір: {size_jpeg} байт  КС={ratio:.2f}")
    return size_jpeg, width, height, ratio


def process_image(label, input_file, results_dir="Results", results_file="results_jpeg.txt"):
    os.makedirs(results_dir, exist_ok=True)
    size_input = os.path.getsize(input_file)
    with open(results_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Зображення: {label}  ({input_file})\n")
        f.write(f"Розмір вихідного файла: {size_input} байт\n")
        f.write(f"{'='*60}\n")
    for table_id in [1, 2]:
        stream_file = os.path.join(results_dir, f"{label}_t{table_id}.asf")
        jpeg_out    = os.path.join(results_dir, f"JPEG_{label}_t{table_id}.jpg")
        print(f"\n[{label}] Таблиця квантування #{table_id}")
        print("  Кодування...")
        try:
            size_in, rows, cols = encode(input_file, stream_file, table_id=table_id)
        except Exception as e:
            print(f"  ПОМИЛКА кодування: {e}")
            continue
        print("  Декодування...")
        try:
            size_jpeg, w, h, ratio = decoder(stream_file, jpeg_out, size_in, table_id=table_id)
        except Exception as e:
            print(f"  ПОМИЛКА декодування: {e}")
            continue
        with open(results_file, "a", encoding="utf-8") as f:
            f.write(f"\nТаблиця квантування #{table_id}:\n")
            f.write(f"  Розмір вихідного файла : {size_in} байт\n")
            f.write(f"  Розмір файла потоку    : {os.path.getsize(stream_file)} байт\n")
            f.write(f"  Розмір файла JPEG      : {size_jpeg} байт\n")
            f.write(f"  Розмір зображення JPEG : {w}x{h}\n")
            f.write(f"  Коефіцієнт стиснення   : {ratio:.2f}\n")
    print(f"  Результати збережено у '{results_file}' та папці '{results_dir}'")


if __name__ == "__main__":
    BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
    RESULTS_DIR = os.path.join(BASE_DIR, "Results")
    RESULTS_TXT = os.path.join(BASE_DIR, "results_jpeg.txt")
    images = {
        "weak_texture":   os.path.join(BASE_DIR, "images", "canvas.png"),
        "medium_texture": os.path.join(BASE_DIR, "images", "canvas_medium.png"),
        "strong_texture": os.path.join(BASE_DIR, "images", "canvas_strong.png"),
    }
    with open(RESULTS_TXT, "w", encoding="utf-8") as f:
        f.write("Результати виконання алгоритму JPEG\n")
        f.write("=" * 60 + "\n")
    for label, path in images.items():
        if not os.path.exists(path):
            print(f"[!] Файл не знайдено: {path}  — пропускаємо")
            continue
        process_image(label, path, results_dir=RESULTS_DIR, results_file=RESULTS_TXT)
    print("\nГотово! Перевірте 'results_jpeg.txt' та папку 'Results'.")