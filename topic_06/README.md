# Topic 6

## OpenCL Environment

```bash
# create tje environment
python3 -m venv /Users/foulds/code/dsm070-2022-apr/topic_06
source /Users/foulds/code/dsm070-2022-apr/topic_06/bin/activate

# upgrade pip and install the wheel packages
cd /Users/foulds/code/dsm070-2022-apr/topic_06/
python3 -m pip install --upgrade pip
pip install wheel

# install the required packages
pip install -r requirements.txt
```

### Linux Config

```bash
sudo apt-get install python3-venv

# create the environment
export DSM070_SRC=$HOME/code/dsm070-2022-apr
export DSM070_ENV=$HOME/env/dsm070

mkdir $HOME/env
mkdir $DSM070_ENV
python3 -m venv $DSM070_ENV
source $DSM070_ENV/bin/activate

# install the required packages
cd $DSM070_SRC/topic_06
pip install wheel
pip install -r requirements.txt
```

### Windows Config

```powershell
$DSM070_SRC="$HOME\code\dsm070-2022-apr"
$DSM070_ENV="$HOME\env\dsm070"

mkdir "$HOME\env"
mkdir $DSM070_ENV

Set-ExecutionPolicy RemoteSigned

python3 -m venv $DSM070_ENV
cd "$DSM070_ENV\Scripts\"
.\activate
pip install --upgrade pip

cd "$DSM070_SRC\topic_06"
pip install wheel
pip install -r requirements.txt
```

## Web References

- [How to Set Up a Virtual Environment in Python](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
