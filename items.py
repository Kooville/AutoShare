import db

def add_item(makeandmodel, location, availability, price, description, user_id, classes):
    sql = """INSERT INTO items (makeandmodel, location, availability, price, description, user_id) 
            VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [makeandmodel, location, availability, price, description, user_id])

    item_id = db.last_insert_id()

    sql = "INSERT INTO vehicle_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_items():
    sql = "SELECT id, makeandmodel, price, location FROM items ORDER BY id DESC"
    return db.query(sql)

def get_classes(item_id):
    sql = "SELECT title, value FROM vehicle_classes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_item(item_id):
    sql = """SELECT items.id,
                    items.makeandmodel,
                    items.description,
                    items.price,
                    items.availability,
                    items.location,
                    users.username,
                    users.id user_id
            FROM items, users
            WHERE items.user_id = users.id AND
                  items.id = ?"""
    results = db.query(sql, [item_id])
    return results[0] if results else None

def update_item(item_id, makeandmodel, location, availability, price, description, classes):
    sql = """UPDATE items SET makeandmodel = ?,
                              location = ?,
                              availability = ?,
                              price = ?,
                              description = ?
                          WHERE id = ?"""
    db.execute(sql, [makeandmodel, location, availability, price, description, item_id])

    sql = "DELETE FROM vehicle_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO vehicle_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, makeandmodel
            FROM items
            WHERE makeandmodel LIKE ? OR description LIKE ? OR location LIKE ? or price LIKE ? or availability LIKE ?
            ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like, like, like])