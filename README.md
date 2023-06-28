# Automated linting scanner

Background: We wanted to scan all our GitLab projects for a valid gitlab-ci.yml.

This repo runs a CI Job which scans all accessible repositories if their gitlab-ci.yml is valid and creates a ticket with the scan result if it is invalid..

If you fixed the findings you can close the created issue and this job will automatically reopen and update the existing ticket if there are new issues found.

## Documentation

Please have a look at our official documentation: [https://github.com/telekom-mms/gitlab-linting-scanner](https://github.com/telekom-mms/gitlab-linting-scanner)

## Contributing

If you want to contribute you can create a merge request so other colleagues will discuss the code with you. Make sure to add both a good and a bad practice to your code example.

## License

Copyright 2023 Telekom MMS GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Author Information
- Christopher Grau
- Sebastian Gumprich
- Christoph Sieber
- Henrik Hülle
- Andreas Hering
- Sebastian Bieger
- Daniel Uhlmann
