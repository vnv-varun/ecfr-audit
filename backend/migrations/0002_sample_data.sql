-- Sample data for eCFR Analyzer database

-- Sample titles (with explicit IDs to match foreign keys)
INSERT INTO titles (id, title_number, title_name) VALUES 
(1, 1, 'General Provisions'),
(2, 2, 'Grants and Agreements'),
(3, 3, 'The President'),
(4, 5, 'Administrative Personnel'),
(5, 7, 'Agriculture'),
(6, 10, 'Energy'),
(7, 12, 'Banks and Banking'),
(8, 14, 'Aeronautics and Space'),
(9, 15, 'Commerce and Foreign Trade'),
(10, 17, 'Commodity and Securities Exchanges'),
(11, 26, 'Internal Revenue'),
(12, 40, 'Protection of Environment');

-- Sample agencies
INSERT INTO agencies (id, agency_name, agency_code, title_id) VALUES
(1, 'Office of the Federal Register', 'OFR', 1),
(2, 'Office of Management and Budget', 'OMB', 2),
(3, 'Executive Office of the President', 'EOP', 3),
(4, 'Office of Personnel Management', 'OPM', 4),
(5, 'Department of Agriculture', 'USDA', 5),
(6, 'Department of Energy', 'DOE', 6),
(7, 'Federal Reserve System', 'FRS', 7),
(8, 'National Aeronautics and Space Administration', 'NASA', 8),
(9, 'Department of Commerce', 'DOC', 9),
(10, 'Securities and Exchange Commission', 'SEC', 10),
(11, 'Internal Revenue Service', 'IRS', 11),
(12, 'Environmental Protection Agency', 'EPA', 12);

-- Sample metrics
INSERT INTO metrics (id, title_id, agency_id, word_count, sentence_count, complexity_score) VALUES
(1, 1, 1, 125000, 5200, 8.2),
(2, 2, 2, 85000, 3800, 9.1),
(3, 3, 3, 42000, 1800, 7.5),
(4, 4, 4, 320000, 14500, 9.7),
(5, 5, 5, 750000, 32000, 8.9),
(6, 6, 6, 420000, 18200, 9.3),
(7, 7, 7, 680000, 28500, 10.2),
(8, 8, 8, 180000, 7800, 8.5),
(9, 9, 9, 315000, 13200, 9.2),
(10, 10, 10, 520000, 21500, 10.5),
(11, 11, 11, 1250000, 52000, 11.2),
(12, 12, 12, 890000, 38000, 9.8);