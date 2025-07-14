# System Architecture: Phase 1 - Manpower Requisition (MPR)

## 1. Purpose

This document provides a comprehensive overview of the technical architecture for the Manpower Requisition (MPR) automation system. It details the end-to-end business process flow, the interaction between different Microsoft 365 services, the underlying data model, and the security and permissions structure.

---

## 2. Business Process Flow

The system automates the MPR process from initial submission to final approval for the hiring requisition itself. The workflow now includes a dedicated HR assignment process after management approval.

### Process Diagram

```mermaid
graph TD
    subgraph "MPR-01: Initiation & Approval"
        A[Dept. Head Submits MPR Form] --> B[Create Item in SharePoint: Status 'MPR Form Submitted'];
        B --> C[Get VP from System Config];
        C --> D[VP Approval];
        D -->|Rejected| R[Update Status: Rejected & Notify]
        D -->|Approved| E[Check Grade]
        E -->|Grade > 15| F[Get EVP from System Config]
        F --> G[EVP Approval]
        G -->|Rejected| R
        G -->|Approved| H[Update Status: Pending HR Assignment]
        E -->|Grade ≤ 15| I[Update Status: MPR Approved]
    end
    subgraph "MPR-02: HR Assignment"
        H --> J[Get HR Manager & HR Team from System Config]
        J --> K[Post Interactive Card to HR Manager]
        K --> L[Manager Selects HR Rep]
        L --> M[Update 'Assigned HR Rep' & Status: CV Sourcing]
        M --> N[Send Notifications]
        N --> Z[End Process]
    end
```

### Narrative Workflow

1.  A **Department Head** fills out the **Microsoft Form** with all requisition details and attaches the required MPR form document.
2.  **Power Automate** triggers, ingesting the form data and the attached document.
3.  A **new item is created** in the `MPR Tracker` SharePoint list. The system generates a unique, sequential **Requisition ID** and sets the overall `Status` to **`MPR Form Submitted`**.
4.  The flow looks up the responsible **VP** in the `System Configuration` list based on the Business Unit selected (e.g., TTE FM VP, TTE EC VP).
5.  An approval request is sent to the VP to approve the initial requisition.
6.  **If the VP rejects**, the overall `Status` is updated to "Rejected," notifications are sent, and the process ends.
7.  **If the VP approves**, the flow updates the `VP Approval Status` field to "Approved" and logs the date. It then checks the **Grade** of the position.
8.  **If Grade is 15 or less**, the overall `Status` is updated to **`MPR Approved`**, signifying that HR can begin sourcing. The process for this phase ends.
9.  **If Grade is greater than 15**, the flow looks up the **EVP** (TTE EVP) and initiates a final approval request for the requisition.
10. If the EVP approves, the `EVP Approval Status` is marked "Approved" and the overall `Status` is set to `Pending HR Assignment`. If rejected, the overall `Status` becomes "Rejected".
11. The status change to `Pending HR Assignment` triggers a second, dedicated flow (`MPR-02`).
12. This flow sends an interactive card to the HR Manager (from System Config), allowing them to select an HR representative from a dynamic choice set (HR Team).
13. The selected HR rep is updated in the `Assigned HR Rep` field, and the status is set to `CV Sourcing`.
14. Notifications are sent to all relevant parties, and the process ends.

---

## 3. Component & Data Flow Diagram

This diagram illustrates how the different Microsoft 365 services communicate with each other to execute the process.

```mermaid
sequenceDiagram
    participant User as Dept. Head
    participant MSForm as Microsoft Form
    participant PA as Power Automate
    participant SP as SharePoint
    participant VP as VP Approver
    participant EVP as EVP Approver
    participant HR_Manager as HR Manager
    participant HR_Team as HR Team

    User->>+MSForm: Submits MPR data & form document
    MSForm->>+PA: Triggers flow with form data
    PA->>PA: Parses attachment details
    PA->>PA: Generates sequential ID
    PA->>+SP: Creates new item in 'MPR Tracker'
    SP-->>-PA: Returns new Item ID
    PA->>+SP: Adds document as attachment to item
    SP-->>-PA: Confirms attachment
    PA->>+SP: Gets VP/EVP from 'System Config'
    SP-->>-PA: Returns Approver Account
    PA->>+VP: Sends VP Approval Request
    VP-->>-PA: Approves/Rejects
    PA->>+EVP: Sends EVP Approval Request (if required)
    EVP-->>-PA: Approves/Rejects
    PA->>+SP: Updates status in 'MPR Tracker'
    SP-->>-PA: Confirms update
    PA->>+HR_Manager: Posts Interactive Card (HR Team Choice)
    HR_Manager-->>-PA: Selects HR Rep
    PA->>+SP: Updates Assigned HR Rep & Status
    PA->>User: Sends final status notification (Teams & Email)
```

---

## 4. Data Model

The system relies on two core SharePoint Online lists to store and manage all data.

### `MPR Tracker` List

| Column Name | Data Type | Purpose & Notes |
| :--- | :--- | :--- |
| **Title** | Single line of text | *Default column.* Populated with the **Job Title**. |
| **Requisition ID** | Single line of text | The unique, user-friendly ID. Format: `MPR-[BU]-[###]`. |
| **Status** | Choice | **The overall progress of the MPR.** Now includes `Pending HR Assignment` and `Ready for Sourcing` to support the new assignment flow. |
| ... | *(all other fields from the form)* | Captures the core details of the request. |
| **Requester** | Person or Group | The user who submitted the form. Captured automatically. |
| **VP Approval Status** | Choice | `Pending`, `Approved`, `Rejected`. **Tracks the approval decision for the initial requisition request.** |
| **EVP Approval Status** | Choice | `Not Required`, `Pending`, `Approved`, `Rejected`. **Tracks the EVP's decision for the initial requisition.** |
| **VP Approval Date** | Date and Time | Timestamp of the VP's decision. |
| **EVP Approval Date**| Date and Time | Timestamp of the EVP's decision. |
| **Assigned HR Rep** | Person or Group | The HR representative assigned via the interactive card in MPR-02. |
| **Requisition Sequence Number**| Number | An integer used internally by the flow to generate the next sequential ID for a business unit. |
| **Last Update** | Date and Time | Automatically updated by the flow whenever a change is made. |
| **FlowVersion** | Number | A technical field used to prevent infinite loops in the Power Automate flow. |

### `System Configuration` List

This list abstracts logic from the flow, making it easy to maintain without technical intervention.

| Title | Account | Purpose & Notes |
| :--- | :--- | :--- |
| TTE EVP | Person or Group | EVP Approver for high-grade requisitions |
| TTE FM VP | Person or Group | VP Approver for FM business unit |
| TTE EC VP | Person or Group | VP Approver for EC business unit |
| HR Team | Person or Group (single value per row) | Each HR Team member is represented by a separate row with Title = "HR Team" and Account = Person or Group. Add or remove rows to manage team membership. |
| HR Manager | Person or Group | HR Manager responsible for assignment selection |

---

## 5. Permissions Model

Access to system components is strictly defined by role to ensure data integrity and confidentiality.

| Role | Access Level | Responsibilities & Rationale |
| :--- | :--- | :--- |
| **Department Heads** | **Form Submitter Only** | Can submit new MPRs via the Microsoft Form link. **Rationale:** They have no direct access to the SharePoint list to ensure data privacy between departments. |
| **HR Team** | **Site Owner / Admin** | Can view and edit all data, manage list structures, and administer the Power Automate flow. **Rationale:** Responsible for the end-to-end management and maintenance of the system. |
| **VPs / EVPs** | **Approver & Reader** | Interact with the system via Approval notifications in Teams/Outlook. Granted "Read" access to the `MPR Tracker` list for oversight. **Rationale:** Allows them to monitor the pipeline without being able to edit data directly, ensuring process integrity. |
