import os
import logging
import pyautogui
import time
import json
import psutil
from psutil import Popen, NoSuchProcess
import subprocess
from subprocess import PIPE
import sys
import traceback
from PIL import Image
import pyscreenshot
from datetime import datetime
import platform
from elements import MaterialXElements

if platform.system() == "Windows":
    import win32api
    import win32gui
    import win32con

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import local_config


pyautogui.FAILSAFE = False


# Logger for current test case
case_logger = None
# Application process
process = None


def close_process(process):
    try:
        child_processes = process.children()
        case_logger.info(f"Child processes: {child_processes}")
        for ch in child_processes:
            try:
                ch.kill()
            except NoSuchProcess:
                case_logger.info(f"Process is killed: {ch}")

        try:
            process.kill()
        except NoSuchProcess:
            case_logger.info(f"Process is killed: {process}")

        time.sleep(0.5)

        for ch in child_processes:
            try:
                status = ch.status()
                case_logger.error(f"Process is alive: {ch}. Name: {ch.name()}. Status: {status}")
            except NoSuchProcess:
                case_logger.info(f"Process is killed: {ch}")

        try:
            status = process.status()
            case_logger.error(f"Process is alive: {process}. Name: {process.name()}. Status: {status}")
        except NoSuchProcess:
            case_logger.info(f"Process is killed: {process}")
    except Exception as e:
        case_logger.error(f"Failed to close process: {str(e)}")
        case_logger.error(f"Traceback: {traceback.format_exc()}")


def open_tool(script_path, execution_script):
    global process

    with open(script_path, "w") as f:
        f.write(execution_script)

    if platform.system() == "Windows":
        pyautogui.hotkey("win", "m")
    else:
        pyautogui.hotkey("win", "d")
        os.system(f"chmod +x {script_path}")

    time.sleep(1)

    process = psutil.Popen(script_path, stdout=PIPE, stderr=PIPE, shell=True)

    time.sleep(3)

    window_hwnd = None
    application_window_found = False

    if platform.system() == "Windows":
        for window in pyautogui.getAllWindows():
            if "MaterialXView" in window.title:
                window_hwnd = window._hWnd
                application_window_found = True
                break
    else:
        process = subprocess.Popen("wmctrl -l", stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        windows = [" ".join(x.split()[3::]) for x in stdout.decode("utf-8").strip().split("\n")]

        for window in windows:
            if "MaterialXView" in window:
                application_window_found = True

    if not application_window_found:
        raise Exception("Application window not found")
    else:
        case_logger.info("Application window found")

    if platform.system() == "Windows":
        win32gui.ShowWindow(window_hwnd, win32con.SW_MAXIMIZE)

    time.sleep(3)


def post_action():
    try:
        close_process(process)
    except Exception as e:
        case_logger.error(f"Failed to do post actions: {str(e)}")
        case_logger.error(f"Traceback: {traceback.format_exc()}")


def create_case_logger(case_name, log_path):
    formatter = logging.Formatter(fmt=u'[%(asctime)s] #%(levelname)-6s [F:%(filename)s L:%(lineno)d] >> %(message)s')

    file_handler = logging.FileHandler(filename=os.path.join(log_path, f"{case_name}.log"), mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(f"{case_name}")
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    global case_logger
    case_logger = logger


def is_case_skipped(case, render_platform):
    if case["status"] == "skipped":
        return True

    if sum([render_platform & set(skip_conf) == set(skip_conf) for skip_conf in case.get("skip_config", "")]):
        for i in case["skip_config"]:
            skip_config = set(i)
            if render_platform.intersection(skip_config) == skip_config:
                return True

    return False 


def save_image(image_path, image_resolution=(1005, 452), offset=(0, -13)):
    resolution_x, resolution_y = get_resolution()

    border_x = int((resolution_x - image_resolution[0]) / 2)
    border_y = int((resolution_y - image_resolution[1]) / 2)

    image_region = (border_x + offset[0], border_y + offset[1], image_resolution[0] + border_x + offset[0], image_resolution[1] + border_y + offset[1])

    screen = pyscreenshot.grab(bbox=image_region)
    screen = screen.convert("RGB")
    screen.save(image_path)


def load_mesh(mesh_path):
    locate_and_click(MaterialXElements.LOAD_MESH.build_path())
    time.sleep(0.5)
    pyautogui.typewrite(mesh_path)
    pyautogui.press("enter")
    time.sleep(0.5)


def load_material(material_path):
    locate_and_click(MaterialXElements.LOAD_MATERIAL.build_path())
    time.sleep(0.5)
    pyautogui.typewrite(material_path)
    pyautogui.press("enter")
    time.sleep(0.5)


def load_environment(environment_path):
    locate_and_click(MaterialXElements.LOAD_ENVIRONMENT.build_path())
    time.sleep(0.5)
    pyautogui.typewrite(environment_path)
    pyautogui.press("enter")
    time.sleep(3)


def enable_environment_drawing():
    time.sleep(1)
    advanced_setting_location = locate_on_screen(MaterialXElements.ADVANCED_SETTINGS.build_path())
    click_on_element(advanced_setting_location)
    time.sleep(1)

    try:
        locate_and_click(MaterialXElements.DRAW_ENVIRONMENT.build_path())
    except:
        # MaterialX viewer can require som etime to load environment file
        time.sleep(15)
        click_on_element(advanced_setting_location)
        time.sleep(1)
        locate_and_click(MaterialXElements.DRAW_ENVIRONMENT.build_path())

    time.sleep(0.5)
    click_on_element(advanced_setting_location)
    time.sleep(0.5)


def locate_on_screen(template, tries=3, confidence=0.9, **kwargs):
    coords = None
    if not "confidence" in kwargs:
        kwargs["confidence"] = confidence
    while not coords and tries > 0 and kwargs["confidence"] > 0:
        case_logger.info("Trying to find {} on screen, confidence = {}".format(template, kwargs["confidence"]))
        with Image.open(template) as img:
            coords = pyautogui.locateOnScreen(img, **kwargs)
        tries -= 1
        kwargs["confidence"] -= 0.07
    if not coords:
        raise Exception("No such element on screen")
    return (coords[0], coords[1], coords[2], coords[3])


def move_to(x, y):
    case_logger.info("Move to x = {}, y = {}".format(x, y))
    pyautogui.moveTo(x, y)


def click_on_element(coords, x_offset=0, y_offset=0):
    x = coords[0] + coords[2] / 2 + x_offset
    y = coords[1] + coords[3] / 2 + y_offset
    pyautogui.moveTo(x, y)
    time.sleep(0.3)
    pyautogui.click()
    case_logger.info("Click at x = {}, y = {}".format(x, y))


def locate_and_click(template, tries=3, confidence=0.9, x_offset=0, y_offset=0, **kwargs):
    coords = locate_on_screen(template, tries=tries, confidence=confidence, **kwargs)
    click_on_element(coords, x_offset=x_offset, y_offset=y_offset)


def detect_render_finishing(max_delay=30):
    PREVIOUS_SCREEN_PATH = "previous_screenshot.jpg"
    CURRENT_SCREEN_PATH = "current_screenshot.jpg"

    def make_viewport_screenshot(screen_path):
        if os.path.exists(screen_path):
            os.remove(screen_path)

        resolution_x = win32api.GetSystemMetrics(0)
        resolution_y = win32api.GetSystemMetrics(1)

        # get center part of viewport
        viewport_resolution = (1000, 500)

        border_x = int(resolution_x / 2 - viewport_resolution[0])
        border_y = int(resolution_y / 2 - viewport_resolution[1])

        viewport_region = (border_x, border_y, resolution_x - border_x, resolution_y - border_y)

        screen = pyscreenshot.grab(bbox=viewport_region)
        screen = screen.convert("RGB")
        screen.save(screen_path)

    start_time = datetime.now()

    make_viewport_screenshot(PREVIOUS_SCREEN_PATH)

    while True:
        if (datetime.now() - start_time).total_seconds() > max_delay:
            raise RuntimeError("Break waiting of render finishing due to timeout")

        time.sleep(3)

        make_viewport_screenshot(CURRENT_SCREEN_PATH)

        metrics = CompareMetrics(PREVIOUS_SCREEN_PATH, CURRENT_SCREEN_PATH)
        prediction = metrics.getPrediction(mark_failed_if_black=True, max_size=20)

        # Viewport doesn't changed
        if prediction == 0:
            break

        make_viewport_screenshot(PREVIOUS_SCREEN_PATH)

def get_resolution():
    if platform.system() == "Windows":
        return win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    else:
        process = subprocess.Popen("xdpyinfo | awk '/dimensions/{print $2}'", stdout=PIPE, shell=True)
        stdout, stderr = process.communicate()
        resolution_x, resolution_y = stdout.decode("utf-8").strip().split("x")
        return int(resolution_x), int(resolution_y)
