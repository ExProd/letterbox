#!/usr/bin/python

'''Scale and letterbox a video file using ffprobe and ffmpeg via subprocess.

Requires ffprobe/ffmpeg to be installed on host machine.
Will scale files to 1280x720 if they are already 1280x720 or smaller.
Will scale files to 1920x1080 if their width is larger than 1280.

Examples:
    Command-line:
        $ python letterbox.py path/to/file
    Module:
        >>> import letterbox
        >>> letterbox.main(path/to/file)

'''

import sys
import os
import subprocess
import json
from fractions import gcd


def is_16_9(video_path):
    '''Check if video is 16:9 using ffprobe.'''

    p = subprocess.Popen(['ffprobe',
                          '-v', 'error',
                          '-show_entries',
                          'stream=width,height',
                          '-of', 'json',
                          video_path],
                          stdout=subprocess.PIPE)
    result = p.communicate()
    aspect_info = json.loads(result[0])
    # Create tuple of resolution i.e. (1280, 720)
    resolution = (int(aspect_info['streams'][0]['width']),
                  int(aspect_info['streams'][0]['height']))

    # Check if video is 16:9
    if not (gcd(resolution[0], 16) == 16 and gcd(resolution[1], 9) == 9):
        return resolution
    return True


def scale_and_letterbox(video_path, resolution):
    '''Scale video and add letterbox to make 16:9

    Args:
        video_path (str): Path to video file.
        resolution (tuple): Original video resolution formatted as (width, height).

    '''

    new_path = os.path.join(os.path.dirname(video_path),
                            'LETTERBOXED_' + os.path.basename(video_path))

    if resolution[0] <= 1280:
        width = 1280
        height = 720
    else:
        width = 1920
        height = 1080

    p = subprocess.Popen(['ffmpeg',
                          '-i', video_path,
                          '-filter:v',
                          ('scale=(sar*iw)*min({width}/(sar*iw)\,{height}/ih)'
                           ':ih*min({width}/(sar*iw)\,{height}/ih), '
                           'pad={width}:{height}:({width}-(sar*iw)*min'
                           '({width}/(sar*iw)\,{height}/ih))/2:({height}-'
                           'ih*min({width}/(sar*iw)\,'
                           '{height}/ih))/2').format(width=width,
                                                    height=height),
                           new_path])
    p.communicate()
    return new_path


def main(video_path):
    '''Main function - Check resolution and scale/letterbox if not 16:9

    Args:
        video_path (str): Path to video file.

    '''

    resolution = is_16_9(video_path)
    if resolution[0]:
        print 'Already 16:9, doing nothing.'
        return

    scale_and_letterbox(video_path, resolution[1])


if __name__ == '__main__':
    try:
        video_path = sys.argv[1]
    except IndexError:
        print 'Enter filepath of video as argument please!'
        sys.exit()
    main(video_path)
