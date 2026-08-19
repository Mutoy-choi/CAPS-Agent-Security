# CAPS Research Data Terms — draft v1

> This is a product-design draft, not legal advice. It must be reviewed and localized before public deployment.

## 1. Plain-language summary

When a user selects **Research mode**, CAPS stores the user's query and the model response in encrypted form and creates a de-identified research copy. The research copy may be used broadly for AI-safety research and product improvement. A user may instead select **Private mode**, which does not persist conversation content on the CAPS application server.

## 2. User content

The user retains ownership of content they are legally entitled to submit. The user represents that they have authority to provide the content and must not submit credentials, unlawful material, confidential third-party records, or personal data they are not authorized to share.

## 3. Service-processing permission

The user authorizes CAPS to process submitted content to provide the chat service, route requests to the selected model provider, secure and operate the service, detect abuse, generate the response, and create the user's export or deletion record.

## 4. Broad research permission

For conversations created while Research mode is active, the user grants a non-exclusive, worldwide, royalty-free permission to create and use de-identified or aggregated research records for:

- AI safety, alignment, jailbreak, prompt-injection and defense research;
- benchmark, red-team, evaluation and auditing methods;
- quality, reliability, security and abuse-prevention analysis;
- model routing, ranking and recommendation;
- development, training, fine-tuning and evaluation of internal models and classifiers;
- development and improvement of products, features and user experience;
- academic or commercial research and publication of aggregate findings.

The product must not describe this permission as hidden, automatic, irrevocable, or unlimited. The displayed consent version controls the permitted use.

## 5. Raw content and research export

Raw conversation content is stored only in encrypted operational tables. The built-in research-export endpoint excludes raw content and returns only de-identified research records. CAPS does not promise that automated de-identification removes every possible identifier, so high-risk detected content is excluded or replaced with a placeholder.

## 6. Withdrawal and deletion

A user may withdraw Research mode from the current browser session. The MVP purges the session's stored conversations and research rows and switches the session to Private mode. A user may also delete all stored data linked to that session. A production policy must explain backup deletion, legal holds and any already-published aggregate results.

## 7. Retention

The default configured retention is 365 days. The operator must publish the actual retention schedule and implement automated expiration before public deployment.

## 8. Model providers

Queries are sent to the configured third-party model provider. The provider may process data under its own terms and privacy policy. The operator must disclose the active provider or routing service.

## 9. Age and eligibility

The MVP should be limited to adults until age-appropriate consent and child-safety controls are implemented.
