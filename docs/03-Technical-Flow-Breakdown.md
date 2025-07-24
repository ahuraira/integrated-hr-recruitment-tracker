# 03: Technical Flow Breakdown

## Introduction

This document provides a detailed technical analysis of each Power Automate flow within the Manpower Requisition (MPR) Automation Suite. It is intended for developers, system administrators, and technical support personnel. Each section breaks down a flow's trigger, variables, core logic, key formulas, and error handling strategy.

---

## 1. Flow: MPR-01-InitiationandApproval

-   **Filename:** `MPR-01-InitiationandApproval-41EB0FF3-D357-F011-BEC1-6045BD8936D0.json`
-   **Purpose:** To capture new manpower requisitions from a Microsoft Form, create a corresponding record in the SharePoint MPR Tracker, generate a unique Requisition ID, and manage the entire VP/EVP approval process.

#### Trigger
-   **Type:** `OpenApiConnectionWebhook`
-   **Connector:** Microsoft Forms
-   **Action:** `When a new response is submitted`
-   **Details:** The flow initiates immediately after a user submits the "Manpower Requisition Form."

#### Key Variables
-   `varNewSequenceNymber` (Integer): Stores the calculated sequential number for the new Requisition ID. Initialized to `1` to handle the first request for any given Business Unit.
-   `varApprovalAttachemnts` (Array): Collects file attachments (name and content bytes) from the form submission to be included in the approval notifications.

#### High-Level Logic
1.  A new form response triggers the flow.
2.  It retrieves the full details of the form submission.
3.  It queries the `MPR Tracker` list to find the highest existing sequence number for the requester's Business Unit.
4.  It calculates the next sequence number (or uses 1 if none exists).
5.  It creates a new item in the `MPR Tracker` list with a uniquely formatted `RequisitionID`.
6.  It processes any file uploads from the form, adding them as attachments to the new SharePoint item and to the `varApprovalAttachemnts` variable.
7.  It queries the `Configuration` list to get the email address of the relevant VP.
8.  It starts an approval process, assigning it to the VP.
9.  **If Approved:** It checks the `Grade`. If the grade is > 15, it repeats the approval process for the EVP. Once all approvals are complete, it updates the MPR status to "MPR Approved."
10. **If Rejected:** It updates the MPR status to "Rejected."
11. In both cases, it sends a final notification email and Teams message to the original requester.

#### Detailed Step-by-Step Analysis
-   **Sequence Number Calculation:** This is a critical piece of custom logic.
    1.  `Get_last_sequence_number`: A `GetItems` action on the `MPR Tracker` list.
    2.  **$filter:** `BusinessUnit eq '@{...}'` to isolate requisitions from the same unit.
    3.  **$orderby:** `RequisitionSequenceNumber desc` to ensure the newest/highest is first.
    4.  **$top:** `1` to retrieve only that single highest record.
    5.  `Check_if_Business_Unit_Already_has_any_MPR`: A condition that checks if the `GetItems` action returned any results (`empty(...)` is false). If it did, it calculates the new number using an `add()` expression; otherwise, it uses the default initialized value of `1`.
-   **Approval Logic:** The flow uses a `Start_and_wait_for_an_approval` action. The approver's email is dynamically fetched from the `Configuration` list, not hard-coded. The nested condition `Check_if_EVP_Approval_is_needed` is a direct implementation of the hierarchical governance business rule.

#### Key Expressions & Formulas
-   **Requisition ID Generation (`Create_item` action):**
    ```power-fx
    concat(
      'MPR-',
      replace(trim(outputs('Get_response_details')?['body/rd75...']), 'TTE ', ''),
      '-',
      formatNumber(variables('varNewSequenceNymber'), '000')
    )
    ```
    -   This concatenates the static prefix "MPR-", the cleaned Business Unit, and the 3-digit zero-padded sequence number.

#### Error Handling Strategy
-   Currently relies on the default Power Automate behavior. If any step (like `GetItems` or an approval) fails, the flow run will fail and require manual inspection and resubmission by an administrator.

---

## 2. Flow: MPR-02-HRAssignment

-   **Filename:** `MPR-02-HRAssignment-A903968A-A760-F011-BEC2-7C1E52273770.json`
-   **Purpose:** To detect when an MPR has been fully approved and facilitate its assignment to a specific HR Representative by the HR Manager.

#### Trigger
-   **Type:** `OpenApiConnection` (Recurrence)
-   **Connector:** SharePoint
-   **Action:** `When an item is created or modified`
-   **Trigger Condition:** `@equals(triggerBody()?['Status']?['Value'], 'MPR Approved')`
-   **Details:** This flow polls the `MPR Tracker` list. The trigger condition is crucial: it ensures the flow only runs for items that have just entered the "MPR Approved" state, effectively "listening" for the completion of Flow 1.

#### Key Variables
-   None.

#### High-Level Logic
1.  The flow is triggered when an item in `MPR Tracker` is updated to have the status "MPR Approved."
2.  It queries the `Configuration` list to get the HR Manager's and HR Team's email addresses.
3.  It formats the list of HR Team members into a JSON array suitable for an Adaptive Card ChoiceSet.
4.  It posts an Adaptive Card to the HR Manager in a private Teams chat. This card displays the MPR details and a dropdown menu to select an HR Rep. The flow then pauses.
5.  When the HR Manager makes a selection and submits the card, the flow resumes.
6.  It parses the response from the card to identify the selected HR Rep's email.
7.  It updates the original MPR item in SharePoint, setting the `AssignedTo` field to the selected HR Rep and changing the `Status` to "CV Sourcing."
8.  It sends confirmation notifications to the newly assigned HR Rep and the original requester.

#### Detailed Step-by-Step Analysis
-   **Adaptive Card Interaction:** The `Post_adaptive_card_and_wait_for_a_response` action is the core of this flow. It creates a rich, interactive UI within Teams and pauses the flow execution indefinitely until a response is received, making it a powerful human-in-the-loop tool. The choices in the dropdown are dynamically populated by the `Select` action, which transforms the SharePoint items from the `Configuration` list into the required format.

#### Key Expressions & Formulas
-   **Trigger Condition:** As noted above, `@equals(triggerBody()?['Status']?['Value'], 'MPR Approved')` is the most important expression, making the entire flow event-driven.

#### Error Handling Strategy
-   Default behavior. A failure in posting the card or updating the item will cause the flow run to fail.

---

## 3. Flow: MPR-03-CandidateLifecycleManagement

-   **Filename:** `MPR-03-CandidateLifecycleManagement-1855A04B-BC67-F011-BEC2-7C1E52273770.json`
-   **Purpose:** A "router" flow that handles two distinct scenarios for the `Candidate Tracker` list: generating a new Candidate ID upon creation and executing specific user-driven actions like scheduling interviews.

#### Trigger
-   **Type:** `OpenApiConnection` (Recurrence)
-   **Connector:** SharePoint
-   **Action:** `When an item is created or modified` on the `Candidate Tracker` list.

#### High-Level Logic
-   **Path A: New Candidate Creation**
    1.  The flow triggers when a new item is created. A condition `empty(triggerBody()?['CandidateID'])` checks if the `CandidateID` field is blank.
    2.  If it is, the flow queries the `Candidate Tracker` list for all "sibling" candidates linked to the same parent `RequisitionID`.
    3.  It calculates the next sequence number using `add(length(...),1)`.
    4.  It constructs the new `CandidateID` (e.g., `MPR-TTE-001-C01`).
    5.  It updates the newly created candidate item with this ID and sets the initial `Status` to "Shortlisted."

-   **Path B: User-Driven Action**
    1.  The flow triggers when an item is modified. The condition `empty(triggerBody()?['CandidateID'])` is false.
    2.  The flow proceeds to a `Switch` action that evaluates the `NextAction_x0028_Trigger_x0029_/Value` column.
    3.  **Case: "Schedule Next Interview"**: It creates calendar events for all members of the `InterviewPanel` people-picker field, creates a new log entry in the `Interview Tracker` list, and crucially, **resets the `NextAction...` column to "Waiting for Input."**
    4.  **Case: "Request Offer Approval"**: It initiates a multi-level approval process for the offer letter, similar to Flow 1.
    5.  The reset of the `NextAction...` column is a critical "reset to idle" pattern that hands control back to the HR Rep and prevents accidental re-triggers.

#### Detailed Step-by-Step Analysis
-   **Dual-Purpose Trigger:** The initial `If` condition is a powerful pattern that allows a single flow to handle both `OnCreate` and `OnModify` events with different logic paths.
-   **Human-in-the-Loop Control:** The `Switch` statement on the `NextAction...` column is the primary mechanism for user-driven automation in the entire suite. It empowers the HR Rep to command the system on demand.

#### Key Expressions & Formulas
-   **Candidate ID Generation (`Compose_-_Format_New_Candidate_ID` action):**
    ```power-fx
    concat(
      ..., // Expression to get parent Requisition ID
      '-C',
      formatNumber(outputs('Compose_-_Calculate_Next_Sequence_Number'), '00')
    )
    ```
    -   This appends the candidate-specific suffix to the parent ID.

#### Error Handling Strategy
-   Default behavior.

---

## 4, 5, & 6. Flows: The Feedback Collection Loop

These three flows work in concert to manage the interview feedback process.

### 4. Flow: MPR-04-TriggerPostInterviewActions
-   **Purpose:** To proactively send feedback request forms to interviewers after an interview is completed.
-   **Trigger:** `Recurrence` (Scheduled to run daily).
-   **Logic:**
    1.  Gets all items from the `Interview Tracker` list where the interview date has passed but `FeedbackStatus` is still "Pending."
    2.  For each interview, it loops through the `InterviewPanel`.
    3.  For each interviewer, it creates a new, unique item in the `Interview Feedback Tracker` list.
    4.  It sends an email to the interviewer containing a hyperlink to the feedback form. This link is dynamically constructed to include the ID of the `Interview Feedback Tracker` item created in the previous step as a URL parameter.
    5.  Updates the `Interview Tracker` status to "Requests Sent."

### 5. Flow: MPR-05-CaptureInterviewFeedback
-   **Purpose:** To capture submitted feedback and update the corresponding records.
-   **Trigger:** `When a new response is submitted` to the "Interview Feedback Form."
-   **Logic:**
    1.  Retrieves the form response details.
    2.  The response contains the ID for the `Interview Feedback Tracker` item (passed via the URL parameter). The flow uses this ID to `PatchItem` with the feedback, recommendation, and any attachments.
    3.  It then checks if all feedback for the parent `Interview Tracker` event has now been received.
    4.  If all feedback is complete, it updates the parent `Interview Tracker` status to "Received" and notifies the HR Rep.

### 6. Flow: MPR-06-TransferInterviewFeedbackBackToInterviewTra
-   **Purpose:** To serve as a manual consolidation and finalization step driven by the HR Representative.
-   **Trigger:** `When an item is created or modified` on the `Interview Feedback Tracker` list, with a trigger condition: `@equals(triggerBody()?['TreatasFinalFeedback'], true)`.
-   **Logic:**
    1.  This flow only runs when an HR Rep manually checks the "Treat as Final Feedback" box on a specific feedback entry.
    2.  It takes the feedback and recommendation from that specific entry.
    3.  It updates the parent `Interview Tracker` item, copying the feedback details.
    4.  It then updates the parent `Candidate Tracker` item, setting its status to "HR Selection" or "Rejected" based on the final recommendation. This officially moves the candidate to the next stage or ends their journey.

#### Detailed Step-by-Step Analysis of the Loop
-   The key to this entire loop is the **passing of the SharePoint item ID in the URL of the feedback form**. In Flow 4, the URL is built like this: `concat('https://forms.office.com/...', '&...ID=', outputs('Create_feedback_record')?['body/ID'])`. This allows Flow 5 to be stateless; it doesn't need to guess which item to update, it is explicitly told in the form data itself. Flow 6 provides a manual override for HR to accelerate the process or select a single definitive piece of feedback.

---
_This document details the internal logic of each flow. For information on how end-users interact with the system, please see [04-User-Guides.md](./04-User-Guides.md)._