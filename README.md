
# Pyenv install
```bash
curl https://pyenv.run | bash
sudo apt-get install build-essential zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev
pyenv install 3.10.10
pyenv virtualenv 3.10.10 pixel-battle
pyenv activate pixel-battle
```

# Project install
```bash
sudo apt install libpq-dev
sudo apt install postgresql postgresql-contrib
make install
```

# Run migrations
```bash
battlecli db upgrade
```
