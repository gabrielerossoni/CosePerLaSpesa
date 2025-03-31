import json
import os
from storage import Storage

class ShoppingList:
    """Class to manage shopping lists for different users."""
    
    def __init__(self):
        """Initialize the shopping list manager."""
        self.storage = Storage("shopping_lists.json")
        self.lists = self.storage.load() or {}
    
    def add_item(self, user_id, item):
        """
        Add an item to a user's shopping list.
        
        Args:
            user_id: The telegram user ID
            item: The item to add to the list
        """
        user_id = str(user_id)
        if user_id not in self.lists:
            self.lists[user_id] = []
        
        # Convert item to lowercase to avoid duplicates with different case
        item = item.strip()
        if item and item.lower() not in [i.lower() for i in self.lists[user_id]]:
            self.lists[user_id].append(item)
            self.storage.save(self.lists)
            return True
        return False
    
    def get_items(self, user_id):
        """
        Get all items in a user's shopping list.
        
        Args:
            user_id: The telegram user ID
            
        Returns:
            A list of items in the user's shopping list
        """
        user_id = str(user_id)
        return self.lists.get(user_id, [])
    
    def remove_item(self, user_id, index):
        """
        Remove an item from a user's shopping list by index.
        
        Args:
            user_id: The telegram user ID
            index: The index of the item to remove
            
        Returns:
            The removed item if successful, None otherwise
        """
        user_id = str(user_id)
        if user_id in self.lists and 0 <= index < len(self.lists[user_id]):
            removed_item = self.lists[user_id].pop(index)
            self.storage.save(self.lists)
            return removed_item
        return None
    
    def clear_list(self, user_id):
        """
        Clear a user's entire shopping list.
        
        Args:
            user_id: The telegram user ID
        """
        user_id = str(user_id)
        if user_id in self.lists:
            self.lists[user_id] = []
            self.storage.save(self.lists)
