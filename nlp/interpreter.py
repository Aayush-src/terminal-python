"""
Advanced NLP interpreter for natural language command translation.
Implements multiple NLP techniques for robust command understanding.
"""
import re
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# Enhanced NLP Pattern Database with comprehensive keyword coverage
COMMAND_PATTERNS = {
    'list_files': {
        'keywords': ['list', 'show', 'display', 'files', 'contents', 'what', 'see', 'view', 'ls', 'dir', 'directory', 'folder', 'items', 'stuff', 'things'],
        'modifiers': {
            'detailed': ['all', 'detailed', 'long', 'full', 'info', 'information', 'complete', 'verbose'],
            'hidden': ['hidden', 'dot', 'all', 'including', 'with'],
            'directory': ['directory', 'folder', 'dir', 'in', 'inside', 'within']
        },
        'command': 'ls',
        'flags': {
            'detailed': '-l',
            'hidden': '-a'
        }
    },
    'navigate': {
        'keywords': ['go', 'change', 'navigate', 'enter', 'open', 'cd', 'switch', 'move to', 'browse to', 'access', 'visit'],
        'targets': {
            'home': ['home', '~', 'user', 'user directory'],
            'root': ['root', 'system', '/', 'top', 'main'],
            'parent': ['up', 'back', '..', 'previous', 'parent directory'],
            'current': ['here', 'current', '.', 'this']
        },
        'command': 'cd'
    },
    'create_directory': {
        'keywords': ['create', 'make', 'new', 'add', 'build', 'generate', 'establish', 'set up', 'initialize'],
        'targets': ['directory', 'folder', 'dir', 'path', 'location'],
        'command': 'mkdir'
    },
    'create_file': {
        'keywords': ['create', 'make', 'new', 'add', 'build', 'generate', 'establish', 'touch', 'write'],
        'targets': ['file', 'document', 'text', 'script', 'program'],
        'command': 'touch'
    },
    'delete': {
        'keywords': ['delete', 'remove', 'rm', 'del', 'trash', 'erase', 'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill'],
        'targets': ['file', 'directory', 'folder', 'item', 'thing', 'stuff'],
        'command': 'rm'
    },
    'copy': {
        'keywords': ['copy', 'duplicate', 'clone', 'cp', 'replicate', 'backup', 'save as', 'make a copy'],
        'command': 'copy'
    },
    'move': {
        'keywords': ['move', 'rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition'],
        'command': 'move'
    },
    'system_info': {
        'cpu': ['cpu', 'processor', 'performance', 'speed', 'usage', 'load', 'cores'],
        'memory': ['memory', 'ram', 'usage', 'mem', 'storage', 'available', 'free'],
        'processes': ['process', 'processes', 'running', 'task', 'ps', 'programs', 'applications'],
        'disk': ['disk', 'space', 'storage', 'capacity', 'drive', 'volume', 'usage']
    }
}

# Enhanced synonym mappings for better recognition
SYNONYM_MAPPINGS = {
    'delete': ['remove', 'rm', 'del', 'trash', 'erase', 'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill', 'wipe', 'clear'],
    'directory': ['folder', 'dir', 'path', 'location', 'place'],
    'file': ['document', 'text', 'script', 'program', 'item'],
    'create': ['make', 'new', 'add', 'build', 'generate', 'establish', 'set up', 'initialize'],
    'show': ['list', 'display', 'view', 'see', 'present', 'reveal'],
    'go': ['navigate', 'change', 'enter', 'open', 'switch', 'move to', 'browse to', 'access', 'visit'],
    'copy': ['duplicate', 'clone', 'cp', 'replicate', 'backup', 'save as', 'make a copy'],
    'move': ['rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition']
}

# Intent Recognition Patterns
INTENT_PATTERNS = {
    'file_management': r'\b(create|make|delete|remove|copy|move|rename|list|show)\b',
    'navigation': r'\b(go|change|navigate|enter|open|cd|pwd)\b',
    'system_monitoring': r'\b(cpu|memory|process|disk|performance|usage)\b',
    'help': r'\b(help|commands|what|how|guide)\b'
}


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text using enhanced regex patterns."""
    entities = {
        'files': [],
        'directories': [],
        'commands': [],
        'flags': [],
        'numbers': [],
        'paths': []
    }

    # Extract file names (with extensions) - more comprehensive pattern
    file_pattern = r'\b[a-zA-Z0-9._-]+\.\w+\b'
    entities['files'] = re.findall(file_pattern, text)

    # Extract directory names - improved pattern
    dir_pattern = r'\b[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)*\b'
    entities['directories'] = re.findall(dir_pattern, text)

    # Extract full paths (including quoted paths)
    path_pattern = r'["\']([^"\']+)["\']|([a-zA-Z]:\\[^\\s]+|[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)*)'
    path_matches = re.findall(path_pattern, text)
    for match in path_matches:
        path = match[0] if match[0] else match[1]
        if path and ('/' in path or '\\' in path or '.' in path):
            entities['paths'].append(path)

    # Extract numbers
    number_pattern = r'\b\d+\b'
    entities['numbers'] = re.findall(number_pattern, text)

    # Extract flags
    flag_pattern = r'-\w+'
    entities['flags'] = re.findall(flag_pattern, text)

    return entities


def expand_synonyms(text: str) -> str:
    """Expand synonyms in text for better pattern matching."""
    text_lower = text.lower()

    for base_word, synonyms in SYNONYM_MAPPINGS.items():
        for synonym in synonyms:
            if synonym in text_lower:
                # Replace synonym with base word for consistent matching
                text_lower = text_lower.replace(synonym, base_word)

    return text_lower


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate enhanced similarity between two strings using synonym expansion."""
    # Expand synonyms in both texts
    text1_expanded = expand_synonyms(text1.lower())
    text2_expanded = expand_synonyms(text2.lower())

    words1 = set(text1_expanded.split())
    words2 = set(text2_expanded.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    # Boost score for exact matches
    exact_match_boost = 0.2 if text1.lower() == text2.lower() else 0.0

    return min(1.0, len(intersection) / len(union) + exact_match_boost)


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

    # Handle complex multi-step commands first
    if ' and ' in query_lower or ' then ' in query_lower or ' after that ' in query_lower:
        return handle_multi_step_command(query)

    # Handle single-step file/folder creation commands
    if any(word in query_lower for word in ['create', 'make', 'new']):
        if any(word in query_lower for word in ['file']):
            # Extract file name
            file_name = extract_entity_from_step(query, ['file'])
            if file_name:
                return f"touch {file_name}"
            else:
                return "touch new_file.txt"
        elif any(word in query_lower for word in ['folder', 'directory', 'dir']):
            # Extract folder name
            folder_name = extract_entity_from_step(
                query, ['folder', 'directory', 'dir'])
            if folder_name:
                return f"mkdir {folder_name}"
            else:
                return "mkdir new_folder"

    # Handle delete/remove commands with enhanced recognition
    elif any(word in query_lower for word in ['delete', 'remove', 'rm', 'del', 'trash', 'erase', 'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill', 'wipe', 'clear']):
        # Extract target name (file or folder) with better patterns
        target = extract_entity_from_step_enhanced(query, ['delete', 'remove', 'rm', 'del', 'trash', 'erase',
                                                   'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill', 'wipe', 'clear'])

        if target:
            # Check if it's likely a directory (no extension, common directory words)
            if not target.count('.') and any(word in query_lower for word in ['directory', 'folder', 'dir']):
                return f"rmdir {target}"
            else:
                return f"rm {target}"
        else:
            return "echo 'Please specify what to delete'"

    # Handle copy commands with enhanced recognition
    elif any(word in query_lower for word in ['copy', 'cp', 'duplicate', 'replicate', 'backup', 'save as', 'make a copy']):
        # Extract source and destination with enhanced patterns
        source = extract_entity_from_step_enhanced(
            query, ['copy', 'cp', 'duplicate', 'replicate', 'backup', 'save as', 'make a copy'])
        dest = extract_entity_from_step_enhanced(
            query, ['to', 'into', 'as', 'destination'])
        if source and dest:
            return f"copy {source} {dest}"
        else:
            return "echo 'Please specify source and destination for copy operation'"

    # Handle move/rename commands with enhanced recognition
    elif any(word in query_lower for word in ['move', 'rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition']):
        # Extract source and destination with enhanced patterns
        source = extract_entity_from_step_enhanced(
            query, ['move', 'rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition'])
        dest = extract_entity_from_step_enhanced(
            query, ['to', 'as', 'destination'])
        if source and dest:
            return f"move {source} {dest}"
        else:
            return "echo 'Please specify source and destination for move operation'"

    # Handle navigation commands with enhanced recognition
    elif any(word in query_lower for word in ['go to', 'navigate', 'change to', 'cd', 'switch', 'move to', 'browse to', 'access', 'visit', 'enter']):
        # Extract directory with enhanced patterns
        directory = extract_entity_from_step_enhanced(
            query, ['go to', 'navigate', 'change to', 'cd', 'switch', 'move to', 'browse to', 'access', 'visit', 'enter'])
        if directory:
            return f"cd {directory}"
        else:
            return "cd"

    # Handle list commands with enhanced recognition
    elif any(word in query_lower for word in ['list', 'show', 'display', 'files', 'view', 'see', 'ls', 'dir', 'directory', 'folder', 'items', 'stuff', 'things', 'contents']):
        if any(word in query_lower for word in ['all', 'hidden', 'detailed', 'long', 'full', 'info', 'information', 'complete', 'verbose']):
            return "ls -la"
        elif any(word in query_lower for word in ['detailed', 'long', 'full', 'info', 'information', 'complete', 'verbose']):
            return "ls -l"
        elif any(word in query_lower for word in ['hidden', 'dot', 'all', 'including', 'with']):
            return "ls -a"
        else:
            return "ls"

    # Enhanced system monitoring commands
    elif any(word in query_lower for word in ['cpu', 'processor', 'performance', 'speed', 'usage', 'load', 'cores']):
        return "cpu"
    elif any(word in query_lower for word in ['memory', 'ram', 'usage', 'mem', 'storage', 'available', 'free']):
        return "mem"
    elif any(word in query_lower for word in ['process', 'processes', 'running', 'task', 'ps', 'programs', 'applications']):
        return "ps"
    elif any(word in query_lower for word in ['disk', 'space', 'storage', 'capacity', 'drive', 'volume', 'usage']):
        return "disk"
    elif any(word in query_lower for word in ['where', 'location', 'path', 'pwd', 'current directory', 'working directory']):
        return "pwd"
    elif any(word in query_lower for word in ['help', 'commands', 'what can', 'guide', 'assistance']):
        return "help"
    elif any(word in query_lower for word in ['clear', 'clean', 'reset', 'wipe']):
        return "clear"
    elif any(word in query_lower for word in ['exit', 'quit', 'close', 'end', 'stop', 'terminate']):
        return "exit"

    # Extract entities
    entities = extract_entities(query)

    # Parse command structure
    structure = parse_command_structure(query)

    # Generate command
    command = generate_command(structure)

    # Enhanced fuzzy matching with synonym support
    if command == "echo 'Command not recognized'":
        # Try synonym expansion first
        expanded_query = expand_synonyms(query)
        best_match, score = get_best_match(expanded_query, COMMAND_PATTERNS)

        # Lower threshold for better recognition
        if score > 0.2:  # Lowered threshold for fuzzy matching
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

        # Try direct keyword matching as fallback
        for pattern_name, pattern_data in COMMAND_PATTERNS.items():
            keywords = pattern_data.get('keywords', [])
            for keyword in keywords:
                if keyword in query_lower:
                    if pattern_name == 'list_files':
                        return "ls"
                    elif pattern_name == 'navigate':
                        return "cd"
                    elif pattern_name == 'create_directory':
                        return "mkdir new_directory"
                    elif pattern_name == 'create_file':
                        return "touch new_file.txt"
                    elif pattern_name == 'delete':
                        return "rm"
                    elif pattern_name == 'copy':
                        return "copy"
                    elif pattern_name == 'move':
                        return "move"

    return command if command != "echo 'Command not recognized'" else f"echo 'I didn't understand: \"{query}\". Try commands like: show files, delete folder, create file, go to directory, copy file, etc.'"


def is_nlp_command(command: str) -> bool:
    """
    Check if a command is an NLP command.

    Auto-detects NLP commands by checking if the command is NOT a known system command.
    Also supports explicit !NLP prefix for backward compatibility.

    Args:
        command (str): Command to check

    Returns:
        bool: True if it's an NLP command
    """
    command = command.strip()

    # Explicit !NLP prefix (backward compatibility)
    if command.lower().startswith('!nlp'):
        return True

    # Auto-detection: if not a known system command, treat as NLP
    return not is_system_command(command)


def is_system_command(command: str) -> bool:
    """
    Check if a command is a known system command.

    Args:
        command (str): Command to check

    Returns:
        bool: True if it's a known system command
    """
    if not command.strip():
        return False

    # Get the first word (command name)
    cmd = command.strip().split()[0].lower()

    # List of known system commands
    system_commands = {
        # Navigation commands
        'ls', 'dir', 'cd', 'pwd', 'root',

        # Directory operations
        'mkdir', 'rmdir',

        # File operations
        'rm', 'del', 'touch', 'copy', 'cp', 'move', 'mv',

        # System monitoring
        'cpu', 'mem', 'ps', 'disk',

        # Package management
        'pip',

        # Special commands
        'help', 'clear', 'exit', 'quit'
    }

    return cmd in system_commands


def extract_nlp_query(command: str) -> str:
    """
    Extract the natural language query from an NLP command.

    Handles both explicit !NLP prefix and auto-detected NLP commands.

    Args:
        command (str): Full NLP command

    Returns:
        str: Extracted query
    """
    command = command.strip()

    # If it has explicit !NLP prefix, remove it
    if command.lower().startswith('!nlp'):
        return command[5:].strip()  # Remove '!nlp' prefix

    # For auto-detected NLP commands, return the full command as the query
    return command


def get_supported_patterns() -> list:
    """
    Get list of supported natural language patterns.

    Returns:
        list: List of supported patterns
    """
    return [
        "List files/directories (show files, display contents, what's here)",
        "Change directory (go to, navigate to, enter folder)",
        "Create directory/folder (make folder, new directory, add folder)",
        "Create file (make file, new document, touch file)",
        "Delete files/directories (remove, trash, erase, get rid of)",
        "Copy files (duplicate, clone, backup, save as)",
        "Move/rename files (relocate, transfer, change location)",
        "Show CPU usage (processor performance, system load)",
        "Show memory usage (RAM usage, memory stats)",
        "Show running processes (running programs, active tasks)",
        "Show disk usage (storage space, disk capacity)",
        "Show current directory (where am I, current location)",
        "Get help (commands guide, what can I do)",
        "Clear terminal (clean screen, reset display)",
        "Exit terminal (quit, close, end session)"
    ]


def analyze_command_context(query: str) -> Dict[str, any]:
    """
    Analyze the context of a command to provide better interpretation.

    Args:
        query (str): The natural language query

    Returns:
        Dict: Context analysis including urgency, complexity, and intent
    """
    query_lower = query.lower()

    context = {
        'urgency': 'normal',
        'complexity': 'simple',
        'intent': 'unknown',
        'has_target': False,
        'has_source': False,
        'has_destination': False,
        'is_multi_step': False
    }

    # Analyze urgency indicators
    urgency_words = ['urgent', 'quickly',
                     'fast', 'immediately', 'asap', 'hurry']
    if any(word in query_lower for word in urgency_words):
        context['urgency'] = 'high'

    # Analyze complexity
    complexity_indicators = ['and', 'then', 'after',
                             'before', 'also', 'next', 'followed by']
    if any(word in query_lower for word in complexity_indicators):
        context['complexity'] = 'complex'
        context['is_multi_step'] = True

    # Analyze intent
    if any(word in query_lower for word in ['create', 'make', 'new', 'add']):
        context['intent'] = 'create'
    elif any(word in query_lower for word in ['delete', 'remove', 'trash', 'erase']):
        context['intent'] = 'delete'
    elif any(word in query_lower for word in ['copy', 'duplicate', 'clone']):
        context['intent'] = 'copy'
    elif any(word in query_lower for word in ['move', 'rename', 'relocate']):
        context['intent'] = 'move'
    elif any(word in query_lower for word in ['show', 'list', 'display', 'view']):
        context['intent'] = 'list'
    elif any(word in query_lower for word in ['go', 'navigate', 'change', 'cd']):
        context['intent'] = 'navigate'

    # Analyze presence of targets, sources, destinations
    entities = extract_entities(query)
    context['has_target'] = len(entities['files']) > 0 or len(
        entities['directories']) > 0
    context['has_source'] = 'from' in query_lower or 'source' in query_lower
    context['has_destination'] = 'to' in query_lower or 'into' in query_lower or 'destination' in query_lower

    return context


def handle_multi_step_command(query: str) -> str:
    """
    Enhanced multi-step command handler with better pattern recognition.

    Args:
        query (str): Multi-step natural language query

    Returns:
        str: Combined commands to execute
    """
    query_lower = query.lower().strip()

    # Enhanced connectors for better splitting
    connectors = [' and ', ' then ', ' after that ', ' next ', ' also ',
                  ' followed by ', ' subsequently ', ' after ', ' before ']
    steps = [query]

    for connector in connectors:
        if connector in query_lower:
            steps = query_lower.split(connector)
            break

    commands = []

    for step in steps:
        step = step.strip()
        if not step:
            continue

        # Enhanced step analysis with better entity extraction
        if any(word in step for word in ['create', 'make', 'new', 'add', 'build', 'generate', 'establish', 'set up', 'initialize']):
            if any(word in step for word in ['folder', 'directory', 'dir', 'path', 'location']):
                # Extract folder name with enhanced extraction
                folder_name = extract_entity_from_step_enhanced(
                    step, ['folder', 'directory', 'dir', 'path', 'location'])
                if folder_name:
                    commands.append(f"mkdir {folder_name}")
            elif any(word in step for word in ['file', 'document', 'text', 'script', 'program']):
                # Extract file name with enhanced extraction
                file_name = extract_entity_from_step_enhanced(
                    step, ['file', 'document', 'text', 'script', 'program'])
                if file_name:
                    commands.append(f"touch {file_name}")

        elif any(word in step for word in ['move', 'copy', 'rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition', 'duplicate', 'clone', 'cp', 'replicate', 'backup', 'save as', 'make a copy']):
            # Extract source and destination with enhanced extraction
            source = extract_entity_from_step_enhanced(step, ['move', 'copy', 'rename', 'mv', 'relocate', 'transfer', 'shift',
                                                       'change location', 'reposition', 'duplicate', 'clone', 'cp', 'replicate', 'backup', 'save as', 'make a copy'])
            dest = extract_entity_from_step_enhanced(
                step, ['to', 'into', 'as', 'destination'])

            if source and dest:
                if any(word in step for word in ['move', 'rename', 'mv', 'relocate', 'transfer', 'shift', 'change location', 'reposition']):
                    commands.append(f"move {source} {dest}")
                elif any(word in step for word in ['copy', 'duplicate', 'clone', 'cp', 'replicate', 'backup', 'save as', 'make a copy']):
                    commands.append(f"copy {source} {dest}")

        elif any(word in step for word in ['delete', 'remove', 'rm', 'del', 'trash', 'erase', 'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill', 'wipe', 'clear']):
            # Extract target with enhanced extraction
            target = extract_entity_from_step_enhanced(
                step, ['delete', 'remove', 'rm', 'del', 'trash', 'erase', 'eliminate', 'destroy', 'get rid of', 'clean up', 'purge', 'drop', 'kill', 'wipe', 'clear'])
            if target:
                # Check if it's likely a directory
                if not target.count('.') and any(word in step for word in ['directory', 'folder', 'dir']):
                    commands.append(f"rmdir {target}")
                else:
                    commands.append(f"rm {target}")

        elif any(word in step for word in ['list', 'show', 'display', 'files', 'view', 'see', 'ls', 'dir', 'directory', 'folder', 'items', 'stuff', 'things', 'contents']):
            if any(word in step for word in ['all', 'hidden', 'detailed', 'long', 'full', 'info', 'information', 'complete', 'verbose']):
                commands.append("ls -la")
            elif any(word in step for word in ['detailed', 'long', 'full', 'info', 'information', 'complete', 'verbose']):
                commands.append("ls -l")
            elif any(word in step for word in ['hidden', 'dot', 'all', 'including', 'with']):
                commands.append("ls -a")
            else:
                commands.append("ls")

        elif any(word in step for word in ['go to', 'navigate', 'change to', 'cd', 'switch', 'move to', 'browse to', 'access', 'visit', 'enter']):
            # Extract directory with enhanced extraction
            directory = extract_entity_from_step_enhanced(
                step, ['go to', 'navigate', 'change to', 'cd', 'switch', 'move to', 'browse to', 'access', 'visit', 'enter'])
            if directory:
                commands.append(f"cd {directory}")

    # Return combined commands
    if commands:
        return " && ".join(commands)
    else:
        return f"echo 'Could not parse multi-step command: {query}'"


def extract_entity_from_step(step: str, keywords: List[str]) -> str:
    """
    Extract entity (file/folder name) from a step.

    Args:
        step (str): The step text
        keywords (List[str]): Keywords to look for

    Returns:
        str: Extracted entity name
    """
    import re

    # Try to find quoted names first
    quoted = re.findall(r'"([^"]*)"', step)
    if quoted:
        return quoted[0]

    quoted = re.findall(r"'([^']*)'", step)
    if quoted:
        return quoted[0]

    # Look for patterns like "named X", "called X", "as X"
    named_patterns = [
        r'named\s+([a-zA-Z0-9._-]+)',
        r'called\s+([a-zA-Z0-9._-]+)',
        r'as\s+([a-zA-Z0-9._-]+)',
        r'with\s+name\s+([a-zA-Z0-9._-]+)'
    ]

    for pattern in named_patterns:
        match = re.search(pattern, step, re.IGNORECASE)
        if match:
            return match.group(1)

    # Look for file extensions (.txt, .py, .js, etc.) - prioritize this
    file_pattern = r'([a-zA-Z0-9._-]+\.[a-zA-Z0-9]+)'
    file_match = re.search(file_pattern, step)
    if file_match:
        return file_match.group(1)

    # Look for folder/directory names (no extension)
    folder_pattern = r'\b([a-zA-Z0-9_-]+)\b'
    folder_matches = re.findall(folder_pattern, step)
    # Filter out common words and action words
    common_words = {'a', 'an', 'the', 'new', 'create', 'make', 'delete', 'remove', 'copy', 'move',
                    'rename', 'file', 'folder', 'directory', 'dir', 'to', 'into', 'as', 'named', 'called', 'with', 'name'}
    for match in folder_matches:
        if match.lower() not in common_words and len(match) > 1:
            return match

    # Fallback: look for words after keywords
    words = step.split()
    for i, word in enumerate(words):
        if word.lower() in keywords and i + 1 < len(words):
            # Skip common words like "a", "the", "new"
            next_word = words[i + 1].lower()
            if next_word in ['a', 'an', 'the', 'new'] and i + 2 < len(words):
                entity = words[i + 2]
            else:
                entity = words[i + 1]
            # Clean up the entity name
            entity = entity.strip('.,!?;:"')
            # Don't return the action word itself as entity
            if entity.lower() not in keywords:
                return entity

    return None


def extract_entity_from_step_enhanced(step: str, keywords: List[str]) -> str:
    """
    Enhanced entity extraction with better pattern recognition.

    Args:
        step (str): The step text
        keywords (List[str]): Keywords to look for

    Returns:
        str: Extracted entity name
    """
    import re

    # Try to find quoted names first (including paths)
    quoted = re.findall(r'"([^"]*)"', step)
    if quoted:
        return quoted[0]

    quoted = re.findall(r"'([^']*)'", step)
    if quoted:
        return quoted[0]

    # Look for patterns like "named X", "called X", "as X", "the X"
    named_patterns = [
        r'named\s+([a-zA-Z0-9._-]+)',
        r'called\s+([a-zA-Z0-9._-]+)',
        r'as\s+([a-zA-Z0-9._-]+)',
        r'with\s+name\s+([a-zA-Z0-9._-]+)',
        r'the\s+([a-zA-Z0-9._-]+)',
        r'a\s+([a-zA-Z0-9._-]+)',
        r'an\s+([a-zA-Z0-9._-]+)'
    ]

    for pattern in named_patterns:
        match = re.search(pattern, step, re.IGNORECASE)
        if match:
            return match.group(1)

    # Look for file extensions (.txt, .py, .js, etc.) - prioritize this
    file_pattern = r'([a-zA-Z0-9._-]+\.[a-zA-Z0-9]+)'
    file_match = re.search(file_pattern, step)
    if file_match:
        return file_match.group(1)

    # Look for paths (with slashes or backslashes)
    path_pattern = r'([a-zA-Z0-9._-]+(?:[/\\][a-zA-Z0-9._-]+)+)'
    path_match = re.search(path_pattern, step)
    if path_match:
        return path_match.group(1)

    # Look for folder/directory names (no extension)
    folder_pattern = r'\b([a-zA-Z0-9_-]+)\b'
    folder_matches = re.findall(folder_pattern, step)

    # Enhanced common words filter
    common_words = {
        'a', 'an', 'the', 'new', 'create', 'make', 'delete', 'remove', 'copy', 'move',
        'rename', 'file', 'folder', 'directory', 'dir', 'to', 'into', 'as', 'named',
        'called', 'with', 'name', 'trash', 'erase', 'eliminate', 'destroy', 'get',
        'rid', 'of', 'clean', 'up', 'purge', 'drop', 'kill', 'wipe', 'clear', 'and',
        'or', 'but', 'in', 'on', 'at', 'by', 'for', 'from', 'with', 'without'
    }

    for match in folder_matches:
        if match.lower() not in common_words and len(match) > 1:
            return match

    # Enhanced fallback: look for words after keywords with better context
    words = step.split()
    for i, word in enumerate(words):
        if word.lower() in keywords and i + 1 < len(words):
            # Skip common words like "a", "the", "new"
            next_word = words[i + 1].lower()
            if next_word in ['a', 'an', 'the', 'new'] and i + 2 < len(words):
                entity = words[i + 2]
            else:
                entity = words[i + 1]
            # Clean up the entity name
            entity = entity.strip('.,!?;:"')
            # Don't return the action word itself as entity
            if entity.lower() not in keywords and entity.lower() not in common_words:
                return entity

    return None
