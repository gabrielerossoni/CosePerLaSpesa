import json
import os
import re
from storage import Storage

class ShoppingList:
    """Class to manage shopping lists for different users."""
    
    def __init__(self):
        """Initialize the shopping list manager."""
        self.storage = Storage("shopping_lists.json")
        lists_data = self.storage.load() or {}
        
        # Convert old format to new format if needed
        self.lists = {}
        for user_id, items in lists_data.items():
            if isinstance(items, list):
                # Convert old format (list of strings) to new format (list of dicts)
                self.lists[user_id] = [{"name": item, "quantity": "1"} for item in items]
            else:
                self.lists[user_id] = items
        
        # Ripulisci i dati corrotti
        self._repair_corrupted_data()
        
        # Save the converted data
        if self.lists and self.lists != lists_data:
            self.storage.save(self.lists)
    
    def _extract_real_name(self, name_dict):
        """
        Estrae il nome reale da un dizionario potenzialmente annidato.
        
        Args:
            name_dict: Un dizionario che potrebbe contenere un nome annidato
            
        Returns:
            Il nome reale come stringa
        """
        if not isinstance(name_dict, dict):
            return str(name_dict)
        
        if "name" not in name_dict:
            return ""
        
        if isinstance(name_dict["name"], dict):
            return self._extract_real_name(name_dict["name"])
        else:
            return str(name_dict["name"])
    
    def _repair_corrupted_data(self):
        """
        Ripara i dati corrotti nelle liste.
        """
        for user_id, items in self.lists.items():
            if not isinstance(items, list):
                self.lists[user_id] = []
                continue
                
            repaired_items = []
            for item in items:
                # Se l'elemento non è un dizionario, saltalo
                if not isinstance(item, dict):
                    continue
                    
                # Se name è un dizionario annidato, estraiamo il nome reale
                if "name" in item and isinstance(item["name"], dict):
                    real_name = self._extract_real_name(item["name"])
                    if real_name:
                        repaired_items.append({
                            "name": real_name,
                            "quantity": item.get("quantity", "1")
                        })
                # Se l'elemento ha una struttura valida, lo manteniamo
                elif "name" in item and isinstance(item["name"], str):
                    repaired_items.append(item)
                    
            self.lists[user_id] = repaired_items
    
    def add_item(self, user_id, item_text):
        """
        Add an item to a user's shopping list with optional quantity.
        
        Args:
            user_id: The telegram user ID
            item_text: The item to add, with optional quantity (e.g. "2 kg di patate")
            
        Returns:
            A tuple (success, item_name, quantity) where success is a boolean,
            item_name is the name of the item, and quantity is the quantity string
        """
        user_id = str(user_id)
        if user_id not in self.lists:
            self.lists[user_id] = []
        
        # Parse quantity from the item text
        # Common Italian quantity patterns: "2 kg di patate", "3 patate", "patate (2kg)"
        item_text = item_text.strip()
        quantity = "1"
        item_name = item_text
        
        # Pattern 1: "2 kg di patate" (quantità + unità + "di" + nome)
        pattern1 = re.compile(r'^(\d+(?:[,.]\d+)?)\s*([a-zA-Z]*)\s+(?:di\s+)(.+)$')
        # Pattern 2: "3 patate" (quantità + nome)
        pattern2 = re.compile(r'^(\d+(?:[,.]\d+)?)\s+(.+)$')
        # Pattern 3: "patate (2kg)" (nome + quantità tra parentesi)
        pattern3 = re.compile(r'^(.+?)\s*\((\d+(?:[,.]\d+)?\s*[a-zA-Z]*)\)$')
        
        match1 = pattern1.match(item_text)
        match2 = pattern2.match(item_text) 
        match3 = pattern3.match(item_text)
        
        if match1:
            # Format: "2 kg di patate"
            amount, unit, name = match1.groups()
            quantity = f"{amount} {unit}".strip()
            item_name = name.strip()
        elif match2:
            # Format: "3 patate"
            amount, name = match2.groups()
            # Se non c'è unità di misura, assumiamo "pezzi"
            if amount == "1":
                quantity = "1"  # Per 1 pezzo, manteniamo semplicemente "1"
            else:
                quantity = f"{amount} pz"
            item_name = name.strip()
        elif match3:
            # Format: "patate (2kg)"
            name, amount = match3.groups()
            item_name = name.strip()
            quantity = amount.strip()
        
        # Check if the item already exists
        item_exists = False
        for i, existing_item in enumerate(self.lists[user_id]):
            # Verifica se l'elemento esiste già, gestendo sia il caso di "name" che è una stringa,
            # sia il caso di "name" che è un dizionario (per proteggere da corruzione dati)
            existing_name = existing_item.get("name", "")
            if isinstance(existing_name, dict) and "name" in existing_name:
                # Caso di corruzione dati, estrai il nome vero
                real_name = self._extract_real_name(existing_name)
                if real_name.lower() == item_name.lower():
                    # Sostituisci completamente l'elemento corrotto
                    self.lists[user_id][i] = {"name": item_name, "quantity": quantity}
                    item_exists = True
                    break
            elif existing_name.lower() == item_name.lower():
                # Caso normale, aggiorna la quantità
                self.lists[user_id][i]["quantity"] = quantity
                item_exists = True
                break
        
        if not item_exists and item_name:
            # Add new item
            self.lists[user_id].append({"name": item_name, "quantity": quantity})
        
        self.storage.save(self.lists)
        return (True, item_name, quantity)
    
    def get_items(self, user_id):
        """
        Get all items in a user's shopping list.
        
        Args:
            user_id: The telegram user ID
            
        Returns:
            A list of item dictionaries with 'name' and 'quantity' keys
        """
        user_id = str(user_id)
        return self.lists.get(user_id, [])
    
    def get_item_names(self, user_id):
        """
        Get just the names of all items in a user's shopping list.
        
        Args:
            user_id: The telegram user ID
            
        Returns:
            A list of item names
        """
        items = self.get_items(user_id)
        return [item["name"] for item in items]
    
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
    
    def update_quantity(self, user_id, index, quantity):
        """
        Update the quantity of an item in the shopping list.
        
        Args:
            user_id: The telegram user ID
            index: The index of the item to update
            quantity: The new quantity
            
        Returns:
            True if successful, False otherwise
        """
        user_id = str(user_id)
        if user_id in self.lists and 0 <= index < len(self.lists[user_id]):
            self.lists[user_id][index]["quantity"] = quantity
            self.storage.save(self.lists)
            return True
        return False
