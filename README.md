# WoW Vox
A quest voiceover framework for World of Warcraft using Python

This is a Python script that uses computer vision and natural language processing techniques to generate voiceovers for the quest descriptions in World of Warcraft. The script captures a screenshot of the game client, extracts the text of the quest accepted message using optical character recognition (OCR) with Tesseract-OCR, and then uses the quest ID to scrape the quest description from the WoWhead website using aiohttp and BeautifulSoup.

After the quest description is obtained, the script uses the Google Cloud Text-to-Speech API to generate a voiceover for the quest description, which is saved as an audio file. The script then uses PyAudio to play the voiceover, providing the player with an audio description of the quest.

The script also uses Selenium to scrape the WoWhead website for the NPC name and gender associated with the quest, which is then used to select the appropriate voice for the Text-to-Speech API. The script uses chromedriver to automate the browser, and BeautifulSoup to parse the HTML of the website.

In terms of functionality, this script is intended to make the process of understanding quests in World of Warcraft easier and more accessible for players who may have visual or reading difficulties. The script uses computer vision and natural language processing to automatically extract and describe quest information, reducing the cognitive load on the player and allowing them to focus on playing the game itself.

That's how I'd describe the project if I asked ChatGPT to write a detailed description for it.. but of course, I'd never do that!
Jokes aside, this is a pet project of mine made for fun, inspired by the classic VoiceOver addon (https://www.curseforge.com/wow/addons/voiceover).
This is an extremely early version, and I don't promise to keep updating, or refining it. (Although I have a lot of functions and bugfixes, improvements in mind still.) Which is why I decided to just put it out here and make it open-source. I made this in about two days, so do what you will with it.

There's two versions, normal and lite.
Normal version: The normal version includes extracting the quest npc's gender data and using that to generate voices appropriate to the gender. -However-, this version comes with a lot of delay between opening up the quest details, to receiving the voice over. I'll be looking into workarounds or fixes for this delay.
Lite version: This version has a single voice option for both male and female npcs. -But-, it loads almost instantly as you open up the quest details, having no delay.
Decide for yourself which one you want to install. Prerequisites vary between the two.

If there's any interest, I'll look to make this an easy-to-use app, with varying voices for different races, and eliminate the delay in the normal version.
As for now, this project is available with an as-is basis and I don't guarantee it to work. Make sure to report any bugs. I'm sure there's many.

# HOW TO INSTALL
(This is quite a complicated procedure for someone who has no experience with Python and such. I apologize for that, and if there's any demand, I will make this an easy to use app instead.)

(If you're experienced, you can ignore anything code related and just copy the repo, of course.)

(note: this guide implies you're on a windows machine)

Prerequisites:
1. Python: https://www.python.org/downloads/
2. A lot of Python modules, bash this into the terminal: "pip install cv2 numpy pygetwindow requests google-cloud-texttospeech pyaudio wave asyncio aiohttp bs4 Pillow mss selenium"
3. A Google Cloud Account (free account is fine): https://cloud.google.com/free
4. Tesseract-OCR: https://github.com/UB-Mannheim/tesseract/wiki
5. Chrome Browser and chromedriver (SKIP FOR LITE VERSION, THIS IS ONLY NEEDED FOR NORMAL INSTALLATION): https://www.google.com/chrome/, https://sites.google.com/chromium.org/driver/
6. A simple, custom WoW addon that outputs quest-id to chat by viewing the quest details: https://www.dropbox.com/s/y3ihxtp79bjsksr/QuestIDLogger.rar?dl=0
7. WoW client (why am i even including this)

After downloading and installing all the prerequisites, you will need to go into your -Google Cloud Account-, create a new project, and enable TTS api. While we're here, we're also gonna download a .json key file required by the script.
1. Once you're logged in, create a new project by clicking the dropdown menu on the top left corner of the screen and selecting "New Project"
2. Click on "APIs & Services" tab in the left-hand menu
3. Click on the "Credentials" tab in the left-hand menu
4. Create a service account
5. Edit the service account
6. Click on the "Keys" menu at the top
7. Click on "Add Key", and create a JSON key. Remember where this gets downloaded, as you will need to use it's path later.
8. Enable the Cloud TTS API here: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/metrics
9. YOU'RE DONE! with the google account part.. at least.. im so sorry.

Now, you should add the custom addon to your WoW. This works the same way as any other addon installation.
1. Extract the folder
2. Add QuestIDLogger folder into your World of Warcraft\_retail_\Interface\AddOns folder. (If you're not on retail, just ignore the retail part.)

After all of that, you can compile your own version of the code by creating a WowVox.py or WowVoxLite.py file and copying my code's contents into it.
IMPORTANT: Edit the code to change the Google TTS Api key with your own, and the tesseract executable's location. Line 23 and 25 on the normal version, and line 17 and 19 on the lite version.

Then with Git Bash, just write "python WowVox.py" or "python WowVoxLite.py" and it should run. If everything works as intended, the console output should be bombarded with "questcandidatenotfound" until you accept a quest.
As soon as you click on a quest, it should immediately (lite version), or with some delay (normal version) read out the text description for you.

If you're a complete newbie and have no clue what you're doing but for some reason desperately want to get this to work, hmu on Discord: **Kelathis#3855**

Have fun.
