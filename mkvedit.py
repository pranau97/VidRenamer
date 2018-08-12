'''
Script to batch edit MKV files' metadata.
Current plans include -
 * Edit filename, file title, directory
 * Batch rename folders
 * Provide customizable renaming schemes.

REQUIRES - mkvpropedit, mediainfo
'''

import os
import argparse
import logging
import subprocess
from glob import glob
from file import File
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def clrscr():
    # Method to clear the terminal screen
    _ = os.system('cls' if os.name == 'nt' else 'clear')


def process_individual(mkv_list):
    # Method to process and set values to a file one by one.

    # List to store all the video file objects
    videos = []

    for i in mkv_list:
        videos.append(File(i))

    process_count = 1
    update_count = 0
    # Store whether user wants to continue processing or not
    stop_flag = False
    # Store the total videos to process
    total = len(videos)
    # List to store all the modified videos
    updated_videos = []

    for video in videos:
        while True:
            log.info("Processing file no. " + str(process_count))

            print("File {0} of {1}".format(
                process_count, total))
            print("Path: ", video.current_path)
            print("Filename: ", video.current_filename)
            print("MKV segment title: ", video.current_metadata_title)

            temp = input(
                "Enter the new MKV segment title "
                "(Press ENTER to skip, \\ to copy filename) ")
            if not temp:
                temp = None
            elif temp == '\\':
                updated_videos.append(video)
                update_count += 1
            else:
                video.set_metadata_title = temp
                updated_videos.append(video)
                update_count += 1

            process = input(
                "Press r to redo, s to stop processing, e to exit, "
                "ENTER to continue ")
            if not process:
                pass
            elif process.lower() == 'r':
                update_count -= 1
                continue
            elif process.lower() == 's':
                stop_flag = True
            elif process.lower() == 'e':
                log.info("Forced exit by user.")
                return 0

            process_count += 1
            clrscr()
            break

        if stop_flag:
            break
        stop_flag = False

    total_updated = len(updated_videos)
    print("About to apply changes to {0} videos.".format(
        total_updated))
    for video in updated_videos:
        print(video.current_filename, ": ")
        print(video.current_metadata_title, "->", video.set_metadata_title)
    process = input("Continue? (y/n) ")

    if process.lower() in ["yes", "y"]:
        for video in updated_videos:
            clrscr()
            video.apply_changes()
            log.info("Applied change for video - " + str(video.current_path))
        print("Applied changes to {0} videos.".format(
            total_updated))
    else:
        print("Changes discarded.")

    if not input("Press ENTER to continue"):
        return 0
    else:
        log.warning("Non-standard exit.")
        return 0


def run(dirpath):
    # Method that manages the script lifecycle and activities

    # Accept a path if not entered via the command line
    wd = dirpath or input("Enter the directory path to the file(s): ")

    # Check if it is a valid directory and change
    # current working directory to it
    if os.path.isdir(wd):
        os.chdir(wd)
    else:
        log.error("Directory not found.")
        return 1

    # Recursively search the current working directory and subdirectories
    # for files ending with a .mkv extension
    mkv_list = [y for x in os.walk(os.getcwd())
                for y in glob(os.path.join(x[0], '*.mkv'))]

    mode = input("Single mode or pattern mode? (s/p) ")
    if mode.lower() in ["single", "s"]:
        status_code = process_individual(mkv_list)
    elif mode.lower() in ["pattern", "p"]:
        pass
    else:
        log.error("Invalid processing option.")
        return 1

    if status_code:
        log.error("Error while processing files")
        return 1
    else:
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch edit MKV files's metadata")
    parser.add_argument(
        '-p',
        '--path',
        default=None,
        help='Enter the directory path to the file(s) to edit.')
    args = parser.parse_args()

    while True:
        status_code = run(args.path)
        args.path = None
        if status_code:
            print("Error encountered.")

        process = input("Restart? (y/n) ")
        if process.lower() in ['yes', 'y']:
            log.info("Restarting...")
            continue
        else:
            log.info("Exiting...")
            break
