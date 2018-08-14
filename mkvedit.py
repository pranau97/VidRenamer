'''
Script to batch edit video files' metadata.
Current plans include -
 * Edit filename, file title, directory
 * Batch rename folders
 * Provide customizable renaming schemes.

Requires - mkvpropedit, mediainfo, mutagen
'''

import os
import argparse
import logging
import subprocess
# import mutagen
from glob import glob
from clrscr import clrscr
from file_mkv import Matroska

# Configure the logger object and set logging level
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("run")


def apply_changes(videos):
    # Method to apply changes to queued edits

    # Store the total number of edited videos
    total_updated = len(videos)
    # Display the queued videos to be modified
    print("About to apply changes to {0} videos.".format(
        total_updated))
    for video in videos:
        print(video.current_filename, ": ")
        print(video.current_metadata_title, "->", video.set_metadata_title)
    # Prompt for confirmation
    process = input("Continue? (y/n) ")
    clrscr()

    # If user agrees, apply changes
    if process.lower() in ["yes", "y"]:
        # Apply changes made to the videos iteratively
        for video in videos:
            status_code = video.update_fields()
            # Raise an error and stop further processing on error
            if status_code == 2:
                return 1
            # Continue silently if there is no error reported
            log.debug("Applied change for video - " + str(video.current_path))

        # Confirm that changes have been applied
        print("Applied changes to {0} videos.".format(
            total_updated))
    # Else, discard all changes and return
    else:
        log.debug("Changes discarded.")
        print("Changes discarded.")

    # Prompt for user input to continue
    input("Press ENTER to continue")
    return 0


def process_individual(mkv_list):
    # This method takes all the mkv files in a given directory
    # and gives the user the option to edit them one by one.

    # TODO: Split the method into smaller pieces

    # List to store all the video file objects
    videos = []

    # Instantiate objects to store the video data
    for i in mkv_list:
        videos.append(Matroska(i))

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
            log.debug("Processing file no. " + str(process_count))

            # Print file info
            print("File {0} of {1}".format(
                process_count, total))
            print("Path: ", video.current_path)
            print("Filename: ", video.current_filename)
            print("MKV segment title: ", video.current_metadata_title)

            # Accept user input for the new video title
            temp = input(
                "Enter the new MKV segment title "
                "(Press ENTER to skip, \\ to copy filename) "
            )
            # Process the input
            # If the input is empty, do nothing
            if not temp:
                pass
            # If the input is a '\', copy the filename without the extension
            # to the title field
            elif temp == '\\':
                video.set_metadata_title = os.path.splitext(
                    video.set_filename)[0]
                updated_videos.append(video)
                update_count += 1
            # Else, set the user input as the value of the title field
            else:
                video.set_metadata_title = temp
                updated_videos.append(video)
                update_count += 1

            # Confirm whether user wants to proceed with the
            # next files or quit
            process = input(
                "Press r to redo, s to stop processing, e to exit, "
                "ENTER to continue "
            )
            # Process the input
            # If the input is empty, go to the next file
            if not process:
                pass
            # If the input is r, redo the edit process for the current file
            elif process.lower() == 'r':
                update_count -= 1
                continue
            # If the input is s, stop the process and proceed directly to
            # applying the changes made so far
            elif process.lower() == 's':
                stop_flag = True
            # If the input is e, terminate the current edit job completely
            elif process.lower() == 'e':
                log.info("Forced exit by user.")
                return 0
            # Do nothing and proceed to the next file, otherwise
            else:
                pass

            process_count += 1
            clrscr()
            break

        # Stop the loop to proceed to applying the changes
        if stop_flag:
            break
        stop_flag = False

    # Call the function to apply the edits that have been made
    if len(updated_videos) > 0:
        status_code = apply_changes(updated_videos)
    else:
        status_code = 0
    return status_code


def run(dirpath):
    # Method that manages the script lifecycle and activities

    # Accept a path if not entered via the command line
    wd = dirpath or input("Enter the directory path to the file(s): ")
    wd = os.path.expanduser(wd)
    # Check if it is a valid directory and change
    # current working directory to it
    if os.path.isdir(wd) or os.path.isdir(os.getcwd() + wd):
        os.chdir(wd)
    else:
        log.error("Directory not found.")
        return 1

    # Recursively search the current working directory and subdirectories
    # for files ending with a .mkv extension
    mkv_list = glob('**/*.mkv', recursive=True)
    # mp4_list = glob('**/*.mp4', recursive=True)
    # avi_list = glob('**/*.mp4', recursive=True)

    ''' Prompt user input to run the script in one of two currently supported
        modes.
        1 - Single mode. This mode looks for all mkv files in a given directory
        and gives the user the option to edit them one by one.
        2 - Pattern mode. This mode lets the user specify a pattern or rule
        which will be used to edit the mkv files in the given directory.
    '''
    process = input("Single mode or batch mode? (s/b) ")
    # If single is selected, call process_individual()
    if process.lower() in ["single", "s"]:
        clrscr()
        status_code = process_individual(mkv_list)
    # If pattern is selected, call process_pattern()
    elif process.lower() in ["batch", "b"]:
        clrscr()
        pass
    # Else, raise an error for providing an invalid option
    else:
        log.error("Invalid processing option.")
        return 1

    # Raise an error if the status code returned by any of the editing
    # methods is non-zero
    if status_code == 1:
        log.error("Error while processing files")
        return 1

    return 0


if __name__ == "__main__":
    # Add config for the argument parsing library
    parser = argparse.ArgumentParser(
        description="Batch edit video files' metadata")
    # TODO: Add more command line arguments to automate the script
    # Add argument to directly launch the script with a path
    # instead of interactively accepting it via user input
    parser.add_argument(
        '-p',
        '--path',
        default=None,
        help='Enter the directory path to the file(s) to edit.'
    )
    # Add argument to terminate the script after 1 run
    parser.add_argument(
        '-r',
        '--no_restart',
        action='store_true',
        help='Stop restarting the script after a batch job is complete.'
    )
    # Parse the command line arguments
    args = parser.parse_args()

    while True:
        status_code = run(args.path)
        # Raise an error on non-zero status code returned by run()
        if status_code == 1:
            print("The script encountered an error.")
            log.error("Error encountered.")

        # Reset the value for the next iteration so that the path
        # can be accepted via user input
        args.path = None

        # Accept user input to restart the script to edit new files if not
        # already specified in the command line
        if args.no_restart:
            break
        process = input("Restart? (y/n) ")
        if process.lower() in ['yes', 'y', False]:
            log.debug("Restarting...")
            clrscr()
            continue
        else:
            log.debug("Exiting...")
            break
