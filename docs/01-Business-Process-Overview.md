# 01: Business Process Overview

## 1. Introduction

This document provides a comprehensive, non-technical overview of the automated Manpower Requisition (MPR) process at Al Gurg. Its purpose is to explain the end-to-end workflow, define the roles of the individuals involved, and detail the key business rules that govern the system's logic.

The primary objective of this automation suite is to transform our recruitment process from a series of manual, disconnected tasks into a single, transparent, and efficient system. By doing so, we ensure accountability, enforce governance, and accelerate the time it takes to bring new talent into the organization.

## 2. Roles & Responsibilities

The following roles are key actors within this automated process:

| Role                      | Responsibility                                                                        |
| :------------------------ | :------------------------------------------------------------------------------------ |
| **Requester**             | Typically a Hiring Manager or Department Head who initiates the request for a new position. |
| **VP / EVP**              | Senior leaders responsible for providing budgetary and strategic approval for new hires. |
| **HR Manager**            | Oversees the HR recruitment function and is responsible for assigning requisitions to recruiters. |
| **HR Representative**     | The recruiter responsible for the operational tasks of sourcing, shortlisting, and managing candidates. |
| **Interview Panel**       | A group of individuals selected to interview a candidate and provide formal feedback.  |
| **System Administrator**  | The technical owner responsible for maintaining and enhancing the automation suite.       |

## 3. End-to-End Process Narrative

The recruitment journey is broken down into four distinct phases, each managed by the automation suite to ensure a seamless transition from one stage to the next.

### Phase 1: Requisition Initiation and Approval

This phase begins the moment a need for a new hire is identified and ends with full management approval.

1.  **Request Initiation:** A **Requester** initiates the process by filling out the official "Manpower Requisition Form." This standardized form captures all necessary details, such as Job Title, Grade, Business Unit, and Justification.
2.  **System Logging:** Upon submission, the system automatically logs the request in the central "MPR Tracker" on SharePoint. It generates a unique, human-readable **Requisition ID** (e.g., `MPR-TTE-001`) for tracking purposes. The initial status is set to "MPR Form Submitted."
3.  **VP Approval:** The system immediately triggers an approval request to the designated **Vice President (VP)** for that Business Unit. The VP receives a notification in both Microsoft Teams and their email, allowing them to approve or reject the request with comments.
4.  **Conditional EVP Approval:** The system automatically checks the "Grade" of the requested position. If the Grade is 16 or higher, a second, sequential approval is automatically routed to the **Executive Vice President (EVP)** after the VP has approved it. This enforces our corporate hiring governance without any manual intervention.
5.  **Finalization:** Once all required approvals are secured, the system updates the requisition's status to **"MPR Approved"** and sends an automated notification to the original **Requester**, informing them that they can proceed.

### Phase 2: HR Assignment and Sourcing

With the requisition approved, this phase ensures it is promptly assigned to a recruiter to begin work.

1.  **HR Manager Notification:** The status change to "MPR Approved" automatically triggers an action. The **HR Manager** receives an interactive card directly in Microsoft Teams, alerting them to the new, unassigned requisition.
2.  **Recruiter Assignment:** The interactive card allows the HR Manager to select an **HR Representative** from a dropdown list and click "Assign."
3.  **Assignment & Notification:** The system assigns the selected HR Representative to the requisition in the MPR Tracker and updates its status to **"CV Sourcing."** Simultaneously, an automated email and a Teams message are sent to the assigned HR Rep, providing them with all the details of the requisition and officially kicking off their search.

### Phase 3: Candidate Lifecycle and Interview Management

This phase covers the operational work of managing candidates and scheduling interviews.

1.  **Candidate Entry:** As the **HR Representative** sources candidates, they add potential fits to the "Candidates List" in SharePoint, linking them to the parent Requisition ID.
2.  **Candidate ID Generation:** The moment a new candidate is added, the system automatically generates a unique **Candidate ID** (e.g., `MPR-TTE-001-C01`), ensuring every candidate can be tracked individually. The candidate's status is set to "Shortlisted."
3.  **Interview Scheduling:** When the HR Representative is ready to schedule an interview, they update the candidate's record with the interview details: the interview title, date/time, and the members of the **Interview Panel**.
4.  **Automated Calendar Invites:** The system detects this update and automatically creates and sends calendar invitations to all members of the Interview Panel and the assigned HR Representative, booking the time in their calendars.
5.  **Interview Logging:** A record of the scheduled interview is created in the "Interview Tracker," linking the candidate, the panel, and the date. This log acts as a historical record of all interview activities.

### Phase 4: Feedback Collection and Final Decision

This final phase ensures that timely, standardized feedback is collected to enable an informed hiring decision.

1.  **Automated Feedback Requests:** On the day of a scheduled interview, the system automatically sends a personalized email to each member of the **Interview Panel**. This email contains a unique link to a standardized "Interview Feedback Form."
2.  **Feedback Submission:** Interviewers use the form to provide their detailed assessment, a recommendation (e.g., "Recommend to Proceed"), and any relevant attachments.
3.  **Feedback Consolidation:** As feedback is submitted, the system captures the responses and attaches them to the "Interview Feedback Tracker."
4.  **Status Updates & Notification:** Once all panel members have submitted their feedback for an interview, the system updates the candidate's status to **"Interview Evaluation Received"** and notifies the **HR Representative** that the feedback is ready for review.
5.  **Final Decision:** The HR Representative and Requester can review the consolidated feedback to make a final decision, such as moving forward with an offer or rejecting the candidate. The system then tracks subsequent steps like "Offer Approval" and "Hired."

## 4. Critical Business Rules

The logic of the automation is governed by a set of predefined business rules that ensure consistency and compliance.

-   **Unique ID Generation:**
    -   **Requisition ID:** Composed of the prefix `MPR`, the Business Unit code (e.g., `FM`), and a 3-digit sequential number (e.g., `001`). This sequence resets per Business Unit.
    -   **Candidate ID:** Appends a candidate-specific suffix (`-C` followed by a 2-digit number) to the parent Requisition ID.
-   **Hierarchical Approvals:**
    -   All requisitions require approval from the respective Business Unit's VP.
    -   Requisitions for positions at **Grade 16 or higher** require an additional, mandatory approval from the EVP.
-   **Status-Driven Automation:**
    -   The entire process is driven by status changes in the SharePoint lists. A flow is only triggered when an item reaches a specific status (e.g., `MPR Approved` triggers the HR assignment). This modular approach makes the system robust and predictable.
-   **Centralized Configuration:**
    -   Key personnel (like VPs, the EVP, and the HR Team) are not hard-coded into the flows. They are maintained in a central "Configuration List" in SharePoint. This allows for easy updates (e.g., if a VP changes) without needing to modify the automation logic itself.

---
_This document outlines the business flow. For details on the underlying technology and data structure, please proceed to the [02-Solution-Architecture.md](./02-Solution-Architecture.md)._