# update yum
sudo yum update

# get python 3.7.10
sudo yum install gcc
wget https://www.python.org/ftp/python/3.7.10/Python-3.7.10.tgz
tar zxvf Python-3.7.10.tgz
rm Python-3.7.10.tgz
cd Python-3.7.10
sudo ./configure --prefix=/opt/python3
sudo make
sudo yum install openssl-devel libffi-devel bzip2-devel xz-devel
sudo make install
# sudo ln -s /opt/python3/bin/python3 /usr/bin/python3
cd ..

# get pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py

# get all the dependencies
pip install -r requirements.txt

# run prediction
chmod +x run.sh
run.sh

