'''
Module that defines the Matroska class and its member methods.

The Matroska class describes a mkv video. It holds the current path, filename
and title of a video and the corresponding values set by the user while
editing the video.

Requires - mediainfo, mkvpropedit
'''


import os
import logging
import subprocess

# Configure the logger object and set logging level
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("matroska")


class Matroska:
    # Class to handle all the operations related to a single mkv video file

    def __init__(self, filepath):
        # Store the current filename
        self.current_filename = os.path.basename(filepath)
        # Store the filename set by the user
        self.set_filename = os.path.basename(filepath)
        # Store the current path
        self.current_path = filepath
        # Store the path entered by the user
        self.set_path = filepath

        # Fetch the current title from the file metadata using mediainfo
        file_metadata = subprocess.run(
            ["mediainfo --Inform=\"General;%Title%\" \"" + filepath + "\""],
            universal_newlines=True,
            shell=True,
            stdout=subprocess.PIPE
        )
        log.debug(file_metadata)

        # Store the current title
        if not file_metadata.stdout:
            self.current_metadata_title = "N/A"
        else:
            self.current_metadata_title = file_metadata.stdout.splitlines()[0]
        # Store the title entered by the user
        self.set_metadata_title = self.current_metadata_title

    def update_fields(self):
        # Method to apply the new values to the video

        # Build the string to call mkvpropedit and set the metadata correctly
        shell_command = ''.join(["mkvpropedit \"",
                                 self.current_path,
                                 "\" --edit info --set \"title=",
                                 self.set_metadata_title,
                                 "\""]
                                )

        # Call mkvpropedit and set the metadata
        result = subprocess.run(
            [shell_command],
            universal_newlines=True,
            shell=True,
            stdout=subprocess.PIPE
        )

        # If the returned is 0, edit was successful
        if result.returncode == 0:
            return 0
        # If 1, there was a warning generated
        if result.returncode == 1:
            log.warning("mkvpropedit: " + result.stdout)
            log.warning(self.current_path)
            return 1
        # Else, the edit failed and there was an error
        log.error("mkvpropedit:" + result.stdout)
        log.error(self.current_path)
        return 2
