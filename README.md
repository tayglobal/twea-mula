# twea-mula
A little system to automate kid's pocket money, presents, spending, etc...

## Install

### AWS Services

Create a Python ``venv``. I used python 3.12, but probably works with other versions.

Install the requirements

```
pip install -r requirements.txt
```

Copy ``settings-examples.py`` to ``settings.py`` and fill the configurations like your AWS account, etc....
At some point I'll refactor this to configure by a YAML.

Note that the KMS key id will be printed during ``setup.py`` so you'll want to stick it in ``settings.py`` once you see the print.

Next would be to setup the AWS stack by running ``setup.py``. I'll refactor this to use Cloud Formation or Terraform at some point. 

```
python setup.py
```

Note that the Discord interaction webhook URL would be printed. Please take note of that.

### Discord

Create a [Discord app](https://discord.com/developers/docs/getting-started).

Copy information such as ``APPLICATION_ID``, ``GUILD_ID``, ``CHANNEL_ID``, etc... to ``settings.py``

Create the slash commands:

```
python create_commands.py
```

Set the webhook URL based on the print in ``setup.py``.

## Slash commands

* ``/ping`` - To wake up the lambda function. This can solve some issue with the 3s timeout limitation that Discord imposes. Alternatively just have an AWS Bridge Event that pokes at the lambda every 5 minutes.
* ``/mula_add`` - This adds a transaction to an account (user). Arguments are ``who``, ``amount`` (can be positive or negative) and ``description``
* ``/mula_fx_set`` - Set the FX rate. Arguments are ``ccy_pair`` (For example GBPJPY) and ``fx_rate`` (a float)
* ``/mula_fx_ls`` - List the FX rate. Takes no arguments
* ``/mula_bal`` - Show the balance for a user. Optional argument is ``who``. If no argument is provided then the user issuing the command's balance is shown
