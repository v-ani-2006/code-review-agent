"""A Python module containing intentional security vulnerabilities for Bandit/AST detection."""
import os
import subprocess
import pickle

API_KEY = "AKIA1234567890EXAMPLE"  # Hardcoded secret
SECRET_TOKEN = "super_secret_jwt_token_12345"


def run_user_code(user_input: str):
    """Executes arbitrary code submitted by untrusted user."""
    return eval(user_input)  # Insecure eval


def execute_shell_command(command: str):
    """Executes shell command with shell=True."""
    return subprocess.check_output(f"echo {command}", shell=True)  # Insecure shell


def deserialize_data(payload: bytes):
    """Unpickles untrusted binary payload."""
    return pickle.loads(payload)  # Insecure unpickling


def query_database(user_id: str):
    """Vulnerable SQL injection string concatenation."""
    query = f"SELECT * FROM users WHERE id = '{user_id}' AND is_active = 1"
    return query
