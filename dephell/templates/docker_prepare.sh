set -e
apt-get update -yq
apt-get install -yq zsh python3 python3-dev python3-pip mc glances zsh-syntax-highlighting wget

# oh my zsh
wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh
chmod +x install.sh
yes | ./install.sh --silent
echo "\nplugins=(colorize command-not-found django celery git pip pipenv python)\n" >> ~/.zshrc
rm install.sh

# pure zsh theme
wget https://raw.githubusercontent.com/sindresorhus/pure/master/pure.zsh
wget https://raw.githubusercontent.com/sindresorhus/pure/master/async.zsh
mv pure.zsh /usr/local/share/zsh/site-functions/prompt_pure_setup
mv async.zsh /usr/local/share/zsh/site-functions/async
echo "\nautoload -U promptinit\npromptinit\nprompt pure\n" >> ~/.zshrc

# dephell
python3 -m pip install -U pip
wget https://raw.githubusercontent.com/dephell/dephell/master/install.py
# pip can't update itself from the first try >.<
bash -c "python3 install.py || python3 install.py"
rm install.py
dephell autocomplete
