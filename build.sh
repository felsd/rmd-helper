#!/bin/sh
python -m nuitka --follow-imports rmd-helper.py
sudo mv rmd-helper.bin /usr/local/bin/rmd-helper
sudo chmod +x /usr/local/bin/rmd-helper
