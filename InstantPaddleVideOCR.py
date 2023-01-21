from time import perf_counter, sleep
from paddleocr import PaddleOCR
from multiprocessing import Pool
# from paddleocr.detection import TextDetector
import os, sys, subprocess, logging
from colorama import Fore, Style, init

init(convert=True)
# Paddleocr supports Chinese, English, French, German, Korean and Japanese.
lang = "french"
# You can set the parameter `lang` as `ch`, `en`, `fr`, `german`, `korean`, `japan`
# to switch the language model in order.

#Initialization of the ocr engine
ocr = PaddleOCR(show_log = False, use_angle_cls=True, lang=lang, use_gpu=False,det=True) # need to run only once to download and load model into memory

def ocr_line(image: str) -> str:
    img_path = os.path.join(os.getcwd(), f"RGBImages\\{image}")
    result = ocr.ocr(img_path, cls=False, det=True)[0]
    # print(result)
    # print(len(result))
    # result = [ [ [ [[156.0, 228.0], [393.0, 226.0], [393.0, 268.0], [156.0, 270.0]], ('GUNDAM', 0.9964537620544434) ] ] ]
    if result:
        return f"{result[0][1][0]}\n{result[1][1][0]}" if len(result) == 2 else result[0][1][0]
    else:
        return

def get_vid(extension: str) -> list:
    folder = os.listdir(os.getcwd())
    mp4: list = list()
    for file in folder:
        if file.endswith(extension):
            mp4.append(file)
    return mp4

def get_time(img: str) -> str:
    start = '0' + img[0:11].replace('_', ':',2).replace('_', ',')
    end = '0' + img[13:24].replace('_', ':',2).replace('_', ',')
    return f"{start} --> {end}"

def write_srt(number: int, time: str, text: str, file: str) -> None:
    if not text:
        return
    file = file[:file.rfind('.')]
    with open(f"{file}.srt", 'a', encoding="utf-8") as srt:
        srt.write(f"{number}\n")
        srt.write(f"{time}\n")
        srt.write(f"{text}\n")
        srt.write("\n")

def create_sub(file: str) -> None:
    images = os.listdir(os.path.join(os.getcwd(), "RGBImages"))
    start_sub = perf_counter()
    print(f"Starting the OCR for {file}.")
    with Pool() as pool:
            result = pool.map(ocr_line, images)
    c = 0
    for image, text in zip(images, result):
        time = get_time(image)
        write_srt(c+1, time, text, file)
        c += 1
    print('\r', Fore.GREEN + f"SRT created for {file} in {round(perf_counter() - start_sub, 2)}s.\n" + Style.RESET_ALL)

def make(vid: list) -> None:
    for file in vid:
        print(f"Starting VSF for {file}.")
        subp = subprocess.Popen(f"""VideoSubFinderWXW.exe -c -r -i "{file}" -te 0.2""", stdout=subprocess.PIPE, shell=True)
        start_vsf = perf_counter()
        while subp.poll() == None:
            print('\r', f"Running for {round(perf_counter() - start_vsf, 2)}s.", end="")
            sleep(0.5)
        end_vsf = perf_counter()
        print('\r',Fore.GREEN + f"VSF for {file} done in {round(end_vsf-start_vsf, 2)}s !" + Style.RESET_ALL)
        create_sub(file)

if __name__ == "__main__":
    print("Type the extension of all the videos, ex : \"Something Someting.avi\" will be '.avi'")
    extension = str(input("Extension of all files : "))
    start_time = perf_counter()
    print("Starting the batch")
    vid = get_vid(extension)
    make(vid)
    print(f"Done in {round(perf_counter() - start_time, 2)} secondes.")