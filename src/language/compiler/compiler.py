from dataclasses import dataclass
from typing import Any, Callable, Dict

from api.language_api.script_processor import ScriptProcessor
from language.compiler.intermediate_representation import (
    IntermediateConstructor,
    IntermediateRepresentation,
)
from language.parsing.ast.trees import ScriptTree


# Each IR node is going to be an ActionBlock.
@dataclass
class CompiledScript:
    IR: IntermediateRepresentation = None
    BYTECODE: Any = None

class Compiler:
    def __init__(self, script: Any):  # noqa: N803
        self.STATES = {
            "AST": None,
            "IR": None,
            "BYTECODE": None
        }
        self.script = script
        self.processor = ScriptProcessor(self.script)
        self.id = self.processor.id
        pass

    def parse_to_ast(self) -> ScriptTree:
        return self.processor.parse()

    def ast_to_ir(self) -> IntermediateRepresentation:
        return IntermediateConstructor.ast_to_instructions(self.STATES['AST'], identifier=self.id)

    def compile(self) -> CompiledScript:
        PASSES: Dict[str, Callable] = {  # noqa: N806
            "parse": self.parse_to_ast,
            "lower_to_ir": self.ast_to_ir
        }
        for pass_name, call in PASSES.items():
            match pass_name:
                case 'parse':
                    self.STATES['AST'] = call()
                case 'lower_to_ir':
                    self.STATES['IR'] = call()


