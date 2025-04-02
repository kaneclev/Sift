from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List

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

class OpCode(Enum):
    """Operation codes for our bytecode instructions"""
    CHECK_TAG = auto()           # Check if element has a specific tag
    CHECK_ATTRIBUTE = auto()     # Check if element has a specific attribute
    CHECK_TEXT = auto()          # Check if element contains specific text
    LOGICAL_AND = auto()         # Logical AND operation
    LOGICAL_OR = auto()          # Logical OR operation
    LOGICAL_NOT = auto()         # Logical NOT operation
    STORE_ALIAS = auto()         # Store current result in an alias
    LOAD_ALIAS = auto()          # Load HTML from an alias
    PUSH_LITERAL = auto()        # Push a literal value onto the stack
    JUMP_IF_FALSE = auto()       # Conditional jump for optimization
    CALL = auto()

@dataclass
class BytecodeInstruction:
    """A single bytecode instruction"""
    opcode: OpCode
    operands: List[Any] = field(default_factory=list)

@dataclass
class FilterBytecode:
    """Complete bytecode for a filter operation"""
    instructions: List[BytecodeInstruction]
    to_alias: str
    from_alias: str = ""
    source_json: Dict = None  # For debugging/reference

    @classmethod
    def from_json(cls, json_data: Dict) -> "FilterBytecode":
        """Compile JSON IR into bytecode"""
        instructions = []
        to_alias = json_data["to_alias"]
        from_alias = json_data.get("from_alias", "")

        # Load from alias if specified
        if from_alias:
            instructions.append(BytecodeInstruction(
                opcode=OpCode.LOAD_ALIAS,
                operands=[from_alias]
            ))

        # Compile the condition
        cls._compile_condition(json_data["condition"], instructions)

        # Store result in to_alias
        instructions.append(BytecodeInstruction(
            opcode=OpCode.STORE_ALIAS,
            operands=[to_alias]
        ))

        return cls(
            instructions=instructions,
            to_alias=to_alias,
            from_alias=from_alias,
            source_json=json_data
        )

    @classmethod
    def _compile_condition(cls, condition: Dict, instructions: List[BytecodeInstruction]) -> None:
        """Compile a condition into bytecode instructions"""
        if "op" in condition:
            op = condition["op"]
            constraints = condition.get("constraints", [])

            if op == "not":
                # For NOT, process the inner constraint, then NOT
                cls._compile_condition(constraints[0], instructions)
                instructions.append(BytecodeInstruction(opcode=OpCode.LOGICAL_NOT))

            elif op in ["and", "any"]:
                # For multiple constraints with AND/OR
                if len(constraints) > 1:
                    # Process first constraint
                    cls._compile_condition(constraints[0], instructions)

                    # For each additional constraint
                    for constraint in constraints[1:]:
                        # Process the constraint
                        cls._compile_condition(constraint, instructions)

                        # Apply operator
                        if op == "and":
                            instructions.append(BytecodeInstruction(opcode=OpCode.LOGICAL_AND))
                        else:  # "any" (OR)
                            instructions.append(BytecodeInstruction(opcode=OpCode.LOGICAL_OR))

                # If only one constraint, process it directly
                elif len(constraints) == 1:
                    cls._compile_condition(constraints[0], instructions)

        # If it's a leaf constraint with htype
        elif "htype" in condition:
            htype = condition["htype"]
            detail = condition.get("detail", {})

            # Select appropriate CHECK operation based on htype
            if htype == "tag":
                instructions.append(BytecodeInstruction(
                    opcode=OpCode.CHECK_TAG,
                    operands=[detail]
                ))
            elif htype == "attr":
                instructions.append(BytecodeInstruction(
                    opcode=OpCode.CHECK_ATTRIBUTE,
                    operands=[detail]
                ))
            elif htype == "text":
                instructions.append(BytecodeInstruction(
                    opcode=OpCode.CHECK_TEXT,
                    operands=[detail]
                ))

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


