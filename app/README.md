## Application structure

### Frontend

* Accept range of IP addresses
* Provide way to modify the default security parameters config
* Requests start of search from `parser`

### Parser

* Accepts IP addresses range and custom config from frontend
* Validates input config
* Reports immediately to `frontend` with unique id to later query the reports
* Visits host devices according to the config and collects used sertificates into DB
* After visiting all addresses requests a report from `analyzer`

### Analyzer

* Accepts the config and range of sertificates needed to be analyzed
* Does the analysis and sends the reports to the user
