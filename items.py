import db

def add_item(makeandmodel, location, availability_start, availability_end, price, description, user_id, classes):
    sql = """INSERT INTO items (makeandmodel, location, availability_start, availability_end, price, description, user_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [makeandmodel, location, availability_start, availability_end, price, description, user_id])

    item_id = db.last_insert_id()

    sql = "INSERT INTO vehicle_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def update_image(item_id, image):
    sql = "UPDATE items SET image = ? WHERE id = ?"
    db.execute(sql, [image, item_id])

def get_image(item_id):
    sql = "SELECT image FROM items WHERE id = ?"
    result = db.query(sql, [item_id])
    return result[0][0] if result else None

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
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
                    items.availability_start,
                    items.availability_end,
                    items.location,
                    items.image IS NOT NULL has_image,
                    users.username,
                    users.id user_id
            FROM items, users
            WHERE items.user_id = users.id AND
                  items.id = ?"""
    results = db.query(sql, [item_id])
    return results[0] if results else None

def update_item(item_id, makeandmodel, location, availability_start, availability_end, price, description, classes):
    sql = """UPDATE items SET makeandmodel = ?,
                              location = ?,
                              availability_start = ?,
                              availability_end = ?,
                              price = ?,
                              description = ?
                          WHERE id = ?"""
    db.execute(sql, [makeandmodel, location, availability_start, availability_end, price, description, item_id])

    sql = "DELETE FROM vehicle_classes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO vehicle_classes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [item_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM vehicle_classes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, makeandmodel
            FROM items
            WHERE makeandmodel LIKE ? OR description LIKE ? OR location LIKE ? or price LIKE ?
            ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like, like])

def reserve_item(item_id, user_id, start_date, end_date):
    sql = "INSERT INTO reservations (item_id, user_id, start_date, end_date) VALUES (?, ?, ?, ?)"
    db.execute(sql, [item_id, user_id, start_date, end_date])

def check_reservations(item_id, start_date, end_date):
    sql = """
        SELECT * FROM reservations
        WHERE item_id = ?
        AND (
            (? BETWEEN start_date AND end_date)
            OR (? BETWEEN start_date AND end_date)
            OR (start_date BETWEEN ? AND ?)
        )
    """
    existing = db.query(sql, [item_id, start_date, end_date, start_date, end_date])
    if existing:
        return True

def remove_reservation(res_id):
    sql = "DELETE FROM reservations WHERE id = ?"
    db.execute(sql, [res_id])

def get_item_reservations(item_id):
    sql = "SELECT id, user_id, start_date, end_date FROM reservations WHERE item_id = ? ORDER BY start_date"
    return db.query(sql, [item_id])