#!/bin/bash
sudo yum update

# inference
rm latest_numerai_tournament_data.csv.xz
wget 'https://numerai-public-datasets.s3-us-west-2.amazonaws.com/latest_numerai_tournament_data.csv.xz'
/opt/python3/bin/python3 predict.py
/opt/python3/bin/python3 send_email.py