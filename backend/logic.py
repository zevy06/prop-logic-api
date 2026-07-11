from dataclasses import dataclass
import itertools

"""
This module contains the core logic for generating truth tables.
"""

"""
We first accept an infix expression from the user, which is then converted to postfix notation using the Shunting Yard algorithm. The postfix expression is evaluated to
transform it into its postfix form using an implimantation 
of the Shunting Yard algorithm.
"""


# List of operators and their precedence and standard associativity

CONNECTORS = {
    'NOT' : {'precedence': 3, 'associativity': 'right'},
    'AND' : {'precedence': 2, 'associativity': 'left'},
    'OR' : {'precedence': 1, 'associativity': 'left'},
    'IMPLIES' : {'precedence': 0, 'associativity': 'right'},
    'EQUIVALENT' : {'precedence': 0, 'associativity': 'right'},
}

def proper_infix(proposition: str) -> list:
    
    # This function takes a proposition in infix notation as input and returns a list of tokens in proper infix notation.
    
    proposition = proposition.replace('(', ' ( ').replace(')', ' ) ')
    
    for connector in CONNECTORS.keys():
        proposition = proposition.replace(connector, f' {connector} ')

    return proposition.split()

def shunting_yard(infix: list) -> list:
    """
    This function takes a list of tokens in infix notation as input and returns a list of tokens in postfix notation using the Shunting Yard algorithm.
    """
    output = []
    op_stack = []
    
    for token in infix:
        if token not in CONNECTORS and token not in ['(', ')']:
            output.append(token)
        elif token in CONNECTORS:
            while (op_stack and op_stack[-1] != '(' and
                   ((CONNECTORS[token]['associativity'] == 'left' and CONNECTORS[token]['precedence'] <= CONNECTORS[op_stack[-1]]['precedence']) or
                    (CONNECTORS[token]['associativity'] == 'right' and CONNECTORS[token]['precedence'] < CONNECTORS[op_stack[-1]]['precedence']))):
                output.append(op_stack.pop())
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            op_stack.pop()  # Pop the '(' from the stack

    while op_stack:
        output.append(op_stack.pop())

    return output


@dataclass
class Node:
    pass

@dataclass
class Proposition(Node):
    name: str
    
@dataclass
class UnaryOp(Node):
    operator: str
    operand: Node
    
@dataclass
class BinaryOp(Node):
    operator: str
    left: Node
    right: Node

def build_ast(postfix: list) -> Node:
    """
    This function takes a list of tokens in postfix notation as input and returns the root of the abstract syntax tree (AST).
    """
    stack = []
    
    for token in postfix:
        if token not in CONNECTORS:
            stack.append(Proposition(token))
        elif token == 'NOT':
            operand = stack.pop()
            stack.append(UnaryOp(token, operand))
        else:
            right = stack.pop()
            left = stack.pop()
            stack.append(BinaryOp(token, left, right))
    
    return stack[0]  # The root of the AST

def evaluate_ast(node: Node, values: dict) -> bool:
    """
    This function takes the root of the AST and a dictionary of truth/false values for the propositions
    given in the AST and returns the truth value of the entire expression.
    """
    
    if isinstance(node, Proposition):
        return values[node.name]
    
    elif isinstance(node, UnaryOp):
        operand_value = evaluate_ast(node.operand, values)
        if node.operator == 'NOT':
            return not operand_value

    elif isinstance(node, BinaryOp):
        left_eval = evaluate_ast(node.left, values)
        right_eval = evaluate_ast(node.right, values)
        
        if node.operator == 'AND':
            return left_eval and right_eval
        elif node.operator == 'OR':
            return left_eval or right_eval
        elif node.operator == 'IMPLIES':
            return not left_eval or right_eval
        elif node.operator == 'EQUIVALENT':
            return left_eval == right_eval
        

def generate_truth_table(proposition: str) -> list:
    
    """
    This function generates a truth table for the given formula in infix notation.
    """
    tokens = proper_infix(proposition)
    variables = sorted(list(set(tokens) - set(CONNECTORS.keys()) - set(['(', ')'])))
    
    ast_root = build_ast(shunting_yard(proper_infix(proposition)))

    combinations = list(itertools.product([False, True], repeat=len(variables)))
    truth_table = []
    for combo in combinations:
        values = dict(zip(variables, combo))
        result = evaluate_ast(ast_root, values)
        truth_table.append((values, result))
        
        
    """
    The result would look like this:
    
    [
        ({'P': False, 'Q': False}, True),
        ({'P': False, 'Q': True}, True),
        ({'P': True, 'Q': False}, False),
        ({'P': True, 'Q': True}, True)
    ]

    Where the first element of the tuple is a dictionary of the truth values of the variables
    and the second element is the truth value of the entire formula for that combination of truth values.
    """

    return truth_table

"""
Validation function to check if the proper infix expression is valid. This function checks for balanced parentheses and valid sequences of operators and operands.
"""

def validate_infix(proposition: list) -> bool:
    
    # checking for balanced parentheses
    
    balance = 0
    for token in proposition:
        if token == '(':
            balance += 1
        elif token == ')':
            balance -= 1
            if balance < 0:
                raise ValueError("Unbalanced parentheses in the proposition.")
    if balance != 0:
        raise ValueError("Unbalanced parentheses in the proposition.")


    # checking for invalid sequences of operators, operands and parentheses
    valid_symbols = set(CONNECTORS.keys()).union(set(['(', ')']))
    
    for i in range(len(proposition)):
        token = proposition[i]

        if token not in valid_symbols and not token.isalnum():
            raise ValueError(f"Invalid symbol '{token}' in the proposition.")

        if i > 0:
            prev_token = proposition[i - 1]
            if prev_token in CONNECTORS and token in CONNECTORS:
                raise ValueError(f"Invalid sequence: '{prev_token}' followed by '{token}' in the proposition.")
            if prev_token == '(' and token in CONNECTORS and token != 'NOT':
                raise ValueError(f"Invalid sequence: '(' followed by '{token}' in the proposition.")
            if prev_token in CONNECTORS and token == ')':
                raise ValueError(f"Invalid sequence: '{prev_token}' followed by ')'.")
            if prev_token == ')' and token == '(':
                raise ValueError("Invalid sequence: ')' followed by '(' in the proposition.")