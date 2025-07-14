# Changelog

All notable changes to the "Recruitment Digitization & Automation Program" will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to Semantic Versioning.

---

## [v1.1.0] - 2025-07-14

### Added

-   **New Flow (`MPR-02HRAssignment`):** Created a dedicated, decoupled flow to manage the assignment of an HR Representative to an approved MPR.
-   **Interactive Teams Assignment:** Implemented an Adaptive Card with a dynamic choice-set sent to the HR Manager, allowing for seamless assignment directly within Microsoft Teams.
-   **New Statuses:** Added `Pending HR Assignment` and `CV Sourcing` to the `Status` lifecycle to facilitate the new process.
-   **Expanded System Configuration:** System Configuration list now manages individual HR Team members (one per row) and the HR Manager for assignment selection.
-   **Updated Documentation:** System Architecture and Detailed Flow Logic updated to reflect new assignment flow, configuration, and process changes.

### Changed
-   **Updated System Architecture:** All documentation has been updated to reflect the new two-flow, event-driven architecture and configuration management.

## [v1.0.0] - 2024-07-03

This is the initial, stable release of the Manpower Requisition (MPR) automation system, marking the completion of Phase 1.

### Added

-   **Initial Process Automation:** Created the end-to-end Power Automate flow (`MPR - 01 - Initiation and Approval`) to manage the process from submission to final approval.
-   **Dynamic Sequential ID Generation:** Implemented logic to create user-friendly, unique IDs for each requisition (e.g., `MPR-EC-024`).
-   **Dynamic Approver Logic:** The system now automatically routes approvals to the correct VP and EVP based on Business Unit and Grade rules stored in a SharePoint configuration list.
-   **Attachment Handling:** The flow now correctly processes the filled MPR form uploaded by the requester and includes it in the approval requests.
-   **Core Data Structure:** Established the `MPR Tracker` and `System Configuration` SharePoint lists as the central database.
-   **Initial Documentation Framework:** Created the foundational documentation set in this GitHub repository, including System Architecture, Deployment Guide, and Detailed Flow Logic.