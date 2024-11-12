CREATE TABLE `models` (
  `_id` string PRIMARY KEY,
  `name` string,
  `file` blob,
  `description` string,
  `thumbnail` blob,
  `size` integer[],
  `min_coords` integer[],
  `max_coords` integer[]
);

CREATE TABLE `tracks` (
  `_id` string PRIMARY KEY,
  `user_id` string,
  `name` string,
  `track` json COMMENT 'list[name, gltfPath, color, position, rotation',
  `thumbnail` blob
);

CREATE TABLE `users` (
  `_id` string PRIMARY KEY,
  `username` varchar(255),
  `mail` varchar(255),
  `password` varchar(255),
  `avatar` blob
);

CREATE TABLE `sets` (
  `_id` string PRIMARY KEY,
  `user_id` string,
  `name` string,
  `thumbnail` string
);

CREATE TABLE `instruction_models` (
  `_id` string PRIMARY KEY,
  `set_id` string,
  `step` integer,
  `name` string,
  `color` string
);

CREATE TABLE `instruction_steps` (
  `_id` string PRIMARY KEY,
  `set_id` string,
  `step` integer,
  `up_mask` string,
  `up_mask_id` string,
  `down_mask` string,
  `down_mask_id` string
);

CREATE TABLE `reviews` (
  `_id` string PRIMARY KEY,
  `user_id` string,
  `set_id` string,
  `comment` string,
  `rating` number
);

ALTER TABLE `tracks` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`_id`);

CREATE TABLE `models_tracks` (
  `models_name` string,
  `tracks_track` json,
  PRIMARY KEY (`models_name`, `tracks_track`)
);

ALTER TABLE `models_tracks` ADD FOREIGN KEY (`models_name`) REFERENCES `models` (`name`);

ALTER TABLE `models_tracks` ADD FOREIGN KEY (`tracks_track`) REFERENCES `tracks` (`track`);


ALTER TABLE `sets` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`_id`);

ALTER TABLE `instruction_models` ADD FOREIGN KEY (`set_id`) REFERENCES `sets` (`_id`);

ALTER TABLE `instruction_models` ADD FOREIGN KEY (`name`) REFERENCES `models` (`name`);

ALTER TABLE `instruction_steps` ADD FOREIGN KEY (`set_id`) REFERENCES `sets` (`_id`);

ALTER TABLE `reviews` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`_id`);

ALTER TABLE `reviews` ADD FOREIGN KEY (`set_id`) REFERENCES `sets` (`_id`);
