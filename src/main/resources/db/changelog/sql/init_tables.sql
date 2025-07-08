-- encoding: utf8

CREATE TABLE docs (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    filetype TEXT NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    file_content BYTEA NOT NULL,
    extracted_text TEXT
);
