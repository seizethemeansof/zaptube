# Zaptube

Browse randomly through Youtube, video clips of maximum 5 seconds with statics between them.

## DISCLAIMER

This script is using an Internet connection to fetch video data from Youtube. If you have limited data plan, better not use it too much as I am not sure about the real data consumption.

## Requirements

The dependencies can be installed from the requirements.txt file with the following command:

```bash
pip install -r requirements.txt
```

## Usage
Issue the following command

```bash
python app.py
```

It will start a Flask server available at the following http://127.0.0.1:5000/

After navigating to that address, the video should start after a while, after approximatively 10 to 15 seconds.

To stop the program, press Ctrl + C multiple times until (hopefully) it stops.