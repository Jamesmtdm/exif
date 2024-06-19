import telebot
import subprocess
import os
import random
import string
from telebot import types
from PIL import Image
import numpy as np

API_TOKEN = os.getenv('API_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))
INVITE_LINK = 'https://t.me/+BsyQHjdkn9IyYTlk'
bot = telebot.TeleBot(API_TOKEN)

mode = None

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type != 'private':
        return

    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            markup = types.InlineKeyboardMarkup()
            change_button = types.InlineKeyboardButton(text="Change Metadata", callback_data="change_metadata")
            remove_button = types.InlineKeyboardButton(text="Remove Metadata", callback_data="remove_metadata")
            spoof_button = types.InlineKeyboardButton(text="Spoof Media", callback_data="spoof_media")
            markup.add(change_button, remove_button, spoof_button)
            bot.send_message(message.chat.id, "Welcome to the Metadata Bot! Choose an option:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f'You must be a member of the group to use this bot. Please join here: {INVITE_LINK}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: Unable to verify membership. Please join the group here: {INVITE_LINK}')

@bot.callback_query_handler(func=lambda call: call.data in ["change_metadata", "remove_metadata", "spoof_media"])
def callback_query(call):
    global mode
    if call.message.chat.type != 'private':
        return

    bot.answer_callback_query(call.id, f"Selected option: {call.data.replace('_', ' ').title()}")
    mode = call.data
    bot.send_message(call.message.chat.id, "Send me an image or video to process.")

@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_media(message):
    if message.chat.type != 'private':
        return

    user_id = message.from_user.id

    try:
        member = bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            bot.send_message(message.chat.id, f'You must be a member of the group to use this bot. Please join here: {INVITE_LINK}')
            return
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: Unable to verify membership. Please join the group here: {INVITE_LINK}')
        return

    global mode
    if mode is None:
        bot.send_message(message.chat.id, "Please select an option first using the provided buttons.")
        return

    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        elif message.content_type == 'video':
            file_info = bot.get_file(message.video.file_id)
        elif message.content_type == 'document':
            file_info = bot.get_file(message.document.file_id)
        else:
            bot.send_message(message.chat.id, "Unsupported file type.")
            return

        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        local_file_path = os.path.join('downloads', os.path.basename(file_path))
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        with open(local_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        if mode == 'change_metadata' or mode == 'spoof_media':
            exiftool_command = [
                'exiftool',
                f'-Artist={random_string()}',
                f'-Author={random_string()}',
                f'-Description={random_string()}',
                f'-Title={random_string()}',
                f'-Creator={random_string()}',
                f'-Subject={random_string()}',
                f'-Comment={random_string()}',
                f'-Copyright=© {random.randint(2000, 2025)} {random_string()}',
                f'-Software={random_string()}',
                f'-Make={random_string()}',
                f'-Model={random_string()}',
                '-overwrite_original',
                local_file_path
            ]
            subprocess.run(exiftool_command)

        if mode == 'remove_metadata':
            if message.content_type == 'photo' or message.document.mime_type.startswith('image/'):
                exiftool_command = ['exiftool', '-all=', '-overwrite_original', local_file_path]
            else:
                exiftool_command = ['ffmpeg', '-i', local_file_path, '-map_metadata', '-1', '-c:v', 'copy', '-c:a', 'copy', local_file_path]
            subprocess.run(exiftool_command)

        if mode == 'spoof_media':
            if message.content_type == 'photo' or message.document.mime_type.startswith('image/'):
                spoof_image(local_file_path)
            else:
                spoof_video(local_file_path)

        output_file = local_file_path

        with open(output_file, 'rb') as edited_file:
            bot.send_document(message.chat.id, edited_file)

        os.remove(local_file_path)
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred: " + str(e))

def spoof_image(file_path):
    with Image.open(file_path) as img:
        pixels = np.array(img)
        for _ in range(10):
            x, y = random.randint(0, pixels.shape[1] - 1), random.randint(0, pixels.shape[0] - 1)
            pixels[y, x] = [random.randint(0, 255) for _ in range(3)]
        img = Image.fromarray(pixels)
        img.save(file_path)
        exiftool_command = [
            'exiftool',
            f'-Artist={random_string()}',
            f'-Author={random_string()}',
            f'-Description={random_string()}',
            f'-Title={random_string()}',
            f'-Creator={random_string()}',
            f'-Subject={random_string()}',
            f'-Comment={random_string()}',
            f'-Copyright=© {random.randint(2000, 2025)} {random_string()}',
            f'-Software={random_string()}',
            f'-Make={random_string()}',
            f'-Model={random_string()}',
            '-overwrite_original',
            file_path
        ]
        subprocess.run(exiftool_command)

def spoof_video(file_path):
    temp_output = "temp_" + os.path.basename(file_path)
    subprocess.run(['ffmpeg', '-i', file_path, '-c:v', 'copy', '-c:a', 'copy', temp_output])
    os.rename(temp_output, file_path)

# Clone the required repository
os.system('git clone https://github.com/Anish-M-code/Metadata-Remover.git')
os.chdir('Metadata-Remover')

bot.polling()
