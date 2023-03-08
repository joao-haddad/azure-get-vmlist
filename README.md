# azure-vm-getlist
Python script to get Azure's VM list and performance metrics

How to use:

- Optional - Create a virtual environment and activate it:

`python3 -m venv .venv`
(activation is OS dependent: https://docs.python.org/3/library/venv.html)


- Install all the requirements:

`pip install -r requirements.txt`


- Make sure you have the AZURE CLI installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

- If you haven't used the AZURE CLI before you will need to run `az login` to set up an account

- Run the script:

`python3 main.py`

- The tool will generate one file:  "azure{date}{uuid}.json.xz"
- (Example: azure20230308-14d51e5d.json.xz")
