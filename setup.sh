# !bin/sh
cd ~/Servers/fullyautomatednutcracker/src
python3 ./deploy_environment.py prod > "../logs/$(date +'%Y-%m-%d_%Hh%Mm').console.log" 2>&1 &
ps ax | grep environment.py
