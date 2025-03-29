from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class HTMLType(Enum):
    TAG = auto()
    ATTRIBUTE = auto()
    TEXT = auto()

    @staticmethod
    def match(to_match) -> "HTMLType":
        match to_match:
            case 'tag':
                return HTMLType.TAG
            case 'attr':
                return HTMLType.ATTRIBUTE
            case 'text':
                return HTMLType.TEXT
            case _:
                raise TypeError(f"Unexpected HTMLType requested to match: {to_match}")
class InstructionType(Enum):
    """Types of instructions in our linear representation"""
    CHECK_PROPERTY = auto()  # Check an HTML property (tag, attribute, text)
    AND = auto()             # Logical AND operation
    OR = auto()              # Logical OR operation
    NOT = auto()             # Logical NOT operation
    PUSH_RESULT = auto()     # Push result to result stack
    STORE_ALIAS = auto()     # Store current result in an alias

@dataclass
class Detail:
    """Simplified detail class focusing only on what's needed"""
    value: Any
    is_contains: bool = False

@dataclass
class Instruction:
    """A single instruction in our linear sequence"""
    type: InstructionType
    data: Optional[Dict] = None  # Additional data needed for the instruction

@dataclass
class FilterProgram:
    """A complete program consisting of a linear sequence of instructions"""
    instructions: List[Instruction]
    to_alias: str
    from_alias: str = ""

    @classmethod
    def from_json(cls, json_data: Dict) -> "FilterProgram":
        """Convert JSON IR to a linear program"""
        instructions = []

        # Process the main operation details
        to_alias = json_data["to_alias"]
        from_alias = json_data.get("from_alias", "")

        # Convert the condition tree to a linear sequence
        cls._process_condition(json_data["condition"], instructions)

        # Add instruction to store result in to_alias
        instructions.append(Instruction(
            type=InstructionType.STORE_ALIAS,
            data={"alias": to_alias}
        ))

        return cls(
            instructions=instructions,
            to_alias=to_alias,
            from_alias=from_alias
        )

    @classmethod
    def _process_condition(cls, condition: Dict, instructions: List[Instruction]):
        """Process a condition and add corresponding instructions"""
        # If it has an operator, process it first
        if "op" in condition:
            op = condition["op"]
            constraints = condition.get("constraints", [])

            if op == "not":
                # For NOT, process the inner constraint first, then apply NOT
                cls._process_condition(constraints[0], instructions)
                instructions.append(Instruction(type=InstructionType.NOT))

            elif op in ["and", "any"]:
                # For AND/OR with multiple constraints
                if len(constraints) > 1:
                    # Process first constraint
                    cls._process_condition(constraints[0], instructions)

                    # For each additional constraint
                    for constraint in constraints[1:]:
                        # Process the constraint
                        cls._process_condition(constraint, instructions)

                        # Apply the appropriate operator
                        if op == "and":
                            instructions.append(Instruction(type=InstructionType.AND))
                        else:  # "any" (OR)
                            instructions.append(Instruction(type=InstructionType.OR))

                # If there's only one constraint, just process it directly
                elif len(constraints) == 1:
                    cls._process_condition(constraints[0], instructions)

        # If it's a leaf constraint (has htype)
        elif "htype" in condition:
            htype = HTMLType.match(condition["htype"])
            detail = condition.get("detail", {})

            # Add instruction to check this property
            instructions.append(Instruction(
                type=InstructionType.CHECK_PROPERTY,
                data={
                    "htype": htype,
                    "detail": detail  # This would be processed further in the evaluator
                }
            ))
