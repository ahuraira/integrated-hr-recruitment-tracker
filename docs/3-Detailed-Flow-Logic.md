# Detailed Flow Logic: Phase 1 - MPR

## 1. Introduction

This document provides a technical deep-dive into the Power Automate flow (`MPR - 01 - Initiation and Approval`). It explains the function of each major block of actions, clarifies the purpose of complex expressions, and highlights critical configurations. This guide should be used for troubleshooting, maintenance, and future development.

**It is highly recommended to have the Power Automate flow open in another window to follow along with this documentation.**

---

## 2. Overall Flow Structure

The flow is designed as a single, trigger-based workflow that orchestrates the entire approval process. It follows these major logical stages:

1.  **Data Ingestion & Validation:** Triggered by the form, captures all user input.
2.  **Attachment & Variable Preparation:** Handles the attached file and prepares variables.
3.  **Sequential ID Generation:** Calculates the next unique `Requisition ID`.
4.  **Main Record Creation:** Creates the central item in the `MPR Tracker` SharePoint list.
5.  **VP Approval Block:** Manages the first level of approval.
6.  **Conditional EVP Approval Block:** Manages the second, grade-dependent approval level.

---

## 3. Section I: Trigger and Data Ingestion

*(Insert your screenshot of the top part of the flow here)*

This section is responsible for starting the flow and gathering all necessary data from the user's submission.

-   **1. When a new response is submitted:**
    -   **Connector:** Microsoft Forms
    -   **Purpose:** The sole trigger for the entire workflow. It fires the instant a user clicks "Submit" on the `Manpower Requisition Form`.

-   **2. Get response details:**
    -   **Connector:** Microsoft Forms
    -   **Purpose:** Retrieves the actual answers from the specific form submission that triggered the flow.

-   **3. Parse JSON to get name and link of attached file:**
    -   **Connector:** Data Operation
    -   **Purpose:** The file upload question in MS Forms returns a JSON string. This action parses that string into structured data (name, id, link, etc.) that can be used in later steps.
    -   **Configuration:** The schema is generated from a sample payload to expect an **array** of file objects.
    -   **Note:** This action is inside a condition to ensure it only runs if a file was actually uploaded, preventing errors on submissions with no attachment.

---

## 4. Section II: Attachment & Variable Preparation

*(Insert your screenshot of the attachment and variable initialization part here)*

This block prepares the file attachment and initializes key variables.

-   **1. For each file attached in MS form:**
    -   **Control:** Apply to each
    -   **Purpose:** This loop processes each file uploaded by the user (even though we limit it to one). It is automatically created when using the output of the `Parse JSON` action.

-   **2. Get file content using path:**
    -   **Connector:** OneDrive for Business
    -   **Purpose:** Reads the binary content of the uploaded file from the creator's OneDrive folder where MS Forms stores it. The file path is constructed dynamically using the `name` property from the `Parse JSON` output.

-   **3. Initialize Approval Attachments:**
    -   **Connector:** Variable
    -   **Purpose:** Creates an **Array** variable named `varApprovalAttachments`. This variable will be used to build the attachment array that is passed to the `Start and wait for an approval` action, allowing approvers to view the attachment directly in the approval request.

-   **4. Append to array variable:**
    -   **Connector:** Variable
    -   **Purpose:** Inside the file loop, this action adds the attachment content to the `varApprovalAttachments` variable. It formats the file into the specific JSON object structure that the Approvals connector requires: `{"Name": "...", "Content": "..."}`.

-   **5. Select:**
    -   **Connector:** Data Operation
    -   **Purpose:** This action finalizes the attachment array for use in the approval email. It ensures the content bytes are correctly formatted. The `Start and wait for an approval` action will use the output of this `Select` action for its attachments.

---

## 5. Section III: Sequential ID Generation

*(Insert your screenshot of the ID generation logic here)*

This is a critical block that generates a user-friendly, unique ID like `MPR-EC-024`.

-   **1. Get Last Sequence Number:**
    -   **Connector:** SharePoint (`Get items`)
    -   **Purpose:** Queries the `MPR Tracker` list to find the single most recent item for the same **Business Unit**.
    -   **Key Configuration:**
        -   **Filter Query:** `Business_x0020_Unit eq '[Business Unit]'` (Note the single quotes around the dynamic content).
        -   **Order By:** `Requisition_x0020_Sequence_x0020_Number desc`
        -   **Top Count:** `1`

-   **2. Initialize variable & Condition:**
    -   **Purpose:** An integer variable `varNewSequenceNumber` is initialized to a default value of `1`. A condition then checks if the `Get Last Sequence Number` step found anything.
    -   **Logic:**
        -   **If Nothing Found (first entry for this BU):** The variable remains `1`.
        -   **If an Item Was Found:** The flow proceeds to the `Compose` action.

-   **3. Compose & Set variable:**
    -   **Purpose:** The `Compose` action calculates the new sequence number by adding 1 to the number from the last item found. We use `Compose` because the `Set variable` action can have issues with complex expressions. The result from `Compose` is then used to update `varNewSequenceNumber`.
    -   **Expression:** `add(int(outputs('Get_Last_Sequence_Number')?['body/value'][0]?['Requisition_x0020_Sequence_x0020_Number']), 1)`

---

## 6. Section IV: VP & EVP Approval Blocks

*(Insert your screenshots of the approval blocks here)*

These sections are nearly identical and manage the approval cycles.

-   **1. Get VP/EVP from Config List:**
    -   **Connector:** SharePoint (`Get items`)
    -   **Purpose:** Retrieves the correct approver's user profile from the `System Configuration` list based on the form input.
    -   **Filter Query (VP):** `Title eq 'TTE [Business Unit] VP'`
    -   **Filter Query (EVP):** `Title eq 'TTE EVP'`

-   **2. Start and wait for an approval:**
    -   **Connector:** Approvals
    -   **Purpose:** Creates and sends the approval request via Teams and Outlook. It pauses the flow until a response is received.
    -   **Key Configuration:**
        -   **Assigned To:** Uses the `Approver Email` from the `Get...from Config List` step.
        -   **Attachments:** Uses the output from the `Select` data operation to include the uploaded MPR form in the request.

-   **3. Condition (Outcome Check):**
    -   Checks if the approval `Outcome` is equal to "Approve". The logic for approval (`True` branch) and rejection (`False` branch) is handled separately.

-   **4. Update Item & Notifications:**
    -   **`Update item`:** Changes the relevant status fields (`VP Approval Status`, `EVP Approval Status`, overall `Status`) and logs the decision date.
    -   **`For each` Loops for Notifications:** As detailed in our previous discussions, we use variables to store the `Approver Name`, `Response`, and `Comments` to avoid nested loops when sending emails and Teams messages.

-   **5. Conditional EVP Approval Logic:**
    -   The entire EVP approval block is nested inside a condition that checks if the `Grade` from the created SharePoint item is greater than `15`. This ensures the second approval step only runs when required by business rules.