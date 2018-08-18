#! /usr/bin/python3.6
'''
Script to batch edit video files' metadata.
Can currently perform the following
 * Edit filename, file title, directory
 * Batch rename folders
 * Provide customizable renaming schemes.

 TODO: * Add subtitle renaming support
       * Add mp4, avi, etc support
       * Add support for downloading subtitles
       * Add support for automatically fetching info

Requires - mkvpropedit, mediainfo, mutagen
'''

import os
import argparse
from glob import glob
from ast import literal_eval
from _clrscr import clrscr
from _logs import error, warning, debug
from _normalize_path import normalize_path
from _colors import COLOR
from file_mkv import Matroska


def apply_changes(videos):
    '''Method to apply changes to queued edits'''

    # Store the total number of edited videos
    total_updated = len(videos)
    # Display the queued videos to be modified
    print("About to apply changes to {0} videos.".format(
        total_updated))
    for video in videos:
        print(video.current_filename + ":")
        if video.current_path != video.set_path:
            print("New path: " + video.set_path)
        if video.current_metadata_title != video.set_metadata_title:
            print("New title: " + video.set_metadata_title)
    process = input("Continue? (y/n) ")
    clrscr()

    if process.lower() in ["yes", "y"]:
        for video in videos:
            status_code = video.update_metadata_fields()
            # Raise an error and stop further processing on error
            if status_code == 2:
                return 1
            debug("Applied change for video - " +
                  str(video.current_path), "run")

        for video in videos:
            status_code = video.update_file_fields()
            # Raise an error and stop further processing on error
            if status_code == 1:
                return 1
            debug("Renamed video - " + str(video.current_path), "run")

        print("Applied changes to {0} videos.".format(
            total_updated))
    else:
        debug("Changes discarded.", "run")
        print("Changes discarded.")

    if not args.no_restart:
        input("Press ENTER to continue")
    return 0


def process_individual(video_list):
    '''Method to process all the video files in a given directory
    and give the user the option to edit them one by one
    '''

    # List to store all the video file objects
    videos = []

    # Instantiate objects to store the video data
    for file in video_list:
        videos.append(Matroska(os.getcwd() + "/" + file))

    process_count = 1
    update_count = 0
    # Store whether user wants to continue processing or not
    stop_flag = False
    # Store the total videos to process
    total = len(videos)
    # List to store all the modified videos
    updated_videos = []

    # Accept user inputs for the files
    for video in videos:
        while True:
            debug("Processing file no. " + str(process_count), "run")

            print("File {0} of {1}".format(
                process_count, total))
            print("Path: ", video.current_path)
            print("Filename: ", video.current_filename)
            print("Video title: ", video.current_metadata_title)

            temp = input(
                "Enter the new video path "
                "(Press ENTER to skip)"
            )
            if temp:
                path = normalize_path(temp)
                if path == 1:
                    return 1
                video.set_path = temp
                video.set_filename = os.path.basename(video.set_path)

            temp = input(
                "Enter the new video title "
                "(Press ENTER to skip, \\ to copy filename) "
            )
            if temp == '\\':
                video.set_metadata_title = os.path.splitext(
                    video.set_filename)[0]
            elif temp:
                video.set_metadata_title = temp

            if (video.current_filename != video.set_filename) or (
                    video.current_metadata_title != video.set_metadata_title):
                updated_videos.append(video)
                update_count += 1
            process = input(
                "Press r to redo, s to stop processing, e to exit, "
                "ENTER to continue "
            )
            if process.lower() == 'r':
                update_count -= 1
                continue
            elif process.lower() == 's':
                stop_flag = True
            elif process.lower() == 'e':
                debug("Forced exit by user.", "run")
                return 0

            process_count += 1
            clrscr()
            break

        # Stop the loop to proceed to applying the changes
        if stop_flag:
            break
        stop_flag = False

    # Call the function to apply the edits that have been made if any
    if len(updated_videos) > 0:
        status_code = apply_changes(updated_videos)
    else:
        status_code = 0
    return status_code


def process_batch_metadata(video_list):
    '''Method to process all the video files in a directory and
    give the user the option to edit them in a batch
    '''

    # Accept pattern to edit metadata
    if not args.m_pattern:
        print(
            COLOR["CYAN"] + "METADATA PATTERN" + COLOR["END"] + "\n"
            "{dir:d} - directory based numbering, {file:d} file based numbering" + "\n"
            "Example - Person of Interest S{dir:02d}E{file:02d} -> Person of Interest S01E01"
        )
    m_pattern = args.m_pattern or input(
        "Enter the metadata pattern (\\ to skip) ")
    debug(m_pattern, "run")

    # Accept metadata to edit filenames
    if not args.f_pattern:
        print(
            COLOR["CYAN"] + "FILE PATTERN" + COLOR["END"] + "\n"
            "{dir:d} - directory based numbering, {file:d} file based numbering" + "\n"
            "Example - Person of Interest S{dir:02d}E{file:02d}.mkv -> "
            "Person of Interest S01E01.mkv\n"
            "Pattern must translate to a valid path"
        )
    f_pattern = args.f_pattern or input("Enter the file pattern (\\ to skip) ")
    debug(f_pattern, "run")

    # Store the list of videos in the current directory
    videos = []
    for file in video_list:
        videos.append(Matroska(os.getcwd() + "/" + file))

    # Accept custom offsets for filenames and metadata
    # TODO: Add support for per directory file offsets
    if args.offset == "True":
        directory_offset = input("Enter directory offset (optional) ") or 1
        file_offset = input("Enter file offset (optional) ") or 1
    elif args.offset == "False":
        directory_offset = 1
        file_offset = 1
    else:
        try:
            # Try literal evaluation of the argument and store in tuple
            tup = literal_eval(args.offset)
        except:
            error("Invalid offsets passed.", "run")
            return 1
        directory_offset = tup[0]
        file_offset = tup[1]

    # Store current video's current path
    current_path = os.path.dirname(videos[0].current_path)
    for video in videos:
        # Increment directory offset and reset file offset when
        # the directory of the previous video doesn't match the current
        if os.path.dirname(video.current_path) != current_path:
            current_path = os.path.dirname(video.current_path)
            directory_offset += 1
            file_offset = 1
            debug(current_path, "run")
        if m_pattern != "\\":
            video.set_metadata_title = m_pattern.format(
                dir=directory_offset, file=file_offset)
        if f_pattern != "\\":
            path = normalize_path(f_pattern.format(
                dir=directory_offset, file=file_offset
            ))
            # Return if the path is invalid
            if path == 1:
                return 1
            video.set_path = path
            video.set_filename = os.path.basename(video.set_path)
        file_offset += 1

    # Call function to apply the changes
    status_code = apply_changes(videos)

    return status_code


def run():
    '''Method that manages the script lifecycle and activities'''

    # Accept a path if not entered via the command line
    wd = args.path or input("Enter the directory path to the file(s): ")
    wd = os.path.expanduser(wd)
    if os.path.isdir(wd) or os.path.isdir(os.getcwd() + wd):
        os.chdir(wd)
    else:
        error("Directory not found.", "run")
        return 1

    # Recursively search the current working directory and subdirectories
    # for files ending with a .mkv extension
    video_list = []
    mkv_list = glob('**/*.mkv', recursive=True)
    # mp4_list = glob('**/*.mp4', recursive=True)
    # avi_list = glob('**/*.mp4', recursive=True)
    video_list.extend(mkv_list)
    # video_list.extend(mp4_list)
    # video_list.extend(avi_list)
    video_list.sort()

    ''' Prompt user input to run the script in one of two currently supported
        modes.
        1 - Single mode. This mode looks for all mkv files in a given directory
        and gives the user the option to edit them one by one.
        2 - Batch mode. This mode lets the user specify a pattern or rule
        which will be used to edit the mkv files in the given directory.
    '''
    process = args.mode or input("Single mode or batch mode? (s/b) ")
    if process.lower() in ["single", "s"]:
        clrscr()
        status_code = process_individual(video_list)
    elif process.lower() in ["batch", "b"]:
        clrscr()
        status_code = process_batch_metadata(video_list)
    else:
        error("Invalid processing option.", "run")
        return 1

    if status_code == 1:
        return 1

    return 0


if __name__ == "__main__":
    # Initialize the argument parsing library
    parser = argparse.ArgumentParser(
        description="Batch edit video files' metadata")
    # TODO: Add more command line arguments to automate the script
    # Add argument to directly launch the script with a path
    # instead of interactively accepting it via user input
    parser.add_argument(
        '-p',
        '--path',
        default=None,
        help='specify the directory path to the file(s) to edit.'
    )
    # Add argument to supply metadata pattern to be used while
    # performing batch edits
    parser.add_argument(
        '-x',
        '--m_pattern',
        default=None,
        help='specify the metadata pattern to be used in batch edits'
    )
    # Add argument to supply metadata pattern to be used while
    # performing batch edits
    parser.add_argument(
        '-y',
        '--f_pattern',
        default=None,
        help='specify the metadata pattern to be used in batch edits'
    )
    # Add argument to specify directory and file offset
    parser.add_argument(
        '-o',
        '--offset',
        default='True',
        help='specify true (default), false, or specific offset in '
        '\"(dir, file)\" format'
    )
    # Add argument to terminate the script after 1 run
    parser.add_argument(
        '-n',
        '--no_restart',
        action='store_true',
        help='don\'t restart the script after a batch job is complete.'
    )
    # Add argument to specify which mode to run the script in
    parser.add_argument(
        '-m',
        '--mode',
        default=None,
        help='specify the mode to run the script in - single or batch.'
    )
    args = parser.parse_args()
    debug(str(args), "run")

    while True:
        status_code = run()
        if status_code == 1:
            print("The script encountered an error.")

        # Reset the value for the next iteration so that the path
        # can be accepted via user input
        args.path = None

        if args.no_restart:
            break
        process = input("Restart? (y/n) ")
        if process.lower() in ['yes', 'y']:
            debug("Restarting...", "run")
            clrscr()
            continue
        else:
            debug("Exiting...", "run")
            break
