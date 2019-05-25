class Host:
    def __init__(self):
        from pymongo import MongoClient

        client = MongoClient()
        db = client['analysbot']
        self.tokens_db = db['tokens']

    def contains_token(self, user_id):
        return self.tokens_db.find_one({'_id': user_id}) is not None

    def get_token(self, user_id):
        user_data = self.tokens_db.find_one({'_id': user_id})
        return user_data['token']

    def add_token(self, user_id, oauth_token):
        self.tokens_db.insert({'_id': user_id, 'token': oauth_token})

    def update_token(self, user_id, oauth_token):
        self.tokens_db.update({'_id': user_id}, {'$set': {'token': oauth_token}})
