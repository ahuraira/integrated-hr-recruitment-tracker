# 05: Deployment and Maintenance Guide

## 1. Introduction

This document is the technical guide for IT administrators and future developers responsible for deploying, managing, and maintaining the Manpower Requisition (MPR) Automation Suite. It assumes the reader has administrative access to the Microsoft Power Platform and SharePoint Online environments.

Following these procedures is critical for ensuring system stability, security, and adherence to proper Application Lifecycle Management (ALM) practices.

## 2. Deployment Protocol

Deploying this solution involves more than just importing flows; it requires setting up the data backend and configuring connections correctly. This protocol should be followed for any new environment (e.g., deploying from a Development environment to Production).

### 2.1. Prerequisites

Before starting the deployment, ensure the following components are in place in the target environment:

1.  **SharePoint Site:** A dedicated SharePoint site must exist.
    -   **Site Name:** `Integrated HR Recruitment Tracker`
2.  **SharePoint Lists:** All required lists must be manually created with the exact column names and data types as defined in the [Solution Architecture document](./02-Solution-Architecture.md). This is a critical step, as the flows rely on the internal names of these columns.
    -   `MPR Tracker`
    -   `Candidate Tracker`
    -   `Interview Tracker`
    -   `Interview Feedback Tracker`
    -   `Configuration` (This list will store approver and team data)
3.  **Service Account:** A dedicated, non-personal service account (e.g., `svc-powerautomate@tte.ae`) must be created in Microsoft 365.
    -   This account must have the necessary Power Automate licenses.
    -   It must be granted "Contribute" or "Edit" permissions on the SharePoint site.
    -   All Power Platform connections in the target environment must be created using this account.

### 2.2. Step-by-Step Deployment Process

The entire solution is packaged within a single Power Platform Solution for portability.

1.  **Export the Solution:**
    -   In the source environment, navigate to **Solutions** and select the MPR Automation Suite solution.
    -   Click **Export**.
    -   Select **Managed** as the package type. This is crucial as it prevents direct, unmanaged customizations in the production environment, enforcing a proper ALM process.
    -   Download the exported `.zip` file.

2.  **Import the Solution:**
    -   In the target environment, navigate to **Solutions** and click **Import**.
    -   Select the `.zip` file downloaded in the previous step.

3.  **Configure Connection References:**
    -   During the import wizard, you will be prompted to configure the **Connection References**. This is the most important post-import step.
    -   For each reference listed (e.g., `shared_sharepointonline`, `shared_teams`), you must map it to the corresponding connection that has been pre-configured with the **Service Account**.
    -   Do **not** use personal user connections.

4.  **Populate the Configuration List:**
    -   The `Configuration` SharePoint list in the new environment will be empty.
    -   Manually populate this list with the correct production data (e.g., the names and email addresses of the actual VPs, EVPs, HR Manager, and HR Team members). The flows dynamically query this list, so this data must be accurate.

5.  **Turn On the Flows:**
    -   By default, all flows within an imported solution are turned off.
    -   Navigate to the solution details, and manually **Turn On** each of the six Power Automate flows. It is best to turn them on in their logical order of execution, starting with `MPR-01`.

## 3. Maintenance and Operations

### 3.1. Routine Maintenance

These are common administrative tasks that do not require editing the flows.

#### Updating Approvers or HR Team Members
-   **Scenario:** A VP changes, or a new recruiter joins the HR team.
-   **Procedure:**
    1.  Navigate to the `Configuration` SharePoint list.
    2.  **Do not edit the flows.**
    3.  Update the relevant item in the list. For example, edit the "TTE VP" item and update the person in the `Account` field.
    -   The flows will automatically pick up this change on their next run. This is a core benefit of the centralized configuration design.

#### Modifying Choice Field Options
-   **Scenario:** The HR team wants to add a new option to the `"Next Action (Trigger)"` dropdown in the `Candidate Tracker`.
-   **Procedure:** This is a code-level change and must follow the full deployment lifecycle (Dev -> Test -> Prod).
    1.  **In the Development environment:**
        a.  Update the column choices in the `Candidate Tracker` SharePoint list.
        b.  Modify the `MPR-03-CandidateLifecycleManagement` flow to add a new `Case` to the `Switch` action that handles the new choice.
    2.  Test the changes thoroughly in Development.
    3.  Export the solution and deploy it to Production using the protocol above.

### 3.2. Monitoring and Troubleshooting

#### Monitoring Flow Run History
-   The primary tool for monitoring is the Power Automate portal.
-   Navigate to **My flows** > **Cloud flows**. From here, you can see the 28-day run history for each flow.
-   A **"Succeeded"** status indicates the flow completed without error.
-   A **"Failed"** status requires immediate investigation.

#### Troubleshooting a Failed Flow
1.  **Identify the Failure:** In the flow's run history, click on the timestamp of the failed run.
2.  **Locate the Error:** The flow editor will open, displaying a red exclamation mark `(!)` on the specific action that failed.
3.  **Examine Inputs and Outputs:** Click on the failed action. Review the `INPUTS` and `OUTPUTS` sections. The `body` or `error` message in the output will almost always contain the specific reason for the failure (e.g., "Item not found," "Invalid user," "The expression is invalid.").
4.  **Formulate a Plan:** Based on the error, determine the cause.
    -   **Bad Data:** An incorrect email, a missing ID, etc. The data may need to be corrected in the SharePoint list.
    -   **Permissions Issue:** The service account may have lost access to a required resource.
    -   **Logic Error:** The flow's internal logic or an expression may be flawed. This requires a code-level fix and redeployment.
5.  **Resubmit (Use with Caution):** For failures caused by transient issues (e.g., a temporary service outage), you can use the **Resubmit** button on the failed run page. Do not resubmit if the root cause was bad data that has not yet been corrected.

### 3.3. Backup and Recovery

-   **Flow Definitions:** The primary backup of the flow logic is this **GitHub repository**. The JSON files in the `/flows` directory represent a point-in-time snapshot of the solution. If a flow is accidentally deleted or corrupted, it can be recreated by importing the corresponding JSON file.
-   **Data:** All transactional data resides in SharePoint Online. SharePoint has its own native backup and recovery features, including version history for list items and a multi-stage Recycle Bin.
-   **Solution Backup:** Regular (e.g., quarterly) manual exports of the entire managed solution from the Production environment should be taken and stored in a secure location as an additional disaster recovery measure.

---
_This guide provides the foundation for managing the MPR Automation Suite. Always follow proper change management procedures when modifying the production environment._