if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/akrcreation2/Ak-FILTER-BOT4.git /shobanafilterbot
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /shobanafilterbot
fi
cd /shobanafilterbot
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
