# CAPS Research Chat — Privacy design notes

> Product and engineering draft. Obtain jurisdiction-specific legal review before a public launch.

## Two user modes

### Research mode

The service stores the user's query and the model response in encrypted form so the user can export or delete the session data. A separate de-identified research record is created for AI-safety research and product improvement under the displayed consent version.

### Private mode

The server forwards the conversation to the configured model provider but does not persist the query, response, or feedback. The browser keeps only the current page's in-memory history.

## Data categories

Research mode may store:

- user query and model response, encrypted at the application layer;
- provider, requested model, latency and token-usage metadata;
- consent version and timestamp;
- optional thumbs-up/down feedback;
- a de-identified research copy with detected secrets and identifiers removed.

The application does not request names, email addresses, phone numbers, or payment details. Users must not submit credentials, confidential records, or data they are not authorized to share.

## Research purposes

The broad research scope includes AI safety, jailbreak and defense research, evaluation, benchmarking, model routing, internal model development and training, abuse prevention, reliability, and product improvement. Raw conversations are not exposed through the research-export API. The research export contains only the de-identified copy.

## User controls

The web UI provides:

- data export for the current browser session;
- research-consent withdrawal, which purges stored conversation and research rows and switches the session to Private mode;
- complete deletion of the current session's stored data.

## Retention

The default configured research retention is 365 days. A production deployment must run a retention job and document backups, deletion propagation, subprocessors, cross-border transfer, and incident response.

## Security baseline

- use HTTPS;
- use independent high-entropy application, encryption, admin, gateway and fingerprint secrets;
- keep the SQLite volume private or replace it with a managed database;
- rotate provider credentials;
- place admin endpoints behind network controls in addition to the bearer token;
- do not use development defaults in a public deployment.
