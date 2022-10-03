from genericpath import exists
import subprocess
import os
import sys
from pathlib import Path

# new imports
import cv2
import os
import random

#Usage: python video_to_images.py --flags
#Flags: --ffmpeg_exe_path "path" ==> Path to the ffmpeg executeable.
#                                  > Defaults to looking for ffmpeg.exe in the folder this script is in.
#
#       --fps "number > 0"       ==> Number of frames to pull from each second of video. 0 will give
#                                  > all frames.
#                                  > Defaults to 0.
#
#       --name "name"            ==> Name of the folder to be created to store the data for this instance
#                                  > of ffmpeg.
#                                  > Defaults to "ffmpeg_output"
#
#       --output_folder "path"   ==> Directory to where ffmpeg will put its output.
#                                  > Defaults to the folder where this script is
#
#       --video_path "path"      ==> Path to the video to be converted into its composite images.
#                                  > Defaults to looking for "video.mp4" in the folder this script
#                                  > is in.



#split_video_into_frames function:
#
#creates a new folder called instance_name in output_path and fills it with the frames
#    of the video at video_path. Samples fps frames per second of video, or every
#    frame if fps = 0
#
#returns a status code - 
#    0 = Success
#    1 = Unspecified error
#    2 = FileExistsError; happens when you try to create data in an already existing folder
#    3 = FileNotFoundError; happens when you try to use an output folder that does not exist

def split_video_into_frames(instance_name, output_path, ffmpeg_path, video_path, fps=24):
    #Create our output folder
    if not output_path.endswith(("\\", "/")) and not instance_name.startswith(("\\", "/")):
        output_path = output_path + "/"
    instance_path = output_path + instance_name
    print(ffmpeg_path, "-i", video_path, "-vf", "fps=" , fps, instance_path + '/%04d.png')
    try:
        Path(f"{instance_path}").mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        return 2
    except FileNotFoundError:
        return 3
    except:
        print("BRUHHH")
        return 1


    ## determine video length:
    vidcap = cv2.VideoCapture(video_path + '.MOV')
    frame_count = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

    print(f"frames = {frame_count}")

    success, image = vidcap.read()
    count = 1

    ## treating fps variable as total images we want
    ## how do we get the total images we want? Use a probability!
    probability = (fps / frame_count)
    print(f"probability:{probability}")
    while success:
      random_number = random.uniform(0,1)
      if (random_number < probability):
        cv2.imwrite(f"{output_path}/image_{count}.png", image)  
        print('Saved image ', count)
      success, image = vidcap.read()
      count += 1



    #Run ffmpeg
    '''
    try:
      subprocess.call([ffmpeg_path, "-i", video_path, "-vf", "fps=" + str(fps), instance_path + '/%04d.png'])
    #except:
      return 1
    '''
    #Sucess, return 0
    return 0

def test():
  instance_name = "test"
  output_path = "test_out"
  ffmpeg_path = ""
  video_path = "airpodvideo"
  fps = 97
  split_video_into_frames(instance_name, output_path, ffmpeg_path, video_path, fps)

if __name__ == '__main__':
    #Default flags
    instance_name = "ffmpeg_output"
    output_path = "./"
    ffmpeg_path = r".\ffmpeg.exe"
    video_path = r".\video.mp4"
    fps = 24

    #Parse flags
    #Flag format up top
    """
    for i in range (len(sys.argv)):
        if i == 0:
            continue
        if sys.argv[i].startswith("--"):
            match sys.argv[i]:
                case "--output_folder":
                    output_path = sys.argv[i+1]
                case "--name":
                    instance_name = sys.argv[i+1]
                case "--ffmpeg_exe_path":
                    ffmpeg_path = sys.argv[i+1]
                case "--video_path":
                    video_path = sys.argv[i+1]
                case "--fps":
                    fps = sys.argv[i+1]
                case _:
                    print("ERROR: Unrecognized flag", sys.argv[i])
                    quit()"""
    
    #Calling split_video_into_frames
    status = split_video_into_frames(instance_name, output_path, ffmpeg_path, video_path, fps=fps)
    if status == 0:
        print("ffmpeg ran successfully.")
    elif status == 1:
        print("ERROR: There was an unknown error running ffmpeg")
    elif status == 2:
        print(f"ERROR: ffmpeg - file {output_path}/{instance_name} already exists.")
    elif status == 3:
        print(f"ERROR: ffmpeg - file {output_path} could not be found.")