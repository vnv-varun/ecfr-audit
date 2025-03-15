CREATE TABLE agency (
	id INTEGER NOT NULL, 
	identifier VARCHAR(255), 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	url VARCHAR(255), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_agency_id ON agency (id);
CREATE UNIQUE INDEX ix_agency_identifier ON agency (identifier);
CREATE TABLE term (
	id INTEGER NOT NULL, 
	term VARCHAR(255) NOT NULL, 
	total_occurrences INTEGER NOT NULL, 
	document_occurrences INTEGER NOT NULL, 
	updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	PRIMARY KEY (id)
);
CREATE INDEX ix_term_id ON term (id);
CREATE INDEX ix_term_term ON term (term);
CREATE TABLE title (
	id INTEGER NOT NULL, 
	number INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	agency_id INTEGER, 
	reserved BOOLEAN, 
	full_name VARCHAR(255), 
	description TEXT, 
	up_to_date_as_of DATETIME, 
	latest_amended_on DATETIME, 
	latest_issue_date DATETIME, 
	source_url VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(agency_id) REFERENCES agency (id)
);
CREATE INDEX ix_title_id ON title (id);
CREATE TABLE regulation (
	id INTEGER NOT NULL, 
	identifier VARCHAR(255), 
	title_id INTEGER, 
	agency_id INTEGER, 
	label VARCHAR(255), 
	name VARCHAR(255) NOT NULL, 
	html_url VARCHAR(255), 
	html_content TEXT, 
	text_content TEXT, 
	created_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(title_id) REFERENCES title (id), 
	FOREIGN KEY(agency_id) REFERENCES agency (id)
);
CREATE UNIQUE INDEX ix_regulation_identifier ON regulation (identifier);
CREATE INDEX ix_regulation_id ON regulation (id);
CREATE TABLE chapter (
	id INTEGER NOT NULL, 
	number VARCHAR(10) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	title_id INTEGER, 
	identifier VARCHAR(50), 
	description TEXT, 
	agency_name VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(title_id) REFERENCES title (id)
);
CREATE INDEX ix_chapter_id ON chapter (id);
CREATE TABLE regulation_reference (
	source_id INTEGER NOT NULL, 
	target_id INTEGER NOT NULL, 
	PRIMARY KEY (source_id, target_id), 
	FOREIGN KEY(source_id) REFERENCES regulation (id), 
	FOREIGN KEY(target_id) REFERENCES regulation (id)
);
CREATE TABLE subchapter (
	id INTEGER NOT NULL, 
	identifier VARCHAR(50) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	chapter_id INTEGER, 
	description TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(chapter_id) REFERENCES chapter (id)
);
CREATE INDEX ix_subchapter_id ON subchapter (id);
CREATE TABLE term_frequency (
	id INTEGER NOT NULL, 
	term_id INTEGER, 
	regulation_id INTEGER, 
	frequency INTEGER NOT NULL, 
	tfidf_score FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(term_id) REFERENCES term (id), 
	FOREIGN KEY(regulation_id) REFERENCES regulation (id)
);
CREATE INDEX ix_term_frequency_id ON term_frequency (id);
CREATE TABLE part (
	id INTEGER NOT NULL, 
	number INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	title_id INTEGER, 
	chapter_id INTEGER, 
	subchapter_id INTEGER, 
	full_identifier VARCHAR(50), 
	description TEXT, 
	authority_note TEXT, 
	source_note TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(title_id) REFERENCES title (id), 
	FOREIGN KEY(chapter_id) REFERENCES chapter (id), 
	FOREIGN KEY(subchapter_id) REFERENCES subchapter (id)
);
CREATE INDEX ix_part_id ON part (id);
CREATE TABLE subpart (
	id INTEGER NOT NULL, 
	identifier VARCHAR(50) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	part_id INTEGER, 
	description TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(part_id) REFERENCES part (id)
);
CREATE INDEX ix_subpart_id ON subpart (id);
CREATE TABLE section (
	id INTEGER NOT NULL, 
	number VARCHAR(50) NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	part_id INTEGER, 
	subpart_id INTEGER, 
	text_content TEXT, 
	html_content TEXT, 
	full_identifier VARCHAR(50), 
	source_url VARCHAR(255), 
	effective_date DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(part_id) REFERENCES part (id), 
	FOREIGN KEY(subpart_id) REFERENCES subpart (id)
);
CREATE INDEX ix_section_id ON section (id);
CREATE TABLE paragraph (
	id INTEGER NOT NULL, 
	identifier VARCHAR(50), 
	section_id INTEGER, 
	parent_id INTEGER, 
	text_content TEXT NOT NULL, 
	level INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(section_id) REFERENCES section (id), 
	FOREIGN KEY(parent_id) REFERENCES paragraph (id)
);
CREATE INDEX ix_paragraph_id ON paragraph (id);
CREATE TABLE regulation_metrics (
	id INTEGER NOT NULL, 
	regulation_id INTEGER, 
	title_id INTEGER, 
	agency_id INTEGER, 
	part_id INTEGER, 
	section_id INTEGER, 
	word_count INTEGER NOT NULL, 
	section_count INTEGER NOT NULL, 
	paragraph_count INTEGER NOT NULL, 
	avg_word_length FLOAT, 
	avg_sentence_length FLOAT, 
	readability_score FLOAT, 
	version_number INTEGER NOT NULL, 
	word_count_change INTEGER, 
	calculated_at DATETIME DEFAULT (CURRENT_TIMESTAMP), 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(regulation_id) REFERENCES regulation (id), 
	FOREIGN KEY(title_id) REFERENCES title (id), 
	FOREIGN KEY(agency_id) REFERENCES agency (id), 
	FOREIGN KEY(part_id) REFERENCES part (id), 
	FOREIGN KEY(section_id) REFERENCES section (id)
);
CREATE INDEX ix_regulation_metrics_id ON regulation_metrics (id);
