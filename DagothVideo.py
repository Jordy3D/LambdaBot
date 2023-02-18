import os

def dagoth_video(audio_path, image_path, output_file, debug=False):

    # if image_path does not have quotes, add them
    image_path = f"{image_path}" if image_path.startswith("\"") else f"\"{image_path}\""
    # if audio_path does not have quotes, add them
    audio_path = f"{audio_path}" if audio_path.startswith("\"") else f"\"{audio_path}\""
    # if output_file does not have quotes, add them
    output_file = f"{output_file}" if output_file.startswith("\"") else f"\"{output_file}\""

    # store complicated ffmpeg command flags in variables
    loglevel = "" if debug else "-loglevel quiet"
    filter = f"-vf \"crop=trunc(iw/2)*2:trunc(ih/2)*2\""
    video = "-c:v libx264 -tune stillimage -pix_fmt yuv420p"
    audio = "-c:a aac -b:a 192k"
    shortest = "-shortest -fflags +shortest -max_interleave_delta 100M"

    command = f"ffmpeg -y -loop 1 -i {image_path} -i {audio_path} {filter} {video} {audio} {shortest} {loglevel} {output_file}"

    if debug:
        print("\nCommand:")
        print(command)
        print()

    os.system(command)


if __name__ == "__main__":
    # get path to audio file
    audio_path = input("Enter audio path: ")
    # get path to image file
    image_path = input("Enter image path: ")
    # get output file name
    output_file = input("Enter output file name: ")

    dagoth_video(audio_path, image_path, output_file, debug=True)