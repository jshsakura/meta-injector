
import sqlite3
import re
import difflib

def normalize_title(title):
    # Lowercase, remove content in parentheses, and remove non-alphanumeric characters
    title = title.lower()
    title = re.sub(r'\(.*?\)', '', title)
    title = re.sub(r'[^\w\s]', '', title) # more permissive than just a-z0-9
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def create_wii_title_db(wiitdb_path):
    wii_db = {}
    wii_db_raw = {}
    with open(wiitdb_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                parts = line.split('=', 1)
                game_id = parts[0].strip()
                title = parts[1].strip()
                if len(game_id) == 6:
                    normalized = normalize_title(title)
                    if normalized not in wii_db:
                        wii_db[normalized] = game_id
                        wii_db_raw[title] = game_id
    return wii_db, wii_db_raw

def find_missing_ids(db_path, wii_db, wii_db_raw):
    conn = sqlite3.connect(db_path)
    conn.text_factory = lambda b: b.decode(errors='ignore')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, region FROM games WHERE game_id IS NULL OR game_id = ''")
    missing_games = cursor.fetchall()
    conn.close()

    update_statements = []
    manual_review = []
    
    wii_titles = list(wii_db.keys())

    for db_id, title, region in missing_games:
        # Strategy 1: Direct match on normalized title
        normalized_title = normalize_title(title)
        if normalized_title in wii_db:
            found_game_id = wii_db[normalized_title]
            sql = f"UPDATE games SET game_id = '{found_game_id}' WHERE id = {db_id};"
            update_statements.append(sql)
            print(f"-- Found a direct match for '{title}' ({region}): {found_game_id}")
            continue

        # Strategy 2: Fuzzy matching
        matches = difflib.get_close_matches(normalized_title, wii_titles, n=1, cutoff=0.8)
        if matches:
            best_match = matches[0]
            found_game_id = wii_db[best_match]
            
            # Check for Korean characters to flag for manual review
            if re.search(r'[\uac00-\ud7a3]', title):
                manual_review.append(f"-- Manual Review Needed for '{title}' ({region}): Matched with '{best_match}' -> {found_game_id}")
            else:
                sql = f"UPDATE games SET game_id = '{found_game_id}' WHERE id = {db_id};"
                update_statements.append(sql)
                print(f"-- Found a fuzzy match for '{title}' ({region}): '{best_match}' with game ID {found_game_id}")
        else:
            print(f"-- No match for '{title}' ({region})")

    return update_statements, manual_review

if __name__ == '__main__':
    wii_db, wii_db_raw = create_wii_title_db('resources/wiitdb.txt')
    
    # Special cases
    wii_db['acdc live rock band track pack'] = 'R33E69'
    wii_db['another code r'] = 'RNOP01'
    wii_db['godziller unleashed'] = 'RGZE70'


    updates, manual_reviews = find_missing_ids('resources/compatibility.db', wii_db, wii_db_raw)
    
    if updates:
        print("\n-- Generated SQL Update Statements:")
        for sql in updates:
            print(sql)
        
        # Execute the updates
        try:
            conn = sqlite3.connect('resources/compatibility.db')
            cursor = conn.cursor()
            for sql in updates:
                cursor.execute(sql)
            conn.commit()
            print(f"\n-- Successfully executed {len(updates)} updates on the database.")
        except sqlite3.Error as e:
            print(f"\n-- An error occurred: {e}")
        finally:
            if conn:
                conn.close()
    else:
        print("\n-- No automatic updates to perform.")

    if manual_reviews:
        print("\n-- These matches require manual review and were not automatically updated:")
        for review in manual_reviews:
            print(review)
