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

## Sample Results

```code
2: [10]       dFA L"*Ppr 00cf1bcd1cd80e7ea91cf20e70ce8023f797ffb9ab77a5fb09fdfa838a00b4a7
3: [ 9]        <Zk2%B%Ul 0002dee7026e0e010ff15ea16a09a8a277102210e191d76f41ef1145b2527920
4: [ 6]           55Tw{J 00003f5f4a0cb51312e87e5c7fe4be1f99705d7823827c8ea4299d248064289a
5: [13]    3T68dUP7:;C/n 000006ce8aeeaf9944b78600bc4404d3cd7ed4ec4595a3315520caa4887558d5
6: [14]   pqN]?Au4LdmisB 0000001a560dcfaaaf286aa1becb23e9ce97c8608d6648d12fc25edeaf036e5b
7: [ 9]        S{y:'&J1r 000000015ae918277c493e5a0fd856a2a781380f8ebbae119b758a8c34cd80dd
```

## Web References

- [How to Set Up a Virtual Environment in Python](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
