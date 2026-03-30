# verba
Verbal Agent. To chat with your AI easier, even if you arent a developer

## Run locally
Use a virtual environment and install the project from the repository root. Do not run the install command from `src/verba`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m verba
```

If `.venv` already exists, skip the first command and just activate it.

## Plan
The Plan is fully described in the plan.md in the docs-folder. Additionally i described my workplan, the architecture for the first MVP and a whiteliste of what software-licenses i want to use for this project.

## My Goal
I want to create this App to make my interaction with an LLM easier without depending on a subscription. I want to be able to set the LLM (The Brain) to whatever i want. I will also leave the possibility to connect it to a third party provider like OpenAi or Anthropic.
I would love to develop together with anybody willing to spend their time. Maybe you are using verba already and have an idea on how it could get even better. 
