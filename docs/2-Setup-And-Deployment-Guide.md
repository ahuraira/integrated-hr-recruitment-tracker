# Setup & Deployment Guide: Phase 1 - MPR

## 1. Introduction

This guide provides step-by-step instructions to deploy the Manpower Requisition (MPR) automation system from scratch. Following these steps will ensure all components are configured correctly for the Power Automate flow to function as designed.

It is crucial to build the components in the order presented to ensure dependencies are met.

## 2. Prerequisites

Before you begin, ensure you have the following:

-   **Permissions:** You must have permissions to:
    -   Create a new Microsoft Team (which also creates a SharePoint Team Site).
    -   Create and modify SharePoint Online lists.
    -   Create and share a Microsoft Form.
    -   Create and run Power Automate flows.
-   **Service Account (Recommended):** While the system can be built with a personal user account, it is a **strong best practice** to use a dedicated service account (e.g., `HR.Automation@yourcompany.com`) to own all components. This prevents the system from breaking if the original creator leaves the company. The service account will need an active M365 license.

---

## 3. Step 1: Create the M365 Team & SharePoint Site

This creates the central, secure location for our data.

1.  **Create a Microsoft Team:**
    *   Navigate to Microsoft Teams and select "Join or create a team".
    *   Choose **"Create team"** -> **"From scratch"**.
    *   Select **"Private"** to restrict access.
    *   Name the team something meaningful, e.g., **`HR Recruitment Hub`**.
    *   Add the core HR team members as **Members**. Add the technical owner(s) (e.g., the service account) as **Owners**.

2.  **Access the SharePoint Site:**
    *   Navigate to the "General" channel of your new Team.
    *   Click the **"Files"** tab.
    *   Click the three dots (**...**) and select **"Open in SharePoint"**.
    *   **Bookmark this SharePoint site URL.** This is your primary workspace.

---

## 4. Step 2: Create SharePoint Lists

These lists form the database for our application. Create them on the SharePoint site from Step 1.

1.  **Create the `MPR Tracker` List:**
    *   From the site's homepage, click **+ New** -> **List**.
    *   Choose **"From blank"**. Name it **`MPR Tracker`**.
    *   Create all columns exactly as specified in the **[System Architecture - Data Model](./1-System-Architecture.md#mpr-tracker-list)** document. Paying close attention to the **Data Type** for each column is critical.

2.  **Create the `System Configuration` List:**
    *   Create another blank list named **`System Configuration`**.
    *   Create the columns as specified in the **[System Architecture - Data Model](./1-System-Architecture.md#system-configuration-list)**.
    *   **Populate this list immediately:** Add one entry for each Business Unit VP and one for the EVP. This is required for the flow to find the correct approvers.

---

## 5. Step 3: Create the Microsoft Form

This is the user-facing entry point for all new requests.

1.  **Import the Form:**
    *   Navigate to Microsoft Forms ([forms.office.com](https://forms.office.com)).
    *   Click **Quick Import**.
    *   Upload the form template provided in this repository: **[`/src/MPR-Form-Import.docx`](../src/MPR-Form-Import.docx)**.
    *   Choose to import it as a **Form**.

2.  **Configure the Form:** The import creates the basic structure, but manual configuration is required.
    *   **Add Branching Logic:** Set up the conditional questions as described in the **[Detailed Flow Logic](./3-Detailed-Flow-Logic.md#i-trigger-and-data-ingestion)** document.
    *   **Set Required Questions** and **Adjust Question Types** (e.g., set number restrictions) for data quality.
    *   **Add the File Upload Question:** Manually add a "File Upload" question at the end, titled "Please attach the filled MPR form".

3.  **Configure Form Settings:**
    *   Click the three dots (...) in the top-right of the form editor and go to **Settings**.
    *   Ensure it is set to **"Only people in my organization can respond"**.

---

## 6. Step 4: Import & Configure the Power Automate Flow

This is the engine of the system. We will import a pre-built package.

1.  **Import the Flow Package:**
    *   In Power Automate, navigate to **My flows** on the left menu.
    *   Click **Import**.
    *   Upload the flow package `.zip` file.

2.  **Configure Connections (CRITICAL):**
    *   During the import process, the screen will show all the connections the flow requires (SharePoint, Outlook, Teams, etc.).
    *   For each connection, you must **"Select during import"**.
    *   Choose **`+ Create new`** for each one to establish fresh, authenticated connections using the current account (ideally the service account). **Do not reuse old connections.** This is the most common point of failure.

3.  **Finalize the Import:** Once all connections are configured, click **Import**.

4.  **Open the Flow and Verify:**
    *   After importing, the flow will be turned off by default. **Do not turn it on yet.**
    *   Open the flow in **Edit** mode.
    *   Manually verify that the key actions are pointing to the correct assets:
        *   Check that the trigger is linked to the **correct Form ID**.
        *   Check that all SharePoint actions are pointing to the **correct Site Address and List Name**.
    *   Save the flow. You can now turn it on and begin testing.

---

## 7. Step 5: Post-Deployment Steps

1.  **Share the Form Link:** Distribute the link to the Microsoft Form to all Department Heads and requesters.
2.  **Grant SharePoint Permissions:**
    *   Navigate to the `MPR Tracker` list settings -> `Permissions for this list`.
    *   **Stop Inheriting Permissions**.
    *   Grant **"Read"** access to the VPs and EVPs so they can view the entire pipeline if they wish.
3.  **Monitor Initial Runs:** Check the run history of the first few live submissions to ensure the flow is executing without errors.