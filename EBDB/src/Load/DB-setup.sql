CREATE TABLE IF NOT EXISTS Specialities(
	ParentID		INT,
	ID			INT,
	Title			VARCHAR(100),
	Code			VARCHAR(30),
	URL			VARCHAR(1000),
	PRIMARY KEY(ID)
);
CREATE TABLE IF NOT EXISTS SourceProviders(
	ID			INT NOT NULL,
	Type			VARCHAR(12) NOT NULL,
	Name            VARCHAR(100),
	Gender 			VARCHAR(20),
	DoB 			VARCHAR(20),
	IsSoleProprietor	VARCHAR(1),
	PrimarySpeciality	VARCHAR(30),
	SecondarySpeciality	VARCHAR(30), 
	PRIMARY KEY(ID)
	/*FOREIGN KEY(PrimarySpeciality) REFERENCES Specialities(ID),
	FOREIGN KEY(SecondarySpeciality) REFERENCES Specialities(ID)*/
);
CREATE TABLE IF NOT EXISTS PhoneNumbers(
	SourceID		INT,
	PhoneNumber 		VARCHAR(20),
	FOREIGN KEY(sourceID) REFERENCES SourceProviders(ID)
);
CREATE TABLE IF NOT EXISTS Addresses(
	SourceID			INT,
	Type			CHAR(1),
	Street			VARCHAR(100),
	City			VARCHAR(50),
	Country			VARCHAR(50),
	County			VARCHAR(50),
	PostCode		VARCHAR(20),
	Unit			VARCHAR(60),
	Region			VARCHAR(20),
	PRIMARY KEY(SourceID, Type),
	FOREIGN KEY(SourceID) REFERENCES SourceProviders(ID)
);

CREATE TABLE IF NOT EXISTS MasterProviders(
	ID			INT UNIQUE NOT NULL AUTO_INCREMENT,
	Type			VARCHAR(12) NOT NULL,
    FirstName		VARCHAR(100),
    MiddleName      VARCHAR(100),
    LastName        VARCHAR(100),
    Credential      VARCHAR(50),
    Prefix      VARCHAR(50),
    Suffix      VARCHAR(50),
	DoB 			DATE,
	IsSoleProprietor	VARCHAR(1),
	Gender			VARCHAR(1),
	PRIMARY KEY(ID)
);


CREATE TABLE IF NOT EXISTS Audit(
	AuditNum		INT UNIQUE NOT NULL AUTO_INCREMENT,
    SourceID        INT,
    ComparisonID    INT,
	Comment			VARCHAR(300),
    PRIMARY KEY(AuditNum)
);
CREATE TABLE IF NOT EXISTS MasteredSpeciality1(
	MasterID		INT,
	Speciality		INT,
	PRIMARY KEY(MasterID, Speciality),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(Speciality) REFERENCES Specialities(ID)
);
CREATE TABLE IF NOT EXISTS MasteredSpeciality2(
	MasterID 		INT,
	Speciality 		INT,
	PRIMARY KEY(MasterID, Speciality),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(Speciality) REFERENCES Specialities(ID)
);
CREATE TABLE IF NOT EXISTS Crosswalk(
	SourceID		INT,
	MasterID		INT,
	PRIMARY KEY(SourceID, MasterID),
	FOREIGN KEY(SourceID) REFERENCES SourceProviders(ID),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID)
);
CREATE TABLE IF NOT EXISTS MasteredWorksAt(
	MasterID		INT,
	SourceID		INT,
	PRIMARY KEY(MasterID, SourceID),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(SourceID) REFERENCES SourceProviders(ID)
);
CREATE TABLE IF NOT EXISTS ReceivesMasteredMailAt(
	MasterID		INT,
	SourceID		INT,
	PRIMARY KEY(MasterID, SourceID),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(SourceID) REFERENCES SourceProviders(ID)
);

CREATE TABLE IF NOT EXISTS Changes(
	AuditNumber		INT,
	MasterID		INT,
	SourceID		INT,
	PRIMARY KEY(AuditNumber, MasterID, SourceID),
	FOREIGN KEY(AuditNumber) REFERENCES Audit(AuditNum),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(SourceID) REFERENCES SourceProviders(ID)
);

CREATE TABLE IF NOT EXISTS MasteredHasPhoneNumber(
	MasterID		INT,
	SourceID		INT,
	PRIMARY KEY(MasterID, SourceID),
	FOREIGN KEY(MasterID) REFERENCES MasterProviders(ID),
	FOREIGN KEY(SourceID) REFERENCES PhoneNumbers(SourceID)
);
