# azure-vm-getlist
Python script to get Azure's VM list and performance metrics

How to use:

- It is best to create a virtual environment:

`python3 -m venv .venv`

- Install all the requirements:

`pip install -r requirements.txt`

- Edit the main.py and replace the subscription_id with your own:

`SUBSCRIPTION_ID = "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`

- Make sure you have the AZURE CLI installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

- If you haven't used the AZURE CLI before you will need to run `az login` to set up an account

- Run the script:

`python3 main.py`

- The tool will generate two files:
    1) savedmetricsdata.bin
    2) savedvmlistdata.bin
