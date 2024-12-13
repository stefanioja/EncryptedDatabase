CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  current_key_id INTEGER,
  FOREIGN KEY (current_key_id) REFERENCES keys(id) 
);

CREATE TABLE IF NOT EXISTS keys (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  e TEXT,
  n TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS files (
  id INTEGER PRIMARY KEY,
  filename TEXT,
  path TEXT,
  public_key_id INTEGER,
  user_id INTEGER,
  FOREIGN KEY (public_key_id) REFERENCES keys(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
  UNIQUE (user_id, filename)
);
