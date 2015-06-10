Our audit information is in a file named "Audit_<groupstamp>.txt". It contains the following columns:
* sId: The source record this audit line applies to
* mId: The master record the source record was merged into
* other: (nullable) The id of the opposing source record which this record
  matched to and which caused this record to be merged into master mId. Null if
  this record didn't match any other records
* score: (nullable) The total score of the match between this record and other for the rule under consideration. Null if this record didn't match any other records
* rule: The rule under consideration. Formatted as a string: '[field, field, field, ...] => max_score'. This string can be generated using only data in the configuration file, thus, it makes it possible to determine the exact effect of a given rule in the configuration file.

