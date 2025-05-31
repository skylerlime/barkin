INSERT INTO Event (Name, Organization, Medium, Duration, SkillLevel, Info, Tags, AverageRating, Cost) VALUES
('Intro to Python', 'CodeAcademy', 'Online', 'One week', 'Beginner', 'Learn the basics of Python programming.', 'python programming', 4, 0),
('Advanced Data Science', 'DataSciPro', 'Hybrid', 'One month', 'Professional', 'Dive deep into machine learning and AI.', 'data science ML AI', 5, 200),
('Creative Writing Workshop', 'WritersHub', 'In Person', 'Multiple days', 'Intermediate', 'Improve your storytelling and writing skills.', 'writing creativity', 3, 50),
('Yoga for Beginners', 'WellnessOrg', 'Online', 'One day', 'Beginner', 'Start your yoga journey with this intro session.', 'health yoga', 5, 10),
('Digital Marketing Bootcamp', 'MarketMasters', 'Hybrid', 'Multiple weeks', 'Intermediate', 'Master modern marketing strategies.', 'marketing business', 4, 150);

INSERT INTO Review (UserID, EventName, EventOrganization, Rating, Comments) VALUES
(1, 'Intro to Python', 'CodeAcademy', 5, 'Fantastic introduction to Python. Very beginner-friendly.'),
(2, 'Intro to Python', 'CodeAcademy', 4, 'Good course, but could use more exercises.'),
(3, 'Advanced Data Science', 'DataSciPro', 5, 'Challenging and informative, great for professionals.'),
(1, 'Creative Writing Workshop', 'WritersHub', 3, 'Decent workshop, but needed more interactive parts.'),
(2, 'Yoga for Beginners', 'WellnessOrg', 5, 'Loved it! Felt refreshed and energized.'),
(3, 'Digital Marketing Bootcamp', 'MarketMasters', 4, 'Useful strategies, great pacing.'),
(1, 'Digital Marketing Bootcamp', 'MarketMasters', 4, 'Good content, but some sections were rushed.');

INSERT INTO User (Type, Email, Password) VALUES
('Admin', 'admin@example.com', 'scrypt:32768:8:1$v6kjwItH2gDwj0lu$bcf7620fcc65956ce2eb86f58feacde5b37809c5aaa76a63cb79fe8f4a671fe2cd022e7d208db21292cbeafc8b7976dbded5c78fb130ef5528881e06b901678d'),
('User', 'alice@example.com', 'scrypt:32768:8:1$v6kjwItH2gDwj0lu$bcf7620fcc65956ce2eb86f58feacde5b37809c5aaa76a63cb79fe8f4a671fe2cd022e7d208db21292cbeafc8b7976dbded5c78fb130ef5528881e06b901678d'),
('User', 'bob@example.com', 'scrypt:32768:8:1$v6kjwItH2gDwj0lu$bcf7620fcc65956ce2eb86f58feacde5b37809c5aaa76a63cb79fe8f4a671fe2cd022e7d208db21292cbeafc8b7976dbded5c78fb130ef5528881e06b901678d'),
('User', 'charlie@example.com', 'scrypt:32768:8:1$v6kjwItH2gDwj0lu$bcf7620fcc65956ce2eb86f58feacde5b37809c5aaa76a63cb79fe8f4a671fe2cd022e7d208db21292cbeafc8b7976dbded5c78fb130ef5528881e06b901678d');