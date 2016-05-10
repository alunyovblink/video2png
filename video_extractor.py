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

    # video title
    title = ''

    # video url
    download_url = ''

    # size
    width = None
    height = None

    # file
    video_dirpath = ''
    video_filepath = ''

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
          raise VideoPNGExtractorError("Size should be set as pair of Width and Height")

        # Set password
        if 'password' in args: self.password = args['password']

        # Set URL.
        self.download_url = download_url

    def create_work_folder(self, video_title):
        video_dirpath = os.path.join(VIDEO_PNG_DIR, video_title)
        if not os.path.exists(video_dirpath):
            os.makedirs(video_dirpath)

        self.video_dirpath = video_dirpath

    def load(self):
        path = self.download_url

        if not os.path.isfile(path):
            raise VideoPNGExtractorError("Selected file is not readable")

        self.video_filepath = path
        video_filename = os.path.basename(path)
        video_title = os.path.splitext(video_filename)[0]
        self.title = video_title
        self.create_work_folder(video_title)

    def download(self):
        # Get video meta info and then download using youtube-dl

        # @TODO: Add to options auth if provided.
        ydl_opts = {}

        # Get meta data of the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(self.download_url, download=False)

        self.title = meta['title']

        # renaming the file
        # remove special characters from the file name
        video_title = ''.join(c for c in meta['title'] if c.isalnum() or c == '-' or c == '_')
        extension = meta['ext']
        video_filename = video_title + '.' + extension

        # create the folder for video
        self.create_work_folder(video_title)

        # create the full path for video file
        video_filepath = os.path.join(self.video_dirpath, video_filename)

        #
        cmd = ['youtube-dl', '-k', '-o', video_filepath, self.download_url]

        # if height was set then setting filter format for video
        if self.height is not None:
            filter_format = 'bestvideo[height <=? %(height)i]+bestaudio/best[height <=? %(height)i]' % {
                "height": self.height}
            cmd.extend(['-f', filter_format])

        print("request=%s" % cmd)

        # download the video
        subprocess.call(cmd)

        # set file path
        self.video_filepath = video_filepath

    def extract_frames(self):
        # setting png files names
        png_filepath = os.path.join(self.video_dirpath, VIDEO_PNG_FRAME_NAME)

        # collecting video filtering options
        #video_filter = "select='eq(pict_type,PICT_TYPE_I)'";
        video_filter = "select='gt(scene\, 0.005)'";

        # setting scale options
        # width scale
        if self.width is None or self.width <= 0:
            width = -1
        else:
            width = self.width

        # height scale
        if self.height is None or self.height <= 0:
            height = -1
        else:
            height = self.height

        # adding scale options to video filtering
        if width <> -1 and height <> -1:
            scale = "scale='if(gt(a,%(width)i/%(height)i),%(width)i,-1)':'if(gt(a,%(width)i/%(height)i),-1,%(height)i)'" % {"width" : width, "height" : height}
            video_filter += ",%(scale)s" % {"scale" : scale}

        cmd = ['ffmpeg', '-i', self.video_filepath, '-f', 'image2', '-vf', video_filter, '-vsync', 'vfr', png_filepath]

        print("creating frames...");
        print(cmd);

        # create iframes
        subprocess.call(cmd)

class VideoPNGExtractorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main(argv):
    extractor = VideoPNGExtractor('temp/test.mp4', {'width': 1024, 'height': 720});
    #extractor = VideoPNGExtractor('temp/test.mp4');
    extractor.load()

    extractor.extract_frames()

if __name__ == "__main__":
	main(sys.argv[1:])