def hex_to_rgb(hex_color):
    """
    將 Hex 字串轉換為 RGB Tuple。
    如果輸入格式錯誤，回傳預設的黑色 RGB (0, 0, 0)。

    Args:
        hex_color (str): Hex 顏色字串，例如 "#FFFFFF" 或 "#FFF"。

    Returns:
        tuple: RGB Tuple (R, G, B)，例如 (255, 255, 255)。
    """
    hex_color = hex_color.strip()
    if not hex_color.startswith('#'):
        return (0, 0, 0)

    hex_color = hex_color[1:] # 移除 '#'

    # 處理簡寫的 Hex (例如 #FFF)
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    if len(hex_color) != 6:
        return (0, 0, 0)

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        return (0, 0, 0)

if __name__ == '__main__':
    # 測試函式
    print(f"'#FFFFFF' -> {hex_to_rgb('#FFFFFF')}") # 預期: (255, 255, 255)
    print(f"'#fff' -> {hex_to_rgb('#fff')}")     # 預期: (255, 255, 255)
    print(f"'#000000' -> {hex_to_rgb('#000000')}") # 預期: (0, 0, 0)
    print(f"'#ABCDEF' -> {hex_to_rgb('#ABCDEF')}") # 預期: (171, 205, 239)
    print(f"'#123' -> {hex_to_rgb('#123')}")     # 預期: (17, 34, 51)
    print(f"'invalid' -> {hex_to_rgb('invalid')}") # 預期: (0, 0, 0)
    print(f"'#12345' -> {hex_to_rgb('#12345')}")   # 預期: (0, 0, 0)
    print(f"'##123456' -> {hex_to_rgb('##123456')}") # 預期: (0, 0, 0)
