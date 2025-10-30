# 01: Business Process Overview

## 1. Introduction

This document provides a comprehensive, non-technical overview of the automated Manpower Requisition (MPR) and Recruitment process. Its purpose is to explain the end-to-end workflow, define the roles of the individuals involved, and detail the key business rules that govern the system's logic.

The objective of this automation suite is to transform our recruitment process from a series of manual, disconnected tasks into a single, transparent, and efficient system. By doing so, we ensure accountability, enforce governance, and accelerate the time it takes to bring new talent into the organization.

## 2. Roles & Responsibilities

The following roles are key actors within this automated process:

| Role | Responsibility |
| :--- | :--- |
| **Requester / Hiring Manager** | The manager who initiates the request for a new position and is the ultimate decision-maker for shortlisting and hiring candidates. |
| **VP / EVP** | Senior leaders responsible for providing budgetary and strategic approval for new hires based on corporate governance rules. |
| **HR Manager** | Oversees the HR recruitment function and is the escalation point for process delays. |
| **HR Representative** | The recruiter assigned to a requisition, responsible for the operational tasks of sourcing, managing candidates, and scheduling interviews. |
| **Interview Panel** | A group of individuals selected to interview a candidate and provide formal, structured feedback. |
| **System Administrator** | The technical owner responsible for maintaining and enhancing the automation suite. |

## 3. End-to-End Process Narrative

The recruitment journey is now a fully orchestrated, five-phase process, managed by the automation suite to ensure a seamless and transparent flow of information.

### Phase 1: Requisition Initiation and Approval

This phase begins when a need for a new hire is identified and ends with full management approval.

1.  **Request Initiation:** A **Requester** starts the process by filling out the official "Manpower Requisition Form."
2.  **System Logging & Security:** Upon submission, the system automatically logs the request in the central "MPR Tracker" and generates a unique **Requisition ID** (e.g., `MPR-EC-024`). Simultaneously, it applies **item-level security**, ensuring that this request is only visible to the Requester and the required chain of command.
3.  **SLA Clock Starts:** The system immediately calculates and sets a target date for the approval, starting the clock for the Service Level Agreement (SLA).
4.  **VP & Conditional EVP Approval:** The system automatically triggers an approval request to the designated **VP**. If the position's grade meets the corporate governance threshold, a sequential approval is then automatically routed to the **EVP**.
5.  **Finalization:** Once approved, the system updates the status to **"MPR Approved"** and notifies the original Requester.

### Phase 2: Automated Assignment and Workspace Provisioning

This phase ensures that every approved requisition is immediately and correctly actioned.

1.  **Automated Assignment:** The status change to "MPR Approved" instantly triggers the next stage. The system, based on predefined business rules, **automatically assigns the requisition to the correct HR Representative** based on the Business Unit.
2.  **Workspace Creation:** Simultaneously, the system provisions a dedicated, secure workspace for the new requisition within the "CV Intake" document library. This includes creating a main folder and all necessary subfolders (e.g., "1. New CVs (Drop Files Here)").
3.  **Official Kickoff:** The newly assigned **HR Representative** receives a notification with all the requisition details and a direct link to their new workspace, officially kicking off the sourcing process. The SLA clock for sourcing begins.

### Phase 3: AI-Powered CV Ingestion and Screening

This is the intelligent core of the system, designed to dramatically reduce manual work.

1.  **CV Upload:** The **HR Representative**'s only manual task is to drag and drop sourced CVs (PDFs or DOCX) into the "1. New CVs (Drop Files Here)" folder.
2.  **AI-Powered Data Extraction:** The system instantly detects each new file and triggers the AI engine. This engine performs a sophisticated, two-stage analysis:
    *   **Stage 1 (Privacy):** It identifies and separates sensitive Personal Information (PII) to create an anonymized version of the CV.
    *   **Stage 2 (Analysis):** It analyzes the anonymized text to extract over 20 key data points, including work history, skills, years of experience, and a calculated **AI Confidence Score** on the candidate's fit for the role.
3.  **Automated Profile Creation:** The system uses this extracted data to automatically create a new, standardized profile in the "Candidate Tracker." Each record is stamped with the next sequential **Candidate ID**, the initial status of **"Sourced,"** and a calculated **Target Shortlisting Date** derived from the SLA configuration. The original CV file is moved to the "Under HM Review" folder to prevent reprocessing, and the AI run is logged for auditability (including prompts, models, and token usage).

### Phase 4: Interactive Hiring Manager Review

This phase provides a best-in-class, consolidated review experience for Hiring Managers.

1.  **Automated Digest:** On a daily schedule, the system checks for any candidates in the "Pending HM Review" state. It then groups these candidates by **Hiring Manager**.
2.  **Interactive Teams Card:** Each Hiring Manager with pending reviews receives a **single, consolidated "digest" card** in Microsoft Teams. This card lists all their pending candidates, showing key AI-generated insights (Confidence Score, Experience, etc.) for each one.
3.  **In-Teams Decision Making:** The manager can review the insights, click a link to view the full CV, and make a decision **directly on the card** by clicking "✔️ Shortlist" or "❌ Reject" for each candidate. If rejecting, they are prompted to provide a reason.
4.  **System Action:** The system instantly captures the manager's decision.
    *   **If Shortlisted:** The candidate's status is updated to "Shortlisted for Interview," and the SLA clock for interview scheduling begins.
    *   **If Rejected:** The status is updated to "Rejected," and the reason is logged.

### Phase 5: Interview Lifecycle and Feedback Management

This phase manages the logistics of the interview process.

1.  **Interview Scheduling:** The **HR Representative** drives this stage using the "Next Action" field on the `Candidate Tracker`. They enter the interview details (title, date/time, panel) and select "Schedule Next Interview."
2.  **Automated Calendar & Logging:** The system automatically sends calendar invitations to the panel and creates a log of the event in the "Interview Schedule" tracker, setting the SLA target date for feedback collection.
3.  **Automated Feedback Requests:** After the interview is complete, a separate, scheduled process automatically sends a personalized email to each panelist with a unique link to the "Interview Feedback Form."
4.  **Feedback Capture & Synchronization:** As interviewers submit feedback, the system captures their responses. Once **all** feedback for an interview is received, the system updates the parent interview's status and sends a notification to the **HR Representative**, informing them that the candidate is ready for a final decision.
5.  **Making the Final Decision:** After reviewing the consolidated feedback, the **HR Representative** makes the definitive go/no-go decision. They do this by navigating to the specific feedback entry they deem final (typically from the Hiring Manager or a final-round interviewer) and checking the **"Treat as Final Feedback"** box.
6.  **System Finalization:** This single action triggers the final automation. The system copies the key recommendation and comments to the main candidate record. Based on the feedback, it will automatically update the candidate's `Overall Status` to either **"HR Selection"** (if positive), starting the offer process, or **"Rejected"** (if negative), closing the loop for that candidate.

## 4. Critical Business Rules & Governance

The logic of the automation is governed by a set of predefined business rules that ensure consistency, compliance, and efficiency across the entire process.

*   **Unique ID Generation:** To ensure every item is uniquely trackable, the system generates standardized IDs:
    *   **Requisition ID:** `MPR-[BU Code]-[Sequence Number]` (e.g., `MPR-EC-024`).
    *   **Candidate ID:** `[Parent Requisition ID]-C[Sequence Number]` (e.g., `MPR-EC-024-C01`).

*   **Hierarchical Approvals:** Corporate hiring governance is automatically enforced:
    *   All requisitions require approval from the respective Business Unit's VP.
    *   Requisitions for positions at **Grade 16 or higher** (configurable) require an additional, mandatory approval from the EVP.

*   **Rule-Based HR Assignment:** To ensure speed and consistency, approved requisitions are **automatically assigned** to a specific, pre-defined HR Representative based on the Business Unit of the request.

*   **Data Security & Confidentiality:** The system is built on a "need-to-know" basis.
    *   **Item-Level Permissions** are automatically applied. A Hiring Manager can only ever see the requisitions and candidates that are relevant to them. They cannot view data from other departments.

*   **Proactive SLA Monitoring:** The system does not just track dates; it enforces timeliness.
    *   Every key stage has a pre-defined Service Level Agreement (SLA) measured in business days.
    *   The system sends automated **warnings** as deadlines approach and **escalations** to management if deadlines are missed.

*   **Centralized Configuration:** Key business parameters—such as the grade threshold for EVP approval, the names of the VPs, and the number of days for each SLA—are not hard-coded. They are stored in a central SharePoint "Configuration List." This allows authorized administrators to update these rules without needing to modify the underlying automation code, making the system highly adaptable to business changes.

## 5. System Governance: The "Guardian" Flows

Running in the background are two critical system flows that ensure the process remains efficient and transparent.

*   **SLA Monitoring Engine:** A "guardian" flow runs daily, checking every active requisition and candidate against their pre-calculated SLA target dates. If a stage is nearing its deadline, it sends proactive **warnings**. If a deadline is missed, it automatically sends **escalations** to the appropriate level of management. This ensures no item can get "stuck" without visibility.
*   **KPI Aggregation Engine:** Another system flow runs whenever a candidate's status changes. It automatically recalculates and updates key performance indicators (KPIs)—like `Positions Filled` and `Average Time to Fill`—on the parent `MPR Tracker`. This transforms the MPR Tracker into a live, analytical dashboard for leadership.

---
_This document outlines the business flow. For details on the underlying technology and data structure, please proceed to the [02-Solution-Architecture.md](./02-Solution-Architecture.md)._