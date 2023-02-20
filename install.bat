@ECHO OFF

@TITLE Prepare and Install
ECHO Installing requirements...
pip install -r requirements.txt

ECHO Creating secrets.py...
IF NOT EXIST secrets.py (
    ECHO token = 'YOUR DISCORD TOKEN HERE' >> secrets.py
    ECHO xi = 'YOUR ELEVENLABS TOKEN HERE' >> secrets.py
    ECHO. >> secrets.py
    ECHO test_guilds = [YOUR GUILD ID HERE] >> secrets.py
    ECHO owners = [YOUR USER ID HERE, YOUR USER ID HERE] >> secrets.py
)