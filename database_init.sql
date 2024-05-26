CREATE TABLE THEMES (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    parent_id INT
);

CREATE TABLE SETS (
    set_num INT PRIMARY KEY,
    name VARCHAR(255),
    year INT,
    theme_id INT,
    num_parts INT,
    img_url VARCHAR(255)
);

CREATE TABLE PARTS (
    part_num INT PRIMARY KEY,
    name VARCHAR(255),
    part_cat_id INT,
    part_material VARCHAR(255)
);

CREATE TABLE PART_RELATIONSHIPS (
    child_part_num INT PRIMARY KEY,
    rel_type VARCHAR(1),
    parent_part_num INT
);

CREATE TABLE PART_CATEGORIES ( -- +
    id INT PRIMARY KEY,
    name VARCHAR(200)
);

CREATE TABLE MINIFIGS ( -- +
    fig_num VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255),
    num_parts INT,
    img_url VARCHAR(255)
);

CREATE TABLE INVENTORY_SETS (
    inventory_id INT PRIMARY KEY,
    set_num VARCHAR(255),
    quantity INT
);

CREATE TABLE INVENTORY_PARTS (
    inventory_id INT PRIMARY KEY,
    part_num VARCHAR(255),
    color_id INT,
    quantity INT,
    is_spare VARCHAR(1),
    img_url VARCHAR(255)
);

CREATE TABLE INVENTORY_MINIFIGS ( -- + moze dodac klucz glowny
    inventory_id INT,
    fig_num VARCHAR(20),
    quantity INT,
    FOREIGN KEY (fig_num) REFERENCES MINIFIGS(fig_num),
    FOREIGN KEY (inventory_id) REFERENCES INVENTORIES(id)
);

CREATE TABLE INVENTORIES (
    id INT PRIMARY KEY,
    version VARCHAR(255),
    set_num VARCHAR(255)
);

CREATE TABLE ELEMENTS (
    element_id INT PRIMARY KEY,
    part_num VARCHAR(255),
    color_id INT,
    design_id INT
);

CREATE TABLE COLORS (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rgb INT, -- jest jako hex zapiswany i trzeba uzyc funkcji HEX przed dodaniem wartosci do tabeli
    is_trans VARCHAR(1)
);


