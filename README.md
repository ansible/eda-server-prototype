A UI for ansible-events

# Setting up a development environment


Run these commands:

    git clone
    python 3.9 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ui
    npm install
    npm run build
    cd ..
    ./run_server.py


Visit this url:

    http://localhost:8080/docs#/auth/register_register_api_auth_register_post


Click "Try it out" on /api/auth/register

Change email and password

Click execute


Visit this url:


    http://localhost:8080/eda


You have set up the development environment.


