# Recruitment Digitization & Automation Program

## 1. Vision & Purpose

This repository contains the documentation and source artifacts for the end-to-end digitization of the TTE recruitment lifecycle. The program's vision is to establish a single, integrated system that provides real-time visibility, enforces accountability, and leverages automation to reduce time-to-hire and improve decision-making.

This system is being developed in distinct, manageable phases to ensure smooth adoption and continuous value delivery.

---

## 2. Program Roadmap & Status

This roadmap outlines the planned phases of the program. The current status indicates which components are active and which are planned for future development.

| Phase | Description | Key Features | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Manpower Requisition (MPR)** | Automates the process from requisition submission through final management approval and **assignment to an HR representative.** | - Automated Sequential ID Generation<br>- Dynamic VP/EVP Approval Workflow<br>- Attachment Handling<br>- Real-time Notifications<br>- **Interactive HR Assignment Card** | ✅ **Complete & In Production** |
| **Phase 2: Candidate Sourcing & Tracking** | Provides a centralized system to track candidates against an approved MPR, from sourcing through to offer acceptance. | - Candidate Database per Requisition<br>- Stage & Status Tracking (Sourced, Interviewed)<br>- Interview Scheduling & Feedback Capture | 🟡 **In Development / Planned** |
| **Phase 3: Employee Onboarding** | Manages the post-offer acceptance process, including visa processing, IT setup, and Day 1 readiness tasks. | - Onboarding Task Checklists<br>- Automated Notifications to Support Depts<br>- Visa Status Tracking | ⚪ **Future Scope** |

---

## 3. System Architecture Overview

The program is built on the Microsoft 365 ecosystem, leveraging a suite of standard tools to create a powerful, integrated solution without requiring extensive custom development.

-   **Input & User Interface:** Microsoft Forms & Power Apps
-   **Automation Engine:** Power Automate
-   **Central Database:** SharePoint Online Lists
-   **Collaboration & Notifications:** Microsoft Teams & Outlook
-   **Configuration & Roles:** SharePoint System Configuration list manages approvers, HR Manager, and individual HR Team members (one per row).

---

## 4. Documentation & Components

Detailed documentation for each phase is maintained within this repository.

*   **For detailed documentation on the current, active phase, please refer to the links below.**

### Phase 1: Manpower Requisition (MPR)

| Document | Description |
| :--- | :--- |
| **[System Architecture](./docs/1-System-Architecture.md)** | The "Big Picture": Process flows, data models, and permissions for the MPR phase. |
| **[Setup & Deployment Guide](./docs/2-Setup-And-Deployment-Guide.md)** | The "How to Rebuild": Step-by-step instructions to deploy the MPR system from scratch. |
| **[Detailed Flow Logic](./docs/3-Detailed-Flow-Logic.md)** | The "How to Edit": A deep dive into the Power Automate flow, explaining complex logic and patterns. |
| **[MPR-02 Assignment Flow Logic](./docs/3.1-Detailed-Flow-Logic-MPR-02.md)** | The "Assignment Process": Details the dedicated flow for HR assignment and interactive card. |

---

## 5. Owners & Governance

-   **Program Sponsor:** [Name of VP/EVP, e.g., Head of HR]
-   **Technical Lead:** [Your Name / Service Account Name]
-   **Change Log:** For a detailed history of all changes and version updates, please see the **[CHANGELOG.md](./CHANGELOG.md)**.