'''
Module that defines the Matroska class and its member methods.

The Matroska class describes a mkv video. It holds the current path, filename
and title of a video and the corresponding values set by the user while
editing the video.

Requires - mediainfo, mkvpropedit
'''


import os
import subprocess
from _logs import error, warning, debug


class Matroska:
    '''Class to handle all the operations related to a single mkv video file'''

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
        debug(str(file_metadata), "matroska")

        # Check if the mediainfo command ran successfully
        # by looking at the return code
        if file_metadata.returncode:
            warning("Mediainfo failed to run correctly.", "matroska")

        # Store the current title
        if file_metadata.returncode or file_metadata.stdout == '\n':
            self.current_metadata_title = "N/A"
        else:
            self.current_metadata_title = file_metadata.stdout.splitlines()[0]
        # Store the title entered by the user
        self.set_metadata_title = self.current_metadata_title

    def update_metadata_fields(self):
        '''Method to apply the new metadata values to the video'''

        # Build the string to call mkvpropedit and set the metadata correctly
        shell_command = ''.join(["mkvpropedit \"",
                                 self.current_path,
                                 "\" --edit info --set \"title=",
                                 self.set_metadata_title,
                                 "\""]
                                )
        result = subprocess.run(
            [shell_command],
            universal_newlines=True,
            shell=True,
            stdout=subprocess.PIPE
        )

        if result.returncode == 0:
            self.current_metadata_title = self.set_metadata_title
            return 0
        if result.returncode == 1:
            warning("mkvpropedit: " + result.stdout, "matroska")
            warning(self.current_path, "matroska")
            self.current_metadata_title = self.set_metadata_title
            return 1
        error("mkvpropedit:" + result.stdout, "matroska")
        error(self.current_path, "matroska")
        return 2

    def update_file_fields(self):
        '''Method to apply the new filename and path to the video'''

        try:
            os.renames(self.current_path, self.set_path)
            self.current_path = self.set_path
            self.current_filename = self.set_filename
        except OSError:
            error("Failed to rename the file", "matroska")
            error(self.current_path, "matroska")
            return 1

        return 0
