from pymongo import MongoClient


class Database:
    def __init__(self, connection_string, database_name, collection_name):
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database(database_name)
        self.collection = self.db.get_collection(collection_name)

        if database_name not in self.client.list_database_names():
            self.db = self.client[database_name]

        if collection_name not in self.db.list_collection_names():
            self.collection = self.db.create_collection(collection_name)

    def execute_command(self, command):
        command_type = command.get("type")

        if command_type == "find":
            query = command.get("query", {})
            sort = command.get("sort")
            projection = command.get("projection", {})
            if sort:
                result = self.collection.find(query, projection).sort(sort)
            else:
                result = self.collection.find(query, projection)
            return result
        else:
            return None

    def insert_many(self, data):
        self.collection.insert_many(data)

    def create_index(self, index_name, keys, unique=False):
        self.collection.create_index(keys, name=index_name, unique=unique)

    def close_connection(self):
        self.client.close()
