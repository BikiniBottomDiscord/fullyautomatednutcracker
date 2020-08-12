import json


class BotGuildSettings:
    instance = None

    class _BGS:
        def __init__(self, **attribs):
            self.__dict__.update(attribs)

    def __init__(self, debug, database, fanbot, reimport=False):
        if not BotGuildSettings.instance or reimport:
            with open(f"config/guild_constants{'_debug' if debug else ''}.json", "r") as fp:
                settings = json.load(fp)
                settings["DEBUG"] = debug
                settings["DATABASE"] = database
                settings["FANBOT"] = fanbot
            BotGuildSettings.instance = self._BGS(**settings)

    def __getattr__(self, name):
        return getattr(self.instance, name)
