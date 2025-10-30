# Changelog

All notable changes to the "MPR Automation Suite" will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [2.0.0] - 2025-09-12

This major version marks the evolution of the MPR system into a comprehensive Talent Intelligence Engine, introducing AI-powered processing, a full candidate lifecycle management suite, and robust system governance.

### Added

-   **AI-Powered CV Ingestion (`MPR-08`, Azure Function):**
    -   Introduced a new, hybrid architecture using a Python-based Azure Function to automate the processing of CVs.
    -   The AI engine automatically extracts 20+ data points from PDF and DOCX files, including candidate details, experience, skills, and an AI-generated confidence score.
-   **Hiring Manager Review Module (`MPR-SYS-SendHMReviewDigest`, `MPR-09`):**
    -   Implemented a best-in-class user experience for Hiring Managers to review candidates.
    -   A scheduled flow now sends a consolidated "digest" of pending candidates via an interactive Adaptive Card in Microsoft Teams.
    -   Managers can now Shortlist or Reject candidates (providing a reason) directly within Teams, with decisions processed by a dedicated webhook flow.
-   **Comprehensive Candidate Lifecycle Management (`MPR-03`):**
    -   The flow now manages the full candidate journey post-shortlisting, including a user-driven "Next Action" control for HR.
    -   Automated the creation of calendar invitations for interview panels and candidates.
-   **Decoupled Feedback Collection Loop (`MPR-04`, `MPR-05`):**
    -   Implemented a robust, two-flow system for managing interview feedback.
    -   A scheduled flow (`MPR-04`) proactively sends feedback requests after an interview is complete.
    -   A listener flow (`MPR-05`) captures form submissions and intelligently checks when all feedback for an event is complete before notifying HR.
-   **Final Decision Finalization (`MPR-06`):**
    -   Added a new flow that allows an HR Rep to designate a piece of feedback as "final," which automatically updates the candidate's status to the next stage (e.g., "HR Selection" or "Rejected").
-   **System Governance - KPI Aggregation (`MPR-SYS-UpdateMPRAggregates`):**
    -   Created a dedicated analytics engine that runs on every candidate change.
    -   It automatically recalculates and updates the parent `MPR Tracker` with real-time pipeline counts (`PositionsFilled`, etc.) and average time-based KPIs (`AvgTimeToFill`, `AvgInterviewProcessTime`, etc.).
-   **System Governance - Proactive SLA Monitoring (`MPR-SYS-MonitorSLAs`):**
    -   Built a comprehensive, scheduled "guardian" flow that monitors all key stages of the process.
    -   It uses a modular, parallel branch architecture to track SLAs for MPR Approval, Sourcing, Shortlisting, Interview Scheduling, and Feedback Collection.
    -   Implements a three-tiered notification system (Warning, Due Today, Breach/Escalation) based on business day calculations.
-   **Enhanced Security Model:** Implemented a robust "Break Inheritance and Grant Access" pattern on all new MPR and Candidate records to enforce a strict, need-to-know item-level security model.
-   **Workspace Provisioning:** The `MPR-02a` flow now automatically creates a standardized folder structure in a SharePoint document library for each new requisition, providing a clean workspace for HR.

### Changed

-   **Architectural Shift:** The solution has evolved from a pure low-code Power Platform system to a sophisticated **hybrid architecture** that integrates a pro-code Azure Function for specialized processing.
-   **HR Assignment (`MPR-02a`):** The assignment process was changed from a flexible, interactive model to a high-speed, **rule-based, hard-coded model** to prioritize automation consistency and speed.
-   **Data Model:** Significantly expanded the SharePoint data model, adding new lists (`Interview Schedule`, `Interview Feedback`, `AI Log`) and numerous `SLAStatus` and `SLATargetDate` columns to support the new governance and tracking features.

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