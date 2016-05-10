#!/usr/bin/env python
# Copyright (c) 2016, alunyov
# All rights reserved.

'''
Contains class VideoExtractor for extracting png from mp4, mkv, webm videos.
'''

import youtube_dl
import sys, os
import subprocess

# Define work folder.
VIDEO_PNG_DIR = 'files'
VIDEO_PNG_FRAME_NAME = 'screen_%6d.png'

class VideoPNGExtractor:
    extension_list = ['mkv', 'mp4', 'webm']

    # video url
    download_url = ''

    # size
    width = None
    height = None

    # auth
    password = None

    def __init__(self, download_url = '', args = {}):
        # check if python modules are installed: youtube-dl
        # check if ffmpeg is installed
        # throw exception if no

        # Set width.
        if 'width' in args: self.width = args['width']

        # Set height.
        if 'height' in args: self.height = args['height']

        #if (self.width is None and self.height is not None) or (self.width is not None and self.height is None):
        if bool(self.width is not None) ^ bool(self.height is not None):
          raise VideoPNGExtractorError("Size should be set as pair of Width and Height");

        # Set password
        if 'password' in args: self.password = args['password']

        # Set URL.
        self.download_url = download_url

    def download(self):
        # Get video meta info and then download using youtube-dl

        # @TODO: Add to options auth if provided.
        ydl_opts = {}

        # Get meta data of the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(self.download_url, download=False)

        # renaming the file
        # remove special characters from the file name
        video_title = ''.join(c for c in meta['title'] if c.isalnum() or c == '-' or c == '_')
        extension = meta['ext']
        video_filename = video_title + '.' + extension

        # create the folder for video
        video_dirpath = os.path.join(VIDEO_PNG_DIR, video_title);
        if not os.path.exists(video_dirpath):
            os.makedirs(video_dirpath);

        # create the full path for video file
        video_filepath = os.path.join(video_dirpath, video_filename);

        #
        cmd = ['youtube-dl', '-k', '-o', video_filepath, self.download_url];

        filter_format = None
        if self.height is not None:
            filter_format = 'bestvideo[height <=? %(height)i]+bestaudio/best[height <=? %(height)i]' % {
                "height": self.height}
            cmd.extend(['-f', filter_format]);

        #cmd.extend(['-k', '-o', video_filename, self.download_url]);

        print("request=%s" % cmd)

        # download the video
        subprocess.call(cmd)

        return meta

    def validate_video(self):
        print ""

    def extract_frames(self, path):
        print ""

class VideoPNGExtractorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main(argv):
    #extractor = VideoPNGExtractor('https://vimeo.com/164152168', {'height' : 370});
    #extractor = VideoPNGExtractor('https://vimeo.com/164152168', {'width': 320, 'height': 540});
    #extractor = VideoPNGExtractor('https://vimeo.com/164152168', {'width': 320, 'height': 360});
    extractor = VideoPNGExtractor('https://vimeo.com/164152168', {'width': 320, 'height': 720});
    extractor.download();

if __name__ == "__main__":
	main(sys.argv[1:])