from dataclasses import dataclass
from typing import Any, Callable, Dict

from api.language_api.script_processor import ScriptProcessor
from language.compiler.types import (
    ComparisonOperator,
    ElementType,
    ExtractStatement,
    Literal,
    LogicalExpression,
    LogicalOperator,
    Program,
    Target,
)
from language.parsing.ast.actions.action_plugins.filter.filter import Filter
from language.parsing.ast.trees import ScriptTree
import language.compiler.compiler_exceptions as cmpe

# Each IR node is going to be an ActionBlock.
@dataclass
class CompiledScript:
    IR: Program = None
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
        #! FailPoint !# 
        # Ensure that the processor was able to initialize the script (i.e., that it was a valid object that can be interpreted.)'
        if not self.processor.is_valid_script:
            # Then we can raise a CompilerException. This one expects the description of the 
            raise cmpe.UnparsableScriptException(self.processor.script.get_issues())
        self.id = self.processor.id

        pass

    def parse_to_ast(self) -> ScriptTree:
        return self.processor.parse()

    def lower_to_ir(self):
        """Convert AST to IR in a straightforward manner"""
        program = Program()

        ast: ScriptTree = self.STATES["AST"]
        # Process targets
        for target_name, url in ast.targets.items():
            program.targets.append(Target(name=target_name, url=url))
        # Process action blocks
        for block in ast.action_blocks:
            target_name = block.target
            # Process each action in the block
            for action in block.actions:
                match action.action_type:
                    case 'filter':
                        # Handle extract where actions
                        condition = self.lower_filter_to_condition(action)
                        output_var = action.metadata["assignment"].replace(';', "")

                        extract_stmt = ExtractStatement(
                            source=target_name,
                            condition=condition,
                            destination=output_var
                        )
                        program.statements.append(extract_stmt)
                    case _:
                        raise TypeError(f"Unexpected action type: {action.action_type}")
                # Easy to add support for other action types here
        print(program)
        return program

    def lower_filter_to_condition(self, filter_action: Filter):
        """Convert a filter action to an IR condition"""
        # If it has an operator, it's a logical expression
        print(filter_action)
        if filter_action.operator:
            expressions = [self.lower_filter_to_condition(op) for op in filter_action.operands]
            return LogicalExpression(
                operator=LogicalOperator(filter_action.operator.value.lower()),
                expressions=expressions
            )

        # Otherwise, it's a leaf filter (comparison)
        element_type = ElementType(filter_action.filter_type.value.lower())

        # Create appropriate selector based on element type

        selector = ElementSelector(element_type=element_type, select=filter_action.value)

        # Handle the comparison operation
        if isinstance(filter_action.value, dict) and "contains" in filter_action.value:
            op = ComparisonOperator.CONTAINS
            value = Literal(filter_action.value["contains"])
        else:
            op = ComparisonOperator.EQUALS
            value = Literal(filter_action.value)

        return Comparison(lhs=selector, rhs=value, operator=op)
    def compile(self) -> CompiledScript:
        PASSES: Dict[str, Callable] = {  # noqa: N806
            "parse": self.parse_to_ast,
            "lower_to_ir": self.lower_to_ir
        }
        for pass_name, call in PASSES.items():
            match pass_name:
                case 'parse':
                    self.STATES['AST'] = call()
                case 'lower_to_ir':
                    self.STATES['IR'] = call()


