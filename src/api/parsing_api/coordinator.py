from typing import List

from api.parsing_api.worker import Worker


class Coordinator:
    @staticmethod
    def coordinate_parsing(scripts: List[str]):
        msgs = []
        for script in scripts:
            msgs.extend(Worker.parse(script=script))
        return msgs