import os
import json
import discord


ADMINS = {}
BLACKLIST_TOKENS = []


class EcosystemBots:
    FullyAutomatedNutcracker = "FAN_"


def load_creds(is_debug, bot: str):
    with open('config/creds.json') as fp:
        creds = json.load(fp)
        return creds[bot + "BETA_TOKEN"] if is_debug else creds[bot + "TOKEN"]


def load_reddit_creds():
    with open(r'config/creds.json') as f:
        creds = json.load(f)
        return creds['REDDIT_USERNAME'], creds['REDDIT_PASSWORD'], creds['REDDIT_SECRET'], creds['REDDIT_ID']


def load_admins():
    global ADMINS
    with open('config/admin.json') as fp:
        ADMINS = json.load(fp)


def load_blacklist():
    global BLACKLIST_TOKENS
    with open('config/blacklisted_tokens.list') as fp:
        BLACKLIST_TOKENS = list(fp.readlines())


def has_blacklisted_word(string):
    for token in BLACKLIST_TOKENS:
        if token in string:
            return True
    return False


def is_blacklisted(token):
    return token in BLACKLIST_TOKENS


def is_admin(user: discord.User):
    return str(user.id) in ADMINS


def get_last_log_file_path():
    scriptpath = os.path.realpath(__file__)
    rootpath = os.path.abspath(os.path.join(scriptpath, '..', '..', '..'))
    logspath = os.path.abspath(os.path.join(rootpath, 'logs'))
    logs = [os.path.join(logspath, log) for log in os.listdir(logspath)]
    latest = max(logs, key=os.path.getctime)
    return latest


def tail(f, lines):
    tail_log = []
    at_idx = 0
    for line in f.readlines():
        if len(tail_log) == lines:
            tail_log[at_idx] = line
            at_idx = (at_idx + 1) % lines
        else:
            tail_log.append(line)
    return tail_log[at_idx:] + tail_log[:at_idx]


def tail_error(f):
    last_error = ""
    listening = False
    for line in f.readlines():
        if "Catching exception in command error" in line:
            listening = True
            last_error = ""
        if line.startswith("discord.ext.commands.errors.CommandInvokeError: Command raised an exception:"):
            last_error += line
            listening = False
        if listening:
            last_error += line
    return last_error
