from tinydb import Query, TinyDB


def upsert_objects(db, objects, unique_id_field="id"):
    """
    Efficiently inserts or updates a list of objects in the database.

    Args:
        db (TinyDB): The database instance.
        objects (list[dict]): The list of objects to insert or update.
        unique_id_field (str): The field that represents the unique ID.

    Returns:
        tuple: (inserted_count, updated_count), counts of new and updated objects.
    """
    # Fetch all existing records and create a lookup for unique IDs
    existing_records = {
        doc[unique_id_field]: doc for doc in db.all() if unique_id_field in doc
    }

    new_objects = []
    updated_objects = []

    for obj in objects:
        unique_id = obj[unique_id_field]
        if unique_id in existing_records:
            # Check if the object needs to be updated (optional: compare fields)
            if obj != existing_records[unique_id]:  # Only update if the object differs
                updated_objects.append((obj, unique_id))
        else:
            # Insert if the ID is not found
            new_objects.append(obj)

    # Perform batch inserts and updates
    if new_objects:
        db.insert_multiple(new_objects)
    for obj, unique_id in updated_objects:
        db.update(obj, Query()[unique_id_field] == unique_id)

    return len(new_objects), len(updated_objects)
