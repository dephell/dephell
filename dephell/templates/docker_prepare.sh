set -e
apt-get update -yq
apt-get install -yq zsh python3 python3-dev python3-pip mc glances zsh-syntax-highlighting wget

# oh my zsh
wget -O /tmp/install.sh https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh
chmod +x /tmp/install.sh
yes | /tmp/install.sh --silent
echo "\nplugins=(colorize command-not-found django celery git pip pipenv python)\n" >> ~/.zshrc
rm /tmp/install.sh

# pure zsh theme
wget https://raw.githubusercontent.com/sindresorhus/pure/master/pure.zsh
wget https://raw.githubusercontent.com/sindresorhus/pure/master/async.zsh
mv pure.zsh /usr/local/share/zsh/site-functions/prompt_pure_setup
mv async.zsh /usr/local/share/zsh/site-functions/async
echo "\nautoload -U promptinit\npromptinit\nprompt pure\n" >> ~/.zshrc

# dephell
python3 -m pip install -U pip
wget -O /tmp/install.py https://raw.githubusercontent.com/dephell/dephell/master/install.py
bash -c "python3 /tmp/install.py"
rm /tmp/install.py
# dephell autocomplete
