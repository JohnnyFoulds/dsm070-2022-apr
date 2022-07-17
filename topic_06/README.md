# Topic 6

## OpenCL Environment

```bash
# create tje environment
python3 -m venv /Users/foulds/code/dsm070-2022-apr/topic_06
source /Users/foulds/code/dsm070-2022-apr/topic_06/bin/activate

# upgrade pip and install the wheel packages
cd /Users/foulds/code/dsm070-2022-apr/topic_06/

# source ~/env/dsm070/bin/activate
# rm -rf ~/env/opencl
# python3 -m venv ~/env/opencl
# source ~/env/opencl/bin/activate
#pip install --upgrade pip==22.1.1
#pip install wheel==0.37.1 setuptools==44.0.0 pybind11==2.9.2 

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

#### NVIDIA Container Platform

https://linuxhandbook.com/setup-opencl-linux-docker/
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
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

## pyOpenCL Build

```bash
# install the libraries if building in linux
apt-get install ocl-icd-libopencl1 \
    opencl-headers \
    pocl-opencl-icd \
    ocl-icd-dev \
    ocl-icd-opencl-dev \
    clinfo

# for the m1 platform do the following, or change it to the correct one for your machine
# x86_64-linux-gnu
sudo ln -s /usr/lib/aarch64-linux-gnu/libOpenCL.so.1 /usr/lib/libOpenCL.so

#pip install wheel==0.37.1 setuptools==44.0.0 pybind11==2.9.2 
pip install wheel==0.37.1 pybind11==2.9.2 
wget https://files.pythonhosted.org/packages/23/ce/02f9588cb19cfcbd75f299545b1625a060b1ee10f0542557b7786995f3e5/pyopencl-2022.1.6.tar.gz
tar -xf pyopencl-2022.1.6.tar.gz 
cd pyopencl-2022.1.6
python setup.py bdist_wheel --universal 
```

## Sample Results

```code
this is a description of the latest block

1: [ 4]             Gtb0 039edd9a95361ebeaf5b1ea8e886b67560b7b21d0a29495f68ed5330d1d15044
2: [10]       dFA L"*Ppr 00cf1bcd1cd80e7ea91cf20e70ce8023f797ffb9ab77a5fb09fdfa838a00b4a7
3: [ 9]        <Zk2%B%Ul 0002dee7026e0e010ff15ea16a09a8a277102210e191d76f41ef1145b2527920
4: [ 6]           55Tw{J 00003f5f4a0cb51312e87e5c7fe4be1f99705d7823827c8ea4299d248064289a
5: [13]    3T68dUP7:;C/n 000006ce8aeeaf9944b78600bc4404d3cd7ed4ec4595a3315520caa4887558d5
6: [14]   pqN]?Au4LdmisB 0000001a560dcfaaaf286aa1becb23e9ce97c8608d6648d12fc25edeaf036e5b
7: [ 9]        S{y:'&J1r 000000015ae918277c493e5a0fd856a2a781380f8ebbae119b758a8c34cd80dd
8: [ 8]         "?@~{-V9 0000000069988e1a731d7f4db1c3e0ea60725970938bebbd6b5d79cd40fef3aa
9: [14]   *jTi0@!N{oOaQf 000000000a71c29b450284efe6325204d4f3b8867a25db00373fe5b90b0e8f57

```

### Final Entry

And there you have it, 11 leading hex zeros: 'this is a description of the latest block20081244780471'

```code
Zeros    Nonce / Tries  SHA-256
   1                28  0a4082c16bc7e24995dba148db28256c8051656284935fa406f06c8da8cb358c
   2               139  00f22d1de9e38a9ea6d83932705d979b2b519180620a211deb99b5cd5228f0d8
   3               420  000e5d4327423b268e10355a0c27c17b200f5abb46782824fda6c6ed2fb2d383
   4            162044  00002bcfb59b2889549e3b7ae916a9cdf2cd452abb9a8057e811ce7d0f8653e0
   5            255095  000008ef297b880aa85f75b32454623b4c40cc0cb170f3ade486a40e8a4698e8
   6          10706820  0000009e3294e2f3ecac0f5eaf26d0813dfb75c94b85e159e27723a758f9d768
   7        1293230791  000000025ebebfea83dac6c2d4008870d6dab55b9d90c9f8742b2e38e8797bd9
   8         395707976  0000000053d18bbf3e8293e6a3bacda6e35ee7715e6353bf55a86cb9c3b4167b
   9      128421639420  0000000004d745e11f4dc9c0055cf4d879803d809d19ccad6bb91ceeee2d57c4
  10     2748345641427  0000000000efeba26a9ef11fffda67de019f2b3c82eb36e97c32946480297534
  11    20081244780471  00000000000ce048553873dbee8bbab601505843f4b75afe2d08fe0da9a2d16b
```


## Web References

- [How to Set Up a Virtual Environment in Python](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
