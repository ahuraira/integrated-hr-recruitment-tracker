# Changelog

All notable changes to the "MPR Automation Suite" will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [1.0.0] - 2023-10-27

### Added
-   **Initial Release:** The first official production release of the end-to-end MPR Automation Suite.
-   **Flow: MPR-01-InitiationandApproval:** Automates the initial request from MS Forms, including dynamic VP/EVP approval loops.
-   **Flow: MPR-02-HRAssignment:** Automates the assignment of approved MPRs to HR Representatives via an interactive Teams card for the HR Manager.
-   **Flow: MPR-03-CandidateLifecycleManagement:** Manages the creation of unique Candidate IDs and orchestrates user-driven actions like scheduling interviews.
-   **Flow: MPR-04-TriggerPostInterviewActions:** A scheduled flow that proactively sends feedback requests to interviewers.
-   **Flow: MPR-05-CaptureInterviewFeedback:** Captures feedback from the MS Form and logs it against the correct interview event.
-   **Flow: MPR-06-TransferInterviewFeedbackBackToInterviewTra:** Provides a mechanism for HR to finalize feedback and move the candidate to the next stage.
-   **Full Documentation Suite:**
    -   `README.md`: High-level project overview.
    -   `01-Business-Process-Overview.md`: Detailed narrative of the business workflow.
    -   `02-Solution-Architecture.md`: Technical architecture, data models, and key management strategy.
    -   `03-Technical-Flow-Breakdown.md`: Deep-dive analysis of each Power Automate flow.
    -   `04-User-Guides.md`: Step-by-step guides for all user roles.
    -   `05-Deployment-and-Maintenance.md`: Protocols for deployment, configuration, and troubleshooting.