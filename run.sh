#!/bin/bash
sudo yum update

# inference
wget 'https://numerai-public-datasets.s3-us-west-2.amazonaws.com/latest_numerai_tournament_data.csv.xz'
/opt/python3/bin/python3 predict.py
/opt/python3/bin/python3 send_email.py
rm latest_numerai_tournament_data.csv.xz

# shuts down instance after making predictions
sudo halt
