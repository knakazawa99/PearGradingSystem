def compress_list_to_1byte(data_list):
    # 先頭から8ビット分を取り出す
    bits = data_list[:8]

    # 不足しているビットを0埋め
    data_len = len(data_list)
    if data_len < 8:
        bits.extend([0 for i in range(8-data_len)])

    byte = 0
    for i in range(8):
        byte |= bits[i]*(2**(i))

    return byte


x = [1 for i in range(6)]
#x = [1,1,1,1,0,0,0,0]

y = compress_list_to_1byte(x)

print(x)
print(y)
