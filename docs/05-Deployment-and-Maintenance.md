# 05: Deployment and Maintenance Guide

## 1. Introduction

This document is the primary technical guide for IT administrators and Power Platform developers responsible for deploying, managing, and maintaining the Manpower Requisition (MPR) Automation Suite. It outlines the protocols for Application Lifecycle Management (ALM), routine maintenance, monitoring, and disaster recovery.

Adherence to these procedures is critical for ensuring system stability, security, and the long-term integrity of the solution.

## 2. Solution Architecture & Dependencies

Before any deployment, it is essential to understand the solution's hybrid architecture. The system consists of two primary, interconnected components:

1.  **The Power Platform Solution:** A **managed solution** containing all Power Automate flows, connection references, and environment variables. This orchestrates the business process.
2.  **The Azure Function App:** A **pro-code Python application** (`ai-processing-azure-functions`) that handles the specialized task of CV parsing and AI analysis.

These two components are deployed and managed separately but are dependent on each other.

---

## 3. First-Time Environment Setup

This protocol is for deploying the entire solution to a new, clean environment (e.g., a formal UAT or Production environment).

### 3.1. Prerequisites

-   **Azure:** An Azure subscription with permissions to create Resource Groups, Storage Accounts, and Azure AI/OpenAI resources.
-   **Power Platform:** A Power Platform environment with a Dataverse database (required for Solutions).
-   **Service Account:** A dedicated, non-personal service account (e.g., `svc-mpr-automation@yourcompany.com`) with:
    -   A Power Automate Premium license (a "Per user" license for the service account is sufficient to own and run the flows).
    -   Permissions to read/write to the target SharePoint site.
    -   An active mailbox.

### 3.2. Azure Deployment (The AI Engine)

1.  **Deploy Azure Resources:** In the target Azure subscription, create a new Resource Group. Within this group, provision:
    *   An **Azure OpenAI Service**.
    *   A **Storage Account**.
    *   An **Application Insights** resource for logging.
    *   A **Function App** (Consumption Plan, Python runtime).
2.  **Configure OpenAI:** In the Azure OpenAI Studio, create the two required Assistants (`CV-PII-Identifier` and `CV-Skills-Analyst`) using the prompts and JSON schemas from the project documentation. Note their Assistant IDs.
3.  **Configure Function App:**
    *   Navigate to the Function App's **Configuration** blade.
    *   Under "Application settings," create and populate all required environment variables as defined in the `ai-processing-azure-functions/README.md` file (e.g., `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `ASSISTANT_ID_...`). This is the secure way to manage secrets.
4.  **Deploy the Code:** Deploy the Python code from the `ai-processing-azure-functions` folder to the newly created Function App using the recommended VS Code extension or a CI/CD pipeline.
5.  **Get the Function URL:** Navigate to the `ProcessCV` function, click **"Get Function Url"**, and copy the full URL, including the `?code=...` key.

### 3.3. Power Platform Deployment (The Orchestrator)

1.  **Create SharePoint Assets:** On the target SharePoint site, manually create all required lists and the `CV Intake` document library. The column names and data types must **exactly match** the specifications in the `02-Solution-Architecture.md` document.
2.  **Configure Connections:** In the target Power Platform environment, create all necessary connections (SharePoint, Office 365, Teams) using the **Service Account**.
3.  **Import the Solution:**
    *   Navigate to **Solutions** and click **Import**.
    *   Upload the latest **managed** solution `.zip` file from the repository's "Releases" section.
    *   **CRITICAL:** During the import wizard, you will be prompted to configure the **Connection References**. For each reference, you must map it to the corresponding connection you pre-configured with the Service Account.
4.  **Configure Environment Variables:**
    *   After the solution is imported, you will be prompted to configure any Environment Variables. The most critical one will be the URL for the Azure Function.
    *   **Update `AzureFunctionUrl`:** Paste the Function URL you copied from the Azure Portal.
5.  **Populate the `Configuration` List:** The SharePoint `Configuration` list will be empty. Manually populate it with the production data for VPs, the HR Manager, and all SLA day counts.
6.  **Turn On the Flows:** By default, all flows are turned off. Manually **Turn On** each flow, starting with the system/listener flows (`MPR-09`, `MPR-05`, etc.) and finishing with the main transactional flows.

---

## 4. Maintenance and Operations

### 4.1. Routine Administrative Tasks (No Code Change)

These are tasks that the designated Business Process Owner (e.g., the HR Manager) can perform.

| Scenario | Procedure | Tool Used |
| :--- | :--- | :--- |
| **An Approver Changes** (e.g., new VP) | Edit the relevant item in the `Configuration` list and update the "Account" field. | SharePoint List |
| **An SLA Needs Adjustment** | Edit the relevant `SLA - ...` item in the `Configuration` list and update the "Value" field. | SharePoint List |
| **A New HR Rep Joins the Team**| If using the (old) interactive assignment, add them to the `Configuration` list. If using the current rule-based assignment, this is a code change (see below).| SharePoint List |

### 4.2. Code-Level Changes (Requires a Full ALM Cycle)

Any change to a Power Automate flow or the Azure Function code is a code-level change and **must** follow the formal "Dev -> Test -> Prod" lifecycle.

**Example Scenario: Change the rule-based HR assignment in `MPR-02a`.**

1.  **Development Environment:**
    *   The developer makes the change in the `MPR-02a` flow within the unmanaged solution in the **Dev environment**.
    *   The developer updates the relevant documentation (`02-Architecture`, `03-Technical-Breakdown`) in a new Git branch.
2.  **Testing:** The change is thoroughly tested in the Dev environment.
3.  **Packaging:** The entire solution is exported from Dev as a **Managed Solution** with an incremented version number.
4.  **Deployment:** The new managed solution is imported into the **Production environment**, which will overwrite the existing solution and deploy the updated version of the flow.
5.  **Source Control:** The documentation and any exported flow definitions are merged into the `main` branch in GitHub.

### 4.3. Monitoring and Troubleshooting

#### Monitoring Flow Run History
-   **Primary Tool:** The Power Automate portal's "Cloud flow activity" page and the run history for each individual flow.
-   **Cadence:** The System Administrator should perform a daily check of the previous day's run history for the critical scheduled flows (`MPR-SYS-MonitorSLAs` and `MPR-SYS-SendHMReviewDigest`) to proactively identify any failures.
-   **Failure Alerts:** The flow owner (the Service Account) will automatically receive an email notification if a flow fails a certain number of times consecutively. These alerts must be actioned immediately.

#### Troubleshooting a Failed Flow
1.  **Identify the Failure:** In the flow's run history, click on the failed run.
2.  **Locate the Error:** The flow designer will show a red exclamation mark `(!)` on the failed action.
3.  **Examine Inputs and Outputs:** Click the failed action. The `error` message in the `OUTPUTS` section will provide the technical reason for the failure (e.g., "Item not found," "404 Not Found" for an HTTP call, "Access Denied").
4.  **Consult the Documentation:** Refer to the `03-Technical-Flow-Breakdown.md` to understand what the failed action was supposed to do.
5.  **Formulate a Plan:**
    *   **Data Issue:** If the error was caused by bad data (e.g., a manager tried to schedule an interview without an end time), the data should be corrected in the SharePoint list, and the flow run can be **Resubmitted**.
    *   **Permissions Issue:** If the error is "Access Denied," verify the Service Account's permissions on the relevant SharePoint site or other resource.
    *   **Transient Issue:** For temporary network or service glitches, using the **Resubmit** button is appropriate.
    *   **Code/Logic Error:** If the flow's logic is flawed, this requires a full ALM cycle to fix in Dev and redeploy.

## 5. Backup and Recovery

-   **Flow & App Definitions:** The **GitHub repository is the primary backup** for the solution's logic and structure. The exported flow JSON files and the Azure Function code represent a definitive point-in-time snapshot.
-   **Data:** All transactional data resides in SharePoint Online. Standard SharePoint data recovery procedures apply (Version History, Recycle Bin). It is recommended to configure a formal backup policy for the SharePoint site if one is not already in place.
-   **Solution Backup:** A best practice is to perform a manual export of the **managed solution** from the Production environment on a regular cadence (e.g., monthly or quarterly) and store the `.zip` file in a secure location as a disaster recovery artifact.