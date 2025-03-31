import json
import os
import logging

logger = logging.getLogger(__name__)

class Storage:
    """Class to handle persistent storage of data in JSON format."""
    
    def __init__(self, filename):
        """
        Initialize the storage with a filename.
        
        Args:
            filename: The name of the file to store data in
        """
        self.filename = filename
    
    def load(self):
        """
        Load data from the storage file.
        
        Returns:
            The loaded data, or None if the file doesn't exist or there's an error
        """
        if not os.path.exists(self.filename):
            return None
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data from {self.filename}: {e}")
            return None
    
    def save(self, data):
        """
        Save data to the storage file.
        
        Args:
            data: The data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data to {self.filename}: {e}")
            return False
