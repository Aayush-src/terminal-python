"""
Advanced NLP interpreter for natural language command translation.
Implements multiple NLP techniques for robust command understanding.
"""
import re
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# NLP Pattern Database
COMMAND_PATTERNS = {
    'list_files': {
        'keywords': ['list', 'show', 'display', 'files', 'contents', 'what', 'see'],
        'modifiers': {
            'detailed': ['all', 'detailed', 'long', 'full', 'info'],
            'hidden': ['hidden', 'dot', 'all'],
            'directory': ['directory', 'folder', 'dir', 'in']
        },
        'command': 'ls',
        'flags': {
            'detailed': '-l',
            'hidden': '-a'
        }
    },
    'navigate': {
        'keywords': ['go', 'change', 'navigate', 'enter', 'open', 'cd'],
        'targets': {
            'home': ['home', '~'],
            'root': ['root', 'system', '/'],
            'parent': ['up', 'back', '..'],
            'current': ['here', 'current', '.']
        },
        'command': 'cd'
    },
    'create_directory': {
        'keywords': ['create', 'make', 'new', 'add'],
        'targets': ['directory', 'folder', 'dir'],
        'command': 'mkdir'
    },
    'create_file': {
        'keywords': ['create', 'make', 'new', 'add', 'touch'],
        'targets': ['file', 'document'],
        'command': 'touch'
    },
    'delete': {
        'keywords': ['delete', 'remove', 'rm', 'del', 'trash'],
        'command': 'rm'
    },
    'copy': {
        'keywords': ['copy', 'duplicate', 'clone', 'cp'],
        'command': 'copy'
    },
    'move': {
        'keywords': ['move', 'rename', 'mv', 'relocate'],
        'command': 'move'
    },
    'system_info': {
        'cpu': ['cpu', 'processor', 'performance', 'speed'],
        'memory': ['memory', 'ram', 'usage', 'mem'],
        'processes': ['process', 'processes', 'running', 'task', 'ps'],
        'disk': ['disk', 'space', 'storage', 'capacity']
    }
}

# Intent Recognition Patterns
INTENT_PATTERNS = {
    'file_management': r'\b(create|make|delete|remove|copy|move|rename|list|show)\b',
    'navigation': r'\b(go|change|navigate|enter|open|cd|pwd)\b',
    'system_monitoring': r'\b(cpu|memory|process|disk|performance|usage)\b',
    'help': r'\b(help|commands|what|how|guide)\b'
}


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text using regex patterns."""
    entities = {
        'files': [],
        'directories': [],
        'commands': [],
        'flags': [],
        'numbers': []
    }

    # Extract file names (with extensions)
    file_pattern = r'\b\w+\.\w+\b'
    entities['files'] = re.findall(file_pattern, text)

    # Extract directory names
    dir_pattern = r'\b\w+(?:/\w+)*\b'
    entities['directories'] = re.findall(dir_pattern, text)

    # Extract numbers
    number_pattern = r'\b\d+\b'
    entities['numbers'] = re.findall(number_pattern, text)

    return entities


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two strings."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union)


def get_best_match(query: str, patterns: Dict) -> Tuple[str, float]:
    """Find the best matching pattern for a query."""
    best_match = None
    best_score = 0.0

    for pattern_name, pattern_data in patterns.items():
        keywords = pattern_data.get('keywords', [])
        for keyword in keywords:
            score = calculate_similarity(query, keyword)
            if score > best_score:
                best_score = score
                best_match = pattern_name

    return best_match, best_score


def parse_command_structure(query: str) -> Dict:
    """Parse the command structure from natural language."""
    query_lower = query.lower()
    words = query.split()

    structure = {
        'action': None,
        'target': None,
        'source': None,
        'destination': None,
        'flags': [],
        'arguments': []
    }

    # Extract action
    for pattern_name, pattern_data in COMMAND_PATTERNS.items():
        if any(keyword in query_lower for keyword in pattern_data.get('keywords', [])):
            structure['action'] = pattern_name
            break

    # Extract targets and arguments
    for i, word in enumerate(words):
        if word.lower() in ['to', 'into', 'as', 'from']:
            continue
        elif i > 0 and words[i-1].lower() in ['to', 'into', 'as']:
            structure['destination'] = word
        elif i > 0 and words[i-1].lower() in ['from']:
            structure['source'] = word
        elif word.startswith('-'):
            structure['flags'].append(word)
        elif word not in ['the', 'a', 'an', 'and', 'or', 'with', 'in', 'on', 'at']:
            structure['arguments'].append(word)

    return structure


def generate_command(structure: Dict) -> str:
    """Generate terminal command from parsed structure."""
    action = structure['action']

    if not action:
        return "echo 'Command not recognized'"

    if action == 'list_files':
        cmd = 'ls'
        if 'detailed' in structure['flags'] or any(word in str(structure['arguments']) for word in ['all', 'detailed', 'long']):
            cmd += ' -l'
        if 'hidden' in structure['flags'] or any(word in str(structure['arguments']) for word in ['hidden', 'all']):
            cmd += ' -a'
        if structure['target']:
            cmd += f' {structure["target"]}'
        return cmd

    elif action == 'navigate':
        cmd = 'cd'
        if structure['target']:
            if structure['target'].lower() in ['home', '~']:
                cmd += ' ~'
            elif structure['target'].lower() in ['root', 'system', '/']:
                cmd += ' /'
            elif structure['target'].lower() in ['up', 'back', '..']:
                cmd += ' ..'
            else:
                cmd += f' {structure["target"]}'
        return cmd

    elif action == 'create_directory':
        if structure['arguments']:
            return f'mkdir {structure["arguments"][0]}'
        return 'mkdir new_directory'

    elif action == 'create_file':
        if structure['arguments']:
            return f'touch {structure["arguments"][0]}'
        return 'touch new_file.txt'

    elif action == 'delete':
        if structure['arguments']:
            return f'rm {structure["arguments"][0]}'
        return "echo 'Please specify what to delete'"

    elif action == 'copy':
        if structure['source'] and structure['destination']:
            return f'copy {structure["source"]} {structure["destination"]}'
        elif len(structure['arguments']) >= 2:
            return f'copy {structure["arguments"][0]} {structure["arguments"][1]}'
        return "echo 'Please specify source and destination'"

    elif action == 'move':
        if structure['source'] and structure['destination']:
            return f'move {structure["source"]} {structure["destination"]}'
        elif len(structure['arguments']) >= 2:
            return f'move {structure["arguments"][0]} {structure["arguments"][1]}'
        return "echo 'Please specify source and destination'"

    return "echo 'Command not implemented'"


def interpret_nl_query(query: str) -> str:
    """
    Advanced NLP interpreter with multiple techniques.

    Args:
        query (str): Natural language query

    Returns:
        str: Terminal command to execute
    """
    if not query or not query.strip():
        return "echo 'Please provide a command'"

    query = query.strip()
    query_lower = query.lower()

    # Quick pattern matching for common commands
    if any(word in query_lower for word in ['cpu', 'processor', 'performance']):
        return "cpu"
    elif any(word in query_lower for word in ['memory', 'ram', 'usage']):
        return "mem"
    elif any(word in query_lower for word in ['process', 'processes', 'running', 'task']):
        return "ps"
    elif any(word in query_lower for word in ['disk', 'space', 'storage']):
        return "disk"
    elif any(word in query_lower for word in ['where', 'location', 'path', 'pwd']):
        return "pwd"
    elif any(word in query_lower for word in ['help', 'commands', 'what can']):
        return "help"
    elif any(word in query_lower for word in ['clear', 'clean']):
        return "clear"
    elif any(word in query_lower for word in ['exit', 'quit', 'close']):
        return "exit"

    # Extract entities
    entities = extract_entities(query)

    # Parse command structure
    structure = parse_command_structure(query)

    # Generate command
    command = generate_command(structure)

    # If no command generated, try fuzzy matching
    if command == "echo 'Command not recognized'":
        best_match, score = get_best_match(query, COMMAND_PATTERNS)
        if score > 0.3:  # Threshold for fuzzy matching
            if best_match == 'list_files':
                return "ls"
            elif best_match == 'navigate':
                return "cd"
            elif best_match == 'create_directory':
                return "mkdir new_directory"
            elif best_match == 'create_file':
                return "touch new_file.txt"
            elif best_match == 'delete':
                return "rm"
            elif best_match == 'copy':
                return "copy"
            elif best_match == 'move':
                return "move"

    return command if command != "echo 'Command not recognized'" else f"echo 'NLP interpretation not available yet. You said: \"{query}\". Try using direct commands like ls, cd, mkdir, touch, copy, move, etc.'"


def get_supported_patterns() -> list:
    """
    Get list of supported natural language patterns.

    Returns:
        list: List of supported patterns
    """
    return [
        "List files/directories",
        "Change directory",
        "Create directory/folder",
        "Delete files/directories",
        "Show CPU usage",
        "Show memory usage",
        "Show running processes",
        "Show disk usage",
        "Show current directory",
        "Get help"
    ]


def is_nlp_command(command: str) -> bool:
    """
    Check if a command is an NLP command (starts with !nlp).

    Args:
        command (str): Command to check

    Returns:
        bool: True if it's an NLP command
    """
    return command.strip().startswith('!nlp')


def extract_nlp_query(command: str) -> str:
    """
    Extract the natural language query from an NLP command.

    Args:
        command (str): NLP command (e.g., "!nlp show me the files")

    Returns:
        str: Extracted natural language query
    """
    if is_nlp_command(command):
        return command[4:].strip()  # Remove "!nlp" prefix
    return command
