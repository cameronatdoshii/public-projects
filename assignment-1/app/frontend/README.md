Steps for deploying to my EC2 instance in AWS.

Step 1:
Deploy the EC2 instance and setup the correct security group

Step 2: 
Using the PEM SSH into the instance 
ssh -i labsuser.pem ec2-user@**ip**
cd ~

Step 3:
cd ~/.aws
vi credentials
paste credentials from lab
confirm identity  aws sts get-caller-identity

Step 4:
Use SCP to copy files from local to the ec2 instance
scp -i labsuser.pem -r app ec2-user@*ip*:

Step 5:
Update the flask app to just app.run() as per instructions in comment in app.py

Step 6:
Do an update and install nginx
sudo yum update -y
sudo yum install python3 python3-pip nginx git -y

Step 7:
Install virtual env
pip3 install virtualenv

Step 8:
Navigate into the app dir and setup a virtual env installing the requirements.txt
cd app
virtualenv venv
source venv/bin/activate
pip install -r /frontend/requirements.txt

Step 9:
Install flask and gunicorn
pip install flask gunicorn

Step 10: 
Check gunicorn is working 
gunicorn --bind 0.0.0.0:8000 app:app
Should be able to navigate to instance-ip:8000

Step 11:
Configure Nginx
sudo vi /etc/nginx/conf.d/myproject.conf
Paste:
server {
    listen 80;
    server_name your-instance-ip;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
Test Nginx 
sudo nginx -t
sudo systemctl restart nginx

Step 12:
Run the app on port 80
gunicorn --bind 0.0.0.0:8000 app:app --daemon

Step 13: 
Verify deployment by going to http://your-instance-ip 
