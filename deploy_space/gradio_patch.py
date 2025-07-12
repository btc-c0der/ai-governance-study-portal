#!/usr/bin/env python3
"""
Gradio Schema Parsing Fix
Patches the schema parsing issue where boolean values are passed instead of dictionaries
"""

import gradio as gr
from gradio_client import utils
import logging

# Store original function
_original_get_type = None

def patched_get_type(schema):
    """
    Patched version of get_type that handles boolean schemas gracefully
    """
    # If schema is a boolean, convert it to a proper schema dict
    if isinstance(schema, bool):
        return {"type": "boolean", "const": schema}
    
    # If schema is not a dict, convert to string type
    if not isinstance(schema, dict):
        logging.warning(f"Schema is not a dict: {schema} (type: {type(schema)})")
        return {"type": "string", "description": str(schema)}
    
    # Call original function for proper dict schemas
    return _original_get_type(schema)

def patched_json_schema_to_python_type(schema, defs=None):
    """
    Patched version that handles malformed schemas
    Updated to match the signature of the original function (schema, defs)
    """
    try:
        # If schema is a boolean, return appropriate Python type
        if isinstance(schema, bool):
            return bool
        
        # If schema is not a dict, return string type
        if not isinstance(schema, dict):
            logging.warning(f"Schema is not a dict: {schema} (type: {type(schema)})")
            return str
        
        # Ensure required keys exist
        if "type" not in schema:
            schema = {"type": "string", **schema}
        
        # Process the schema to get the type
        type_ = utils._json_schema_to_python_type(schema, defs)
        
        # Handle case where type_ is not a string (the error in the traceback)
        if not isinstance(type_, str):
            return str
            
        # Handle the replace operation that's failing
        try:
            CURRENT_FILE_DATA_FORMAT = "gradio_client.client.FileData"
            if isinstance(type_, str) and CURRENT_FILE_DATA_FORMAT in type_:
                return type_.replace(CURRENT_FILE_DATA_FORMAT, "filepath")
            return type_
        except Exception as e:
            logging.error(f"Error in replace operation: {e}, type_: {type_}")
            return str
    
    except Exception as e:
        logging.error(f"Schema parsing error: {e}, schema: {schema}")
        return str  # Safe fallback

def apply_gradio_patches():
    """Apply patches to fix schema parsing issues"""
    global _original_get_type
    
    try:
        # Store original function
        _original_get_type = utils.get_type
        
        # Apply patches
        utils.get_type = patched_get_type
        
        # Store original functions for reference
        original_internal_json_schema = utils._json_schema_to_python_type
        original_json_schema = utils.json_schema_to_python_type
        
        # Monkey patch the problematic functions with our fixed versions
        utils._json_schema_to_python_type = patched_json_schema_to_python_type
        utils.json_schema_to_python_type = patched_json_schema_to_python_type
        
        print("✅ Gradio schema parsing patches applied successfully")
        print(f"✅ Original internal function signature: {original_internal_json_schema.__code__.co_varnames}")
        print(f"✅ Original public function signature: {original_json_schema.__code__.co_varnames}")
        print(f"✅ Patched function signature: {patched_json_schema_to_python_type.__code__.co_varnames}")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not apply Gradio patches: {e}")
        return False

# Apply patches when module is imported
if __name__ == "__main__":
    apply_gradio_patches()
