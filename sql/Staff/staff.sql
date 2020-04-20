DROP TABLE IF EXISTS [STAFF];

CREATE TABLE IF NOT EXISTS [STAFF] (
[username] VARCHAR NULL PRIMARY KEY,
[password] VARCHAR NULL,
[is_admin] INTEGER NULL
);

INSERT INTO STAFF VALUES
('admin@fiveteen.com', 'admin', 1),
('staff1@fiveteen.com', 'staff', 0),
('staff2@fiveteen.com', 'staff', 0),
('staff3@fiveteen.com', 'staff', 0),
('staff4@fiveteen.com', 'staff', 0),
('staff5@fiveteen.com', 'staff', 0),
('staff6@fiveteen.com', 'staff', 0);