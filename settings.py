import platform
# settings.py

# Replace with your actual Trading212 API key
API_KEY = "30566783ZckaphEhLbzjJbDoKRojsKYvjuYGf"

server = 'missiondatabase.database.windows.net'
database = 'mission_sandbox'
username = 'missionuser'
password = 'Connect@123'

if platform.system() == 'Darwin':
    #paramaters for MacOS
    filepath='/workarea/files/' 
else:
    #parameters for windows
    filepath = 'C:\\workarea\\files\\'

