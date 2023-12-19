import copy
import numpy as np
import cv2
import subprocess
import time
import OCR
import pyautogui
import os

import sudo6  # 6宫格解决方案
import sudo9  # 9宫格解决方案
import cut_screenshot  # 截图&裁剪

# 游戏模式参数确认
# 宫格
sudoku_square_grid_confirm = 9  # 4,6,9
# 坐标转换
coord_convert_confirm = False  # True, False
# 矩阵图形&坐标行列
matrix_rows_and_columns = sudoku_square_grid_confirm
# 创建一个字典，其中的键是数独大小，值是对应的模块名
sudoku_modules = {
    4: 'sudo4',
    6: 'sudo6',
    9: 'sudo9'
}


def find_picture():
    """
    使用OpenCV模板匹配找到小图在大图中的位置
    """
    # Step 1: 截图并保存到电脑
    os.system('adb shell screencap -p /sdcard/region_nextOne.png')
    os.system('adb pull /sdcard/region_nextOne.png')

    # Step 2: 使用OpenCV读取大图和小图
    big_image = cv2.imread('region_nextOne.png')
    small_image = cv2.imread('nextOne.png')  # 小图路径

    # Step 3: 使用模板匹配找到小图位置
    result = cv2.matchTemplate(big_image, small_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Step 4: 获取小图的顶点坐标
    top_left = max_loc
    bottom_right = (top_left[0] + small_image.shape[1], top_left[1] + small_image.shape[0])

    # Step 5: 计算小图中心点坐标
    center_point = (top_left[0] + bottom_right[0]) // 2, (top_left[1] + bottom_right[1]) // 2

    # Step 6: 使用adb命令模拟点击
    os.system(f'adb shell input tap {center_point[0]} {center_point[1]}')
    # print('-----------------NEXT ONE-------------------')
    # 延时0.5s    消除手机开启触摸轨迹的红色误判
    time.sleep(0.5)
    # 定义你要点击的点的坐标
    x, y = 2000, 500
    # 构造adb命令
    adb_command = f"adb shell input tap {x} {y}"
    # 执行adb命令
    os.system(adb_command)
    # print('-----------------NEXT ONE-------------------')


def adb_click(coordinates_ma, ocr_ma, solution_ma):
    # 定义延时时间
    global target_coordinates
    DELAY = 0.1

    # ////////////
    match sudoku_square_grid_confirm:
        case 4:
            # 目标坐标点，根据数独的数字1-4
            target_coordinates = {
                1: (144, 1630),
                2: (418, 1630),
                3: (665, 1630),
                4: (927, 1630)
            }
        case 6:
            # 目标坐标点，根据数独的数字1-6
            target_coordinates = {
                1: (100, 1630),
                2: (270, 1630),
                3: (440, 1630),
                4: (610, 1630),
                5: (780, 1630),
                6: (950, 1630)
            }
        case 9:
            # 目标坐标点，根据数独的数字1-6
            target_coordinates = {
                1: (100, 1630),
                2: (270, 1630),
                3: (440, 1630),
                4: (610, 1630),
                5: (780, 1630),
                6: (950, 1630)
            }
        case _:
            print("请确认数独矩阵分割图形&坐标行列确认： 4,6,9")
            return None  # 如果输入不合法，返回None
    # ////////////

    # 比较两个矩阵并执行ADB命令
    print('12111111111')
    for i in range(matrix_rows_and_columns):
        for j in range(matrix_rows_and_columns):
            if ocr_ma[i][j] == 0 and solution_ma[i][j] != 0:
                # 获取原始坐标
                x, y = coordinates_ma[i][j]
                # 点击原始坐标
                adb_tap_command = f"adb shell input swipe {x} {y} {x} {y} 56"
                subprocess.run(adb_tap_command, shell=True)
                # time.sleep(DELAY)  # 延时
                # 获取目标坐标
                target_x, target_y = target_coordinates[solution_ma[i][j]]
                # 点击目标坐标
                adb_tap_command = f"adb shell input swipe {target_x} {target_y} {target_x} {target_y} 56"
                subprocess.run(adb_tap_command, shell=True)
                time.sleep(DELAY)  # 延时


# 主函数
def main(sudu_number):
    # 截图取图，二值化
    # cut_screenshot.get_convert_cut_screenshot()
    # 原始坐标矩阵
    # coordinates_matrix = cut_screenshot.coordinate_matrix()
    print('-----------------WAIT OCR----AVG 12s--------------------')
    # OCR识别结果矩阵
    ocr_matrix = OCR.padddleocr_result()
    # 解决方案矩阵
    # 获取对应的模块名
    module_name = sudoku_modules[sudu_number]
    # 获取全局符号表
    global_symbols = globals()
    # 获取对应的模块
    module = global_symbols[module_name]
    # 使用模块的函数
    module.sudoku = copy.deepcopy(ocr_matrix)
    _, solution_matrix = module.solve()

    if solution_matrix is None:
        print("无解决方案，请确认OCR识别结果是否正确！")
        # exit(1)  # 退出程序
    else:
        print("解决方案：")
        print(solution_matrix)

    time.sleep(1)
    # adb_click(coordinates_matrix, ocr_matrix, solution_matrix)

    time.sleep(0.3)

    find_picture()
    time.sleep(1)


if __name__ == '__main__':
    while True:
        main(sudoku_square_grid_confirm)
        break