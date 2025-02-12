from scrapling import StealthyFetcher


class MakeTargetRequest:
    def __init__(self, json_tree):
        response= StealthyFetcher().fetch(json_tree["targets"]["eBay"], os_randomize=True,  disable_resources=True)
        print(response)
        pass
