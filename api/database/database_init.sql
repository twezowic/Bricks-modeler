CREATE TABLE COLORS (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rgb VARCHAR(6),
    is_trans VARCHAR(1)
);

CREATE TABLE SETS (
    id INT PRIMARY KEY,
    set_num VARCHAR(255),
    name VARCHAR(256),
    year INT,
    num_parts INT,
    img_url VARCHAR(255)
);

CREATE TABLE PARTS (
    part_num VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE INVENTORY_PARTS (
    inventory_id INT NULL,
    part_num VARCHAR(100),
    color_id INT,
    quantity INT,
    is_spare VARCHAR(1),
    img_url VARCHAR(255),
    FOREIGN KEY (inventory_id) REFERENCES SETS(id),
    FOREIGN KEY (part_num) REFERENCES PARTS(part_num),
    FOREIGN KEY (color_id) REFERENCES COLORS(id)
);
