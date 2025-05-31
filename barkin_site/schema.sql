-- initialize database and drop/create tables

DROP TABLE IF EXISTS SavedEvents;
DROP TABLE IF EXISTS Review;
DROP TABLE IF EXISTS Event;
DROP TABLE IF EXISTS User;

CREATE TABLE User (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT CHECK(Type IN ('User', 'Admin')) NOT NULL,
    Email VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE Event (
    Name VARCHAR(32) NOT NULL,
    Organization Varchar(50) NOT NULL,
    Medium TEXT CHECK(Medium IN ('In Person', 'Online', 'Hybrid')) NOT NULL,
    Duration TEXT CHECK(Duration IN ('One day', 'Multiple days', 'One week', 'Multiple weeks', 'One month', 'Multiple months')) NOT NULL,
    SkillLevel TEXT CHECK(SkillLevel IN ('Beginner', 'Intermediate', 'Professional')) NOT NULL,
    Info TEXT NOT NULL,
    Tags VARCHAR(255) NOT NULL,
    AverageRating REAL,
    Cost INTEGER NOT NULL,
    PRIMARY KEY (Name, Organization)
);

CREATE TABLE Review (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    EventName VARCHAR(32) NOT NULL,
    EventOrganization VARCHAR(50) NOT NULL,
    Rating INTEGER NOT NULL CHECK (Rating >= 1 AND Rating <= 5),
    PublishedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Comments VARCHAR(500) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES User(ID),
    FOREIGN KEY (EventName, EventOrganization) REFERENCES Event(Name, Organization)
);

CREATE TRIGGER UpdateAverageRatingAfterInsert
AFTER INSERT ON Review
BEGIN
    UPDATE Event
    SET AverageRating = (
        SELECT ROUND(AVG(Rating), 1)
        FROM Review
        WHERE Review.EventName = NEW.EventName AND Review.EventOrganization = NEW.EventOrganization
    )
    WHERE Event.Name = NEW.EventName AND Event.Organization = NEW.EventOrganization;
END;

CREATE TABLE SavedEvents (
    UserID INTEGER NOT NULL,
    EventName VARCHAR(32) NOT NULL,
    EventOrganization VARCHAR(50) NOT NULL,
    PRIMARY KEY (UserID, EventName, EventOrganization),
    FOREIGN KEY (UserID) REFERENCES User(ID),
    FOREIGN KEY (EventName, EventOrganization) REFERENCES Event(Name, Organization)
);
