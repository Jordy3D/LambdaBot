import os
import requests
import json
import datetime

import secrets # secrets.py stores the API key

import CandyConsole2 as CC


supports_colour = False


def pad(string, length, char=" ", right=False):
    if right:
        return string + char * (length - len(string))
    else:
        return char * (length - len(string)) + string



def __request(url=None, headers=None, response_data="json"):
    if not url:
        return None
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            if response_data == "json":
                return response.json(), response.status_code
            else:
                return response, response.status_code
        
    except:
        return None, 408
        

def get_voices(cloned=False):
    url = f"https://api.elevenlabs.io/v1/voices"
    headers = {
        "accept": "application/json",
        "xi-api-key": secrets.xi
    }
    
    data, status = __request(url, headers=headers)
    
    if data == None:
        return f"Request error. Status code: {status}"

    my_dict = {}
    for voice in data["voices"]:
        if cloned:
            if voice["category"] == "cloned":
                my_dict[voice["name"]] = voice["voice_id"]
        else:
            my_dict[voice["name"]] = voice["voice_id"]

    return my_dict

    
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
    def __init__(self, tier, character_count, character_limit, can_extend, reset_unix, voice_limit, sub_cost=None, sub_renew_unix=None):
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
        if sub_cost is not None:
            self.sub_renew_unix = sub_renew_unix
            self.sub_renew_date = datetime.datetime.fromtimestamp(sub_renew_unix).strftime("%Y-%m-%d %H:%M:%S")
            # time until sub renewal in the format DD:HH:MM:SS
            until = datetime.datetime.fromtimestamp(sub_renew_unix) - datetime.datetime.now()
            self.sub_time_remaining = str(until).split(".")[0]

    def __str__(self):
        output = ""

        heading_styles = [CC.TextStyles.BOLD, CC.TextStyles.ITALICS]
        heading_pad = 22

        global supports_colour

        output += print_swap("Generation Data:", CC.TextStyles.BOLD, supports_colour) + "\n"

        output += print_swap(pad("Characters Used: ", heading_pad), heading_styles, supports_colour) + f"{self.characters_used}\n"
        output += print_swap(pad("Characters Left: ", heading_pad), heading_styles, supports_colour) + f"{self.character_remaining}\n"
        output += print_swap(pad("Can Extend Limit: ", heading_pad), heading_styles, supports_colour) + f"{'Yes' if self.can_extend else 'No'}\n"
        output += print_swap(pad("Reset Date: ", heading_pad), heading_styles, supports_colour) + f"{self.reset_date}\n"
        output += print_swap(pad("Time Until Reset: ", heading_pad), heading_styles, supports_colour) + f"{self.time_remaining}\n"
        output += print_swap(pad("Voices Used: ", heading_pad), heading_styles, supports_colour) + f"{self.voices_used}\n"

        output += print_swap("Subscription Data:", CC.TextStyles.BOLD, supports_colour) + "\n"
        output += print_swap(pad("Tier: ", heading_pad), heading_styles, supports_colour) + f"{self.tier}\n"
        if self.sub_cost is not None:
            output += print_swap(pad("Sub Cost: ", heading_pad), heading_styles, supports_colour) + f"{self.sub_cost}\n"
            output += print_swap(pad("Renewal Date: ", heading_pad), heading_styles, supports_colour) + f"{self.sub_renew_date}\n"
            output += print_swap(pad("Time Until Renewal: ", heading_pad), heading_styles, supports_colour) + f"{self.sub_time_remaining}\n"

        return output


def get_user_data():

    url = f"https://api.elevenlabs.io/v1/user/subscription"
    headers = {
        "accept": "application/json",
        "xi-api-key": secrets.xi
    }

    data, status = __request(url, headers=headers)
    
    if data == None:
        return f"Request error. Status code: {status}"
    
    try:
        user = User(data["tier"], data["character_count"], data["character_limit"], data["can_extend_character_limit"], data["next_character_count_reset_unix"], data["voice_limit"], data["next_invoice"]["amount_due_cents"], data["next_invoice"]["next_payment_attempt_unix"])
    except:
        # if the above fails, it's because the user doesn't have a subscription
        user = User(data["tier"], data["character_count"], data["character_limit"], data["can_extend_character_limit"], data["next_character_count_reset_unix"], data["voice_limit"], None, None)
    
    return user


class History:
    # contains history_item_id, voice_id, voice_name, text, date_unix, content_type, character_count_change_from, character_count_change_to
    def __init__(self, history_item_id, voice_id, voice_name, text, date_unix, content_type, character_count_change_from, character_count_change_to):
        self.history_item_id = history_item_id
        self.voice_id = voice_id
        self.voice_name = voice_name
        self.text = text
        self.data_unix = date_unix
        self.date = datetime.datetime.fromtimestamp(date_unix).strftime("%Y-%m-%d %H:%M:%S")
        self.content_type = content_type
        self.character_count = character_count_change_to - character_count_change_from

    def __str__(self):
        output = ""

        heading_styles = [CC.TextStyles.BOLD, CC.TextStyles.ITALICS]
        heading_pad = 22

        global supports_colour
        output += print_swap(pad("History Item ID: ", heading_pad), heading_styles, supports_colour) + f"{self.history_item_id}\n"

        text_output = CC.split_message(self.text, 50)
        text_field = ""

        for i, line in enumerate(text_output):
            if i == 0:
                out_line = print_swap(pad("Text: ", heading_pad), heading_styles, supports_colour) + f"{line}"
                text_field += f"{out_line}\n"
            else:
                out_line = pad("", heading_pad) + f"{line}"
                if out_line.startswith(" "):
                    text_field += f"{out_line}\n"
                    # print(f"Output: {out_line}")
                else:
                    print("Error: line doesn't start with a space")

        output += text_field

        output += print_swap(pad("Character Count: ", heading_pad), heading_styles, supports_colour) + f"{self.character_count}\n"
        output += print_swap(pad("Voice ID: ", heading_pad), heading_styles, supports_colour) + f"{self.voice_id}\n"
        output += print_swap(pad("Voice Name: ", heading_pad), heading_styles, supports_colour) + f"{self.voice_name}\n"
        output += print_swap(pad("Date: ", heading_pad), heading_styles, supports_colour) + f"{self.date}\n"
        output += print_swap(pad("Content Type: ", heading_pad), heading_styles, supports_colour) + f"{self.content_type}\n"

        return output


def get_history():
    url = f"https://api.elevenlabs.io/v1/history"
    headers = {
        "accept": "application/json",
        "xi-api-key": secrets.xi
    }

    data, status = __request(url, headers=headers)

    history = []
    
    if data == None:
        return f"Request error. Status code: {status}"
    
    for item in data["history"]:
        history.append(History(item["history_item_id"], item["voice_id"], item["voice_name"], item["text"], item["date_unix"], item["content_type"], item["character_count_change_from"], item["character_count_change_to"]))

    return history


def print_swap(text, styles, supports_colour=False):
    if supports_colour:
        return CC.candy_colour(text, styles)
    else:
        return text



if __name__ == "__main__":
    # check if code is running in CMD or Powershell in os.environ.keys()
    # if "TERM_PROGRAM" in os.environ.keys():

    if any("vscode" in name.lower() for name in os.environ):
        # if it is, use the Windows colorama module
        supports_colour = True

    print(print_swap("ElevenLabs API Test", [CC.TextStyles.BOLD], supports_colour))

    user_data = get_user_data()
    print(user_data)
    
    print(print_swap("History Data", [CC.TextStyles.BOLD], supports_colour))
    history = get_history()    
    print(history[105])

    # clone = user_data.tier != "free"
    # print(get_voices(cloned=clone))

