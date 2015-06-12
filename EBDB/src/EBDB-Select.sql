Select Statement used in Python Script


SELECT SP.*, PN.PhoneNumber,
    A1.Street, A1.City, A1.Country, A1.County, A1.PostCode, A1.Unit, A1.Region,
    A2.Street, A2.City, A2.Country, A2.County, A2.PostCode, A2.Unit, A2.Region
FROM SourceProviders as SP
    LEFT JOIN PhoneNumbers PN ON SP.ID = PN.SourceID
    LEFT JOIN (SELECT * FROM Addresses WHERE Type = "m") A1 ON A1.SourceID = SP.ID
    LEFT JOIN (SELECT * FROM Addresses WHERE Type = "p") A2 ON A2.SourceID = SP.ID
WHERE SP.Type = 'Organization';