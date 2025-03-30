import db

def add_item(makeandmodel, type, location, availability, price, description, user_id):
    sql = """INSERT INTO items (makeandmodel, type, location, availability, price, description, user_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [makeandmodel, type, location, availability, price, description, user_id])

def get_items():
    sql = "SELECT id, makeandmodel, type, location FROM items ORDER BY id DESC"
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.makeandmodel,
                    items.type,
                    items.description,
                    items.price,
                    items.location,
                    users.username
            FROM items, users
            WHERE items.user_id = users.id AND
                  items.id = ?"""
    return db.query(sql, [item_id])[0]