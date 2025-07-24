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
