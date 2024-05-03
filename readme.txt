# DMQL-project
# Olympic Games Dataset
# Kavya Elemati, Pallavi Thupakula, Ruchitha Kota

Data Source= https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results?resource=download

The csv file 'Athlete Events' consists of all the required data.
We used python dataframes to split 'Athlete Events' into multiple csv files corresponding to the tables in our database and then imported the csv files into postgres sql.
Some of the columns like eventid, sportid have been generated in python using factorize.

The 120 years Olympic games dataset contains 2 lakhs 70 thousand records. Loading the data with huge records was causing failure while importing in postgres sql.
So, we only considered the first 2000 records for our project.


THE FOLLOWING IS THE PYTHON SCRIPT FOR SPLITTING THE DATA INTO DIFFERENT csv FILES:

import pandas as pd
df = pd.read_csv(r'C:\Users\Kavya\Desktop\dmql project\athlete_events.csv')
df = df.iloc[:2000]

# Function to check if a string contains only alphabets and spaces
def is_alphabetic(name):
  return all(char.isalpha() or char.isspace() for char in name)

# Filter rows in 'Name' column with only alphabets and spaces
df = df[df['Name'].apply(is_alphabetic)]

#Generating the sportid
df['SportID'] = pd.factorize(df['Sport'])[0] + 1

#Generating the eventid
df['EventID'] = df.groupby(['Event']).ngroup() + 1

# Extracting data for Athletes_profile table
athletes_profile_df = df[['ID', 'Name', 'Sex', 'Height', 'Weight']].drop_duplicates()

# Extracting data for participation table
participation_df = df[['ID', 'Age', 'NOC', 'Games', 'EventID']].drop_duplicates()

# Generating participationID
participation_df['participationID'] = range(1, len(participation_df) + 1)
# Move participation_id to the first column 
participation_df = pd.concat([participation_df['participationID'], participation_df.drop('participationID', axis=1)], axis=1)

# Writing to CSV files
athletes_profile_df.to_csv('athletes_profile.csv', index=False)
participation_df.to_csv('participation.csv', index=False)

Event_table_df = df[['EventID','Event']].drop_duplicates()
Event_table_df.to_csv('Event_table.csv', index=False)

Sport_table_df = df[['SportID','Sport']].drop_duplicates()
Sport_table_df.to_csv('Sport_table.csv', index=False)

EventSport_table = ['EventID','SportID']
EventSport_table_df = df[['EventID','SportID']].drop_duplicates()
EventSport_table_df.to_csv('EventSport_table.csv', index=False)

Host_table = ['City','Year','Season','Games']
Host_table_df = df[Host_table].drop_duplicates()

Medal_table = ['ID','Name','Games','EventID','Medal']     
#ID is the athlete_id
Medal_table_df = df[Medal_table].drop_duplicates()

Host_table_df.to_csv('Hosts table.csv', index=False)
Medal_table_df.to_csv('Medal table.csv', index=False)


TABLE CREATION:

CREATE TABLE IF NOT EXISTS AthletesProfile(
	ID INT NOT NULL,
	NAME VARCHAR(70),
	SEX CHAR,
	HEIGHT INT,
	WEIGHT INT,
	PRIMARY KEY(ID)
)


CREATE TABLE IF NOT EXISTS Country(
	NOC CHAR(3),
	COUNTRY VARCHAR(60),
	PRIMARY KEY(NOC)
);

CREATE TABLE IF NOT EXISTS Events(
	EVENTID INT NOT NULL,
	EVENTNAME VARCHAR(100),
	PRIMARY KEY(EVENTID)
);


CREATE TABLE Participation (
    participationID INT,
    ID INT,
    Age INT,
    NOC VARCHAR(255),
    Games VARCHAR(255),
    EventID INT
);

ALTER TABLE Participation
ADD PRIMARY KEY (participationID);

-- Adding a foreign key that references AthletesProfile table
ALTER TABLE Participation
ADD CONSTRAINT fk_athletes_profile
FOREIGN KEY (ID) REFERENCES AthletesProfile(ID);

-- Adding a foreign key that references Country table
ALTER TABLE Participation
ADD CONSTRAINT fk_country
FOREIGN KEY (NOC) REFERENCES Country(NOC);

-- Adding a foreign key that references Events table
ALTER TABLE Participation
ADD CONSTRAINT fk_events
FOREIGN KEY (EventID) REFERENCES Events(EventID);




CREATE TABLE Sports(
	SPORTID INT NOT NULL,
	SPORTNAME VARCHAR(50),
	PRIMARY KEY(SPORTID)
);

CREATE TABLE EventSport(
	EVENTID INT NOT NULL,
	SPORTID INT NOT NULL,
	PRIMARY KEY(EVENTID),
	FOREIGN KEY(EVENTID) REFERENCES Events,
	FOREIGN KEY(SPORTID) REFERENCES Sports
);



CREATE TABLE Hosts (
    City VARCHAR(255) PRIMARY KEY,
    Year INT,
    Season VARCHAR(255),
	Games VARCHAR(255)
);


CREATE TABLE Medals (
    ID INT,
    Name VARCHAR(255),
    Games VARCHAR(255),
    EventID INT,
    Medal VARCHAR(255)
);

-- Adding a FOREIGN KEY constraint that references AthletesProfile
ALTER TABLE Medals
ADD CONSTRAINT fk_athlete_id
FOREIGN KEY (ID) REFERENCES AthletesProfile(ID);

-- Adding a FOREIGN KEY constraint that references Events
ALTER TABLE Medals
ADD CONSTRAINT fk_event_id
FOREIGN KEY (EventID) REFERENCES Events(EventID);




QUERIES :

1)insert into:
insert into athletesprofile(id, name, sex, height, weight) 
values (1500, 'Kavya', 'F',160,59);

insert into participation(participationid, id, age, noc, games, eventid) 
values (1240, 1500, 23, 'IND', '2016 Summer',112);

2)Update:
update athletesprofile set weight=45 where name='Pallavi';

3)Delete:
delete from participation
where participation.participationid=1230

4)Finding the name of the Event a particular athlete participated in:

select athletesprofile.name,events.eventname 
from athletesprofile, participation, events 
where athletesprofile.name='Kavya' and 
athletesprofile.id=participation.id and 
participation.eventid=events.eventid;

5) Query to find the total number of medals won by each country in a specific year.
select c.country, count(m.medal) as totalmedals
from medals m
join athletesprofile ap on m.id=ap.id
join participation p on ap.id=p.id
join country c on p.noc=c.noc
join hosts h on p.games=h.games
where h.year=2016 and m.medal is not null
group by c.country
order by totalmedals desc;


6)Query to find the most popular sport by number of participants in the latest Olympics

select s.sportname, count(distinct p.id) as numberofparticipants
from sports s
join eventsport es on s.sportid=es.sportid
join events e on es.eventid=e.eventid
join participation p on e.eventid=p.eventid
join hosts h on p.games=h.games
where h.year= (select max(year) from hosts)
group by s.sportname
order by numberofparticipants desc
LIMIT 1;

7) Query to determine the average age of medalists for each Olympic Games:

select 
	h.games,
	avg(p.age) as averageage
from medals m
join participation p on m.id=p.id
join hosts h on p.games=h.games
where m.medal is not null
group by h.games
order by min(h.year);


8)Query to find athletes who have participated in both the Summer and Winter Olympics:

select
	ap.name,
	string_agg(distinct h.season, ', ' order by h.season) as seasonsparticipated
from athletesprofile ap
join participation p on ap.id=p.id
join hosts h on p.games=h.games
group by ap.name
having count(distinct h.season)>1

9)Query to find the event that had the highest number of participating athletes in the last Olympic games:

select
	e.eventname,
	count (distinct p.id) as participants
from events e
join participation p on e.eventid=p.eventid
join hosts h on p.games=h.games
where h.year=(select max(year) from hosts)
group by e.eventname
order by participants desc
limit 1;


INDEXING:

CREATE INDEX idx_medals_id_medal ON Medals(ID, Medal);
CREATE INDEX idx_athletesprofile_id ON AthletesProfile(ID);
CREATE INDEX idx_participation_id_noc_games ON Participation(ID, NOC, Games);
CREATE INDEX idx_country_noc ON Country(NOC);
CREATE INDEX idx_hosts_games_year ON Hosts(Games, Year);