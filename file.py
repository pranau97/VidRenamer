'''
Module that defines the File class and its member methods.

The File class describes a video. It holds the current path, filename
and title of a video and the corresponding values set by the user while
editing the video.

Requires - mediainfo, mkvpropedit
'''


import os
import logging
import subprocess
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class File:
    # Class to handle all the operations related to a single video file

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
            stdout=subprocess.PIPE)
        log.debug(file_metadata)

        # Store the current title
        if not file_metadata.stdout:
            self.current_metadata_title = "N/A"
        else:
            self.current_metadata_title = file_metadata.stdout.splitlines()[0]
        # Store the title entered by the user
        self.set_metadata_title = self.current_metadata_title

    def apply_changes(self):
        '''Applies the new values for the video file.'''
        pass
