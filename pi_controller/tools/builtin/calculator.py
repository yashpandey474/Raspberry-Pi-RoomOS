import ast
import math
import operator


class SafeEvaluator(ast.NodeVisitor):

    BINOPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    UNARYOPS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if type(node.value) not in (int, float):
            raise ValueError("Only numeric values are allowed.")

        return self._check(node.value)

    def visit_BinOp(self, node):
        operation = self.BINOPS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported arithmetic operation.")

        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent too large.")

        return self._check(operation(left, right))

    def visit_UnaryOp(self, node):
        operation = self.UNARYOPS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operation.")

        return self._check(operation(self.visit(node.operand)))

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    @staticmethod
    def _check(value):
        if type(value) is int and value.bit_length() > 1024:
            raise ValueError("Result too large.")

        if type(value) is float and not math.isfinite(value):
            raise ValueError("Result is not finite.")

        if type(value) not in (int, float):
            raise ValueError("Invalid numeric result.")

        return value


class CalculatorTool:
    name = "calculate"
    description = (
        "Evaluate a mathematical expression. "
        "Convert natural-language calculations into arithmetic expressions."
    )

    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Arithmetic expression, e.g. 12500 * 0.18.",
            }
        },
        "required": ["expression"],
        "additionalProperties": False,
    }

    async def execute(self, arguments: dict) -> dict:
        expression = arguments.get("expression", "")

        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("Expression cannot be empty.")

        if len(expression) > 200:
            raise ValueError("Expression is too long.")

        try:
            tree = ast.parse(expression, mode="eval")

            if sum(1 for _ in ast.walk(tree)) > 50:
                raise ValueError("Expression is too complex.")

            result = SafeEvaluator().visit(tree)

        except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError(f"Invalid calculation: {exc}") from exc

        return {
            "expression": expression,
            "result": result,
        }