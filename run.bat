@echo off
:restart
python3 "scraper.py" -v
pause
goto:restart