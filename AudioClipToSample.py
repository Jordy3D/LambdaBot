import os
import random

# get folder path from user
folder_path = input("Enter path to clip folder: ")

file_count = 3
clip_count = 40

audio_formats = ["mp3", "wav", "ogg", "flac", "m4a"]

def generate_file(output_name, folder_path, clip_count):

    # get all files in folder
    clips = os.listdir(folder_path)

    # create a list of all files in folder
    clip_list = []

    # loop through all files in folder
    for clip in clips:
        ext = str(clip).split(".")[-1]
        if ext in audio_formats:
            # add file to list
            clip_list.append(f"{folder_path}/{clip}")

    print(f"Found {len(clip_list)} clips")

    all = False
    # get 60 random files from list, with no duplicates
    if len(clip_list) < clip_count:
        all = True
        clip_count = int(len(clip_list) / 4)
    random_clips = random.sample(clip_list, clip_count)

    concat_string = ""

    for clip in random_clips:
        concat_string += f"-i \"{clip}\" -i s.wav -i s.wav "

    filter_string = ""
    for i in range(file_count):
        filter_string += f"[{i}:0]"

    filter_string += f"concat=n={clip_count}:v=0:a=1[out]"


    command = f"ffmpeg {concat_string} -filter_complex \"{filter_string}\" -map \"[out]\" -y {output_name}.wav"
    print(command)

    # combine silence and random files, overwriting existing file
    os.system(command)


# for the number of files to generate
for i in range(file_count):
    # generate a file
    generate_file(f"sample{i + 1}", folder_path, clip_count)