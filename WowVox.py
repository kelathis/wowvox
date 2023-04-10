import numpy as np
import pygetwindow as gw
from google.cloud import texttospeech
import pyaudio
import wave
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image
from mss import mss
import subprocess
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # run selenium in headless mode
driver = webdriver.Chrome(options=options)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"c:\yourownpath\googlekey.json" # <- path to your google key json file
client = texttospeech.TextToSpeechClient()
tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # don't forget to change this to your own tesseract path

def capture_screenshot():
    window = gw.getWindowsWithTitle('World of Warcraft')[0]
    x, y, width, height = window.left, window.top, window.width, window.height

    # note: my screen is 2560x1400. change this to your own res
    quarter_width = 1920 // 14
    quarter_height = 1080 // 14

    # adjusted the coordinates to capture the bottom-left quarter of the screen
    left = x
    top = y + (height - quarter_height)
    right = x + quarter_width
    bottom = y + height

    with mss() as sct:
        monitor = {"top": top, "left": left, "width": quarter_width, "height": quarter_height}
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return np.array(img)

def extract_quest_accepted_text(screenshot):
    img = Image.fromarray(screenshot)
    img.save('temp_screenshot.png')
    
    result = subprocess.run([tesseract_cmd, 'temp_screenshot.png', 'stdout', '--psm', '6'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    os.remove('temp_screenshot.png')
    return result.stdout

def find_quest_accepted(text):
    if text is not None:
        # preprocess the text
        text = text.replace('\n', ' ').replace('\r', ' ').strip()
        text = ' '.join(text.split())

        # finding the line that contains "Quest"
        lines = text.split('.')
        for line in lines:
            if "Quest" in line and "has" in line:
                # extract the quest ID from the line
                quest_id = ''.join(filter(str.isdigit, line[line.index("Quest") + len("Quest"):]))
                if len(quest_id) <= 10:
                    return quest_id

        # quest ID not found
        print("questcandidatenotfound")  # debug
        return None
    else:
        print("questcandidatenotfound")  # debug
        return None

async def get_quest_text(quest_id, retries=3):
    print(f"Getting quest text for ID: {quest_id}")  # debug

    for attempt in range(retries):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.wowhead.com/quest={quest_id}") as response:
                text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        desc_header = soup.find('h2', class_='heading-size-3', string='Description')

        if desc_header is not None:
            description_parts = []
            for sibling in desc_header.next_siblings:
                if isinstance(sibling, str):
                    description_parts.append(sibling.strip())
                elif sibling.name == 'br':
                    description_parts.append('\n')
                elif sibling.name == 'h2' and sibling.get_text(strip=True) == 'Rewards':
                    break  # stop processing siblings when encountering the "Rewards" header
            description = ''.join(description_parts)
            print(f"Quest description: {description}")  # debug
            
            # remove the <name> placeholder from the quest text
            description = description.replace("<name>", "")
            
            return description

        print(f"Attempt {attempt + 1}: Can't get description") # debug
        await asyncio.sleep(1)

    return None

def get_npc_name(quest_id):
    url = f"https://www.wowhead.com/quest={quest_id}"
    driver.get(url)  # selenium gets url (idk why i commented on this)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    infobox = soup.find("div", {"id": "infobox-contents-0"})
    if infobox:
        print("infobox found")  # debug
        ul_element = infobox.find("ul")
        if ul_element:
            print("ul element found")  # debug
            li_elements = ul_element.find_all('li')
            for li_element in li_elements:
                npc_link_element = li_element.find('a', href=lambda href: href and "/npc=" in href)
                if npc_link_element:
                    npc_link = npc_link_element['href']
                    print(npc_link)  # debug

                    # extract and format the NPC name
                    npc_name = npc_link.split('/')[-1].replace('-', ' ').title()
                    print(npc_name)

                    # break the loop after finding the first NPC (it otherwise gets both the quest starter, and ender npc)
                    break
        else:
            print("ul element not found")  # debug
    else:
        print("infobox not found")  # debug

    start_npc_element = soup.select_one('#infobox-contents-0 a[href*="/npc="]')
    if start_npc_element:
        npc_name = start_npc_element.get_text(strip=True)
        print(f"Starting NPC: {npc_name}")  # debug
        return npc_name
    else:
        print("Starting NPC not found")  # debug
    
def get_npc_gender(npc_name):
    # perform the search mm yes
    search_url = f"https://wowpedia.fandom.com/wiki/Special:Search?scope=internal&query={quote_plus(npc_name)}&ns%5B0%5D=0&ns%5B1%5D=110&ns%5B2%5D=114&ns%5B3%5D=2900"
    print(search_url)
    driver.get(search_url)

    # click on the first search result
    wait = WebDriverWait(driver, 10)
    first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".unified-search__results a.unified-search__result__title")))
    if first_result:
        print("first result found")
    else: print("search unsuccessful")
    driver.execute_script("arguments[0].click();", first_result)

    # get the page source and parse it with BeautifulSoup (i love soup)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    infobox = soup.find('table', class_='infobox')
    if infobox:
        print("gender infobox found")
        gender_data = infobox.find('th', string='Gender')
        if gender_data:
            print("gender found")
            gender = gender_data.find_next_sibling('td').text.strip()
            return gender
    print("gender data unsuccessful")
    return None

def generate_voiceover(quest_text, gender):
    print(f"Generating voiceover for: {quest_text}")  # debug
    input_text = texttospeech.SynthesisInput(text=quest_text)
    voice_name = "en-US-News-M" if gender == "Female" else "en-GB-Neural2-F" # change this if you want different voices for different genders
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name=voice_name)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

    with open("voiceover.wav", "wb") as out:
        out.write(response.audio_content)

    return "voiceover.wav"

def play_voiceover(file_path):
    wf = wave.open(file_path, "rb")
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    stream.stop_stream()
    stream.close()
    p.terminate()

async def main():
    encountered_quest_ids = set()
    
    while True:
        screenshot = capture_screenshot()
        text = extract_quest_accepted_text(screenshot)
        quest_id = find_quest_accepted(text)

        if quest_id and quest_id not in encountered_quest_ids:
            encountered_quest_ids.add(quest_id)
            print(f"Quest ID detected: {quest_id}")  # debug
            quest_text = await get_quest_text(quest_id)
            if quest_text:
                npc_name = get_npc_name(quest_id)
                npc_gender = None
                if npc_name:
                    npc_gender = get_npc_gender(npc_name)
                voiceover_path = generate_voiceover(quest_text, npc_gender)
                play_voiceover(voiceover_path)

        await asyncio.sleep(1)

asyncio.run(main())