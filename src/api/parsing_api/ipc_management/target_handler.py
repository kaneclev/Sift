
from language.IR.instructions.instruction import Instruction


class TargetHandler:
    def __init__(self, instruction: Instruction):
        self.url = instruction.url
        self.alias = instruction.alias
        pass
    def __str__(self):
        return f"TargetHandler( url: {self.url}, alias: {self.alias} )"
    def to_dict(self):
        return {"url": self.url, "alias": self.alias}
