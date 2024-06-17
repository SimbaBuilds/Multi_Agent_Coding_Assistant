#crud.py
code = """

class Item:
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Item(id={self.id}, name={self.name}, description={self.description})"

class CRUDApp:
    def __init__(self):
        self.items = []

    def create_item(self, id, name, description=None):
        item = Item(id, name, description)
        self.items.append(item)
        return item

    def read_item(self, id):
        for item in self.items:
            if item.id == id:
                return item
        return None

    def update_item(self, id, name=None, description=None):
        for item in self.items:
            if item.id == id:
                if name:
                    item.name = name
                if description:
                    item.description = description
                return item
        return None

    def delete_item(self, id):
        for index, item in enumerate(self.items):
            if item.id == id:
                return self.items.pop(index)
        return None

    def list_items(self):
        return self.items
        
    """
        



