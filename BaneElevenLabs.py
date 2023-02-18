import requests
import json
import datetime

import secrets # secrets.py stores the API key


def get_voices(cloned=False):
    url = f"https://api.elevenlabs.io/v1/voices"
    headers = {
        "accept": "application/json",
        "xi-api-key": secrets.xi
    }

    # send the request
    response = requests.get(url, headers=headers)

    # check if the request was successful
    if response.status_code == 200:
        # return a dict of {name: voice_id}
        my_dict = {}
        for voice in response.json()["voices"]:
            if cloned:
                if voice["category"] == "cloned":
                    my_dict[voice["name"]] = voice["voice_id"]
            else:
                my_dict[voice["name"]] = voice["voice_id"]
    
        return my_dict
    else:
        # print the error
        print(response.text)
        return "Something went wrong!"


def generate_audio(voice, message, stability, similarity_boost, file_name="audio.mp3", debug=False):

    if debug:
        print("Data")
        print(f"\tMessage: {message}")
        print(f"\tVoice: {voice}")
        print(f"\tStability: {stability}")
        print(f"\tSimilarity Boost: {similarity_boost}")


    # create the request
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": secrets.xi,
        "Content-Type": "application/json"
    }

    data = {
        "text": message,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    # send the request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # check if the request was successful
    if response.status_code == 200:
        # create a file to store the audio in in the audio folder
        with open(f"{file_name}", "wb") as f:
            f.write(response.content)
        return True
    else:
        # print the error
        print(response.text)
        return False



class User:
    def __init__(self, tier, character_count, character_limit, can_extend, reset_unix, voice_limit, sub_cost, sub_renew_unix):
        self.tier = tier
        self.characters_used = f"{character_count}/{character_limit}"
        self.character_remaining = character_limit - character_count
        self.can_extend = can_extend
        self.reset_unix = reset_unix
        self.reset_date = datetime.datetime.fromtimestamp(reset_unix).strftime("%Y-%m-%d %H:%M:%S")
        # time until reset in the format DD:HH:MM:SS
        until = datetime.datetime.fromtimestamp(reset_unix) - datetime.datetime.now()
        self.time_remaining = str(until).split(".")[0]
        voices_used = len(get_voices(cloned=True))
        self.voices_used = f"{voices_used}/{voice_limit}"
        self.sub_cost = sub_cost
        self.sub_renew_unix = sub_renew_unix
        self.sub_renew_date = datetime.datetime.fromtimestamp(sub_renew_unix).strftime("%Y-%m-%d %H:%M:%S")
        # time until sub renewal in the format DD:HH:MM:SS
        until = datetime.datetime.fromtimestamp(sub_renew_unix) - datetime.datetime.now()
        self.sub_time_remaining = str(until).split(".")[0]

    def __str__(self):
        output = ""
        output += "User Data:\n"
        output += f"  Characters Used:       {self.characters_used}\n"
        output += f"  Characters Remaining:  {self.character_remaining}\n"
        output += f"  Can Extend Limit:      {'Yes' if self.can_extend else 'No'}\n"
        output += f"  Reset Date:            {self.reset_date}\n"
        output += f"  Time Until Reset:      {self.time_remaining}\n"
        output += f"  Voices Used:           {self.voices_used}\n"
        output += "\nSubscription Data:\n"
        output += f"  Tier:                  {self.tier}\n"
        # convert cents to dollars
        output += f"  Sub Cost:              ${self.sub_cost / 100:.2f}\n"
        output += f"  Sub Renewal Date:      {self.sub_renew_date}\n"
        output += f"  Time Until Renewal:    {self.sub_time_remaining}\n"
        return output


def get_user_data():

    url = f"https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "accept": "application/json",
        "xi-api-key": secrets.xi
    }

    # send the request
    response = requests.get(url, headers=headers)

    # check if the request was successful
    if response.status_code == 200:
        # store the data in a User object
        data = response.json()
        user = User(data["tier"], data["character_count"], data["character_limit"], data["can_extend_character_limit"], data["next_character_count_reset_unix"], data["voice_limit"], data["next_invoice"]["amount_due_cents"], data["next_invoice"]["next_payment_attempt_unix"])
        return user



if __name__ == "__main__":
    print(get_user_data())

    # print(get_voices())

