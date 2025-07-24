# Documentation Strategy and Contribution Guidelines

## 1. Guiding Principle: Documentation as Code

The documentation for the "MPR Automation Suite" is considered an integral part of the solution, with the same importance as the Power Automate flows themselves. We adhere to a **"Documentation as Code"** philosophy, which means:

-   **Version Controlled:** All documentation resides in this GitHub repository and is version-controlled alongside the application code (the flow JSON definitions).
-   **Centralized Source of Truth:** This repository is the single, definitive source of truth. Any documentation found outside of this repository should be considered stale or unofficial.
-   **Part of the Development Lifecycle:** A feature or bug fix is not considered "done" until the code is complete AND all relevant documentation has been updated to reflect the change.

The purpose of this approach is to ensure our documentation remains a living, accurate, and valuable asset for all stakeholders, from end-users to future developers.

## 2. Audience-Centric Documentation

Our documentation is structured to serve multiple audiences. Each document in the `/docs` folder is written with a specific reader in mind. When making updates, it is crucial to maintain the appropriate tone and level of detail for that document's intended audience.

| Document Suffix                  | Primary Audience                  | Focus                                   |
| :------------------------------- | :-------------------------------- | :-------------------------------------- |
| `01-Business-Process-Overview.md`  | Business Stakeholders, Management | The "Why" and "What" – Process Narrative    |
| `02-Solution-Architecture.md`    | Architects, Technical Leads       | The "How" – Blueprints & Structure      |
| `03-Technical-Flow-Breakdown.md` | Developers, Technical Support     | The "Deep How" – Code-Level Logic       |
| `04-User-Guides.md`              | End-Users (HR, Managers)          | Step-by-Step Instructions               |
| `05-Deployment-and-Maintenance.md`| IT Administrators                 | Operations & Management                 |

## 3. Contribution Workflow: The Definition of Done

All changes to this project, whether to a flow or to the documentation, **must** be managed through a GitHub Pull Request (PR). This ensures peer review and adherence to our quality standards.

The core of our strategy is the **Pull Request Documentation Checklist**. A PR cannot be approved and merged until the author has reviewed the impact of their changes against all documentation and updated it accordingly.

### The Pull Request Process

1.  **Create a Branch:** Create a new branch from `main` for your changes. Use a descriptive name, for example:
    -   `feature/add-offer-letter-generation`
    -   `bugfix/fix-sequence-number-calculation`
    -   `docs/update-user-guide-screenshots`

2.  **Make Your Changes:**
    -   If modifying a flow, make the changes in the development environment. Once complete, export the updated flow's JSON definition and commit it to the `/flows` directory in your branch.
    -   Commit your changes with clear, descriptive messages.

3.  **Update All Relevant Documentation:** Before submitting your PR, go through the checklist below and update every document impacted by your change. Commit these documentation changes to your branch.

4.  **Open a Pull Request:** Create a new PR to merge your branch into `main`. The PR description will be pre-populated with the checklist from our template. Go through it and mark the checkboxes to confirm you have completed the required reviews.

5.  **Peer Review:** Another team member must review the PR, checking both the code/flow changes and the corresponding documentation updates for accuracy and clarity.

6.  **Merge:** Once approved, the PR can be merged into `main`. The `main` branch should always represent the stable, deployable state of the solution.

### Pull Request Documentation Checklist Template

> The following checklist must be completed for every Pull Request.
>
> **1. Code & Versioning**
> -   [ ] The updated flow JSON has been exported and committed to the `/flows` directory.
> -   [ ] The `CHANGELOG.md` has been updated in the `[Unreleased]` section with a clear description of the change.
>
> **2. High-Level Documentation Review**
> -   [ ] **`README.md`**: Does the change affect the high-level process flow diagram or the overall summary? If so, update it.
> -   [ ] **`01-Business-Process-Overview.md`**: Does the change alter the business process narrative, introduce a new step, or modify a business rule? If so, update the text to reflect this.
>
> **3. Architectural Documentation Review**
> -   [ ] **`02-Solution-Architecture.md`**:
>     -   [ ] **Data Model:** Does the change add or modify a SharePoint column? If so, update the List Definitions and the ERD diagram.
>     -   [ ] **Orchestration:** Does the change affect how the flows interact? If so, update the Solution Components/Orchestration diagram and descriptive text.
>
> **4. Technical Documentation Review**
> -   [ ] **`03-Technical-Flow-Breakdown.md`**:
>     -   [ ] **Logic:** Has the core logic of the modified flow changed? Update the "High-Level Logic" section for that flow.
>     -   [ ] **Variables & Expressions:** Were any new variables or key formulas added or changed? Document them.
>
> **5. End-User Documentation Review**
> -   [ ] **`04-User-Guides.md`**:
>     -   [ ] **User Actions:** Does the change affect how a user interacts with the system? Update the relevant user guide section with new instructions and screenshots.
>     -   [ ] **FAQ:** Does this change potentially introduce a new common question? Update the FAQ.
>
> **6. Administrative Documentation Review**
> -   [ ] **`05-Deployment-and-Maintenance.md`**: Does the change affect how the solution is deployed or maintained? If so, update the relevant protocol.

---
_By following this strategy, we ensure that our documentation remains a reliable and invaluable asset for years to come._