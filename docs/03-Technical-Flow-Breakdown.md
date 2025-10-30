# 03: Technical Flow Breakdown

## 1. Introduction

This document provides a detailed technical analysis of each Power Automate flow within the Manpower Requisition (MPR) Automation Suite. It is intended for developers, system administrators, and technical support personnel who need to understand the internal workings of the automation logic.

Each section breaks down a flow's purpose, trigger mechanism, key variables, high-level logic, and a detailed analysis of its most critical steps and expressions. This is the definitive guide to the "how" of the system.

---

## 2. System Governance Flows

These two background flows are the "brain" and "heartbeat" of the entire suite. They do not manage a single transactional process but instead provide overarching governance, monitoring, and analytics across the entire system.

### 2.1. Flow: `MPR-SYS-MonitorSLAs`

-   **Filename:** `MPR-SYS-MonitorSLAs-BEF87AAD-FF8E-F011-B4CB-7C1E52273770.json`
-   **Purpose:** To act as the central "guardian" of process efficiency. This flow runs on a daily schedule to proactively monitor all active requisitions and candidates against their pre-calculated SLA target dates, sending tiered notifications and escalations for items nearing or in breach of their SLA.

#### Trigger
-   **Type:** `Recurrence` (Scheduled).
-   **Configuration:** The flow is configured to run once daily at a specific time (e.g., 8:00 AM). This cadence provides timely daily notifications without creating excessive system load.

#### Key Variables
-   **Encapsulation Strategy:** To ensure robust parallel execution, all calculation variables are initialized **inside** their respective `Scope` containers, not at the global level. This prevents race conditions.
-   `var[Stage]SLADays` (Integer): Stores the SLA day count (e.g., `2` for Approval) fetched from the `Configuration` list.
-   `var[Stage]DaysCounter` (Integer): The primary counter used by the business day calculation engine. It is reset to `0` for every item being processed.
-   `var[Stage]RunnerDate` (String): The "iterator" date used in the `Do until` loop for business day calculations, formatted as 'yyyy-MM-dd'.

#### High-Level Logic
The flow is architected with a **modular, parallel branch structure**. Each branch is a self-contained `Scope` responsible for monitoring a single SLA (e.g., `Monitor_MPR_Approval_SLA`, `Monitor_Sourcing_SLA`). This design allows for concurrent processing and isolates failures.

The core logic within each branch follows the sophisticated **"Calculate and Switch"** enterprise pattern:
1.  **Get Active Items:** Fetches all SharePoint items that are currently in a state relevant to the SLA being checked (e.g., `Status eq 'MPR Form Submitted'`).
2.  **Loop & Calculate:** It loops through each item. For each one, it first checks if today is a business day. If so, it executes a "Business Day Calculator" `Scope` to determine the exact number of business days remaining until the pre-calculated `SLATargetDate` (a positive number), or the number of days overdue (a negative number).
3.  **Switch & Act:** A `Switch` statement on the calculated number of days executes the appropriate tiered notification logic based on the item's current `SLAStatus` to prevent duplicate alerts.

#### Detailed Step-by-Step Analysis
-   **Business Day Calculator:** This is the most complex component. It uses two `Do until` loops within a conditional block.
    1.  A condition checks if the `TargetDate` is in the future or the past.
    2.  If in the future, it loops forward from `utcNow()` to the `TargetDate`, incrementing a counter for each weekday encountered.
    3.  If in the past, it loops *backward* from `utcNow()` to the `TargetDate`, *decrementing* a counter for each weekday, resulting in a negative number that signifies a breach.
-   **Stateful Notifications:** The `Switch` statement is paired with a nested `Condition` that checks the item's current `SLAStatus` (e.g., `ApprovalSLAStatus`). This ensures that the "Warning" notification is only sent if the status is `On Track`, and the "Due Today" notification is only sent if the status is `Warning Sent`, etc. This creates a reliable, stateful notification machine.
-   **Dynamic Recipients:** Notifications are sent to the correct stakeholders by reading from the SharePoint item's "Person" fields (e.g., `AssignedTo/Email`, `HiringManager/Email`), ensuring the alerts are always contextual.

#### Key Expressions & Formulas
-   **Timezone-Aware Date:** `formatDateTime(convertFromUtc(utcNow(), 'Arabian Standard Time'), 'yyyy-MM-dd')` is used to establish a reliable "today" value for all calculations.
-   **Weekday Check:** `dayOfWeek(variables('varRunnerDate'))` is used within a condition to check if the day is not `0` (Sunday) or `6` (Saturday).

### 2.2. Flow: `MPR-SYS-UpdateMPRAggregates`

-   **Filename:** `MPR-SYS-UpdateMPRAggregates-4072E411-2787-F011-B4CB-7C1E52273770.json`
-   **Purpose:** To function as a real-time analytics engine. It runs whenever a candidate's record is changed, recalculates a comprehensive set of KPIs and pipeline counts for the parent MPR, and updates the master `MPR Tracker` item.
-   **Trigger:** `When an item is created or modified` on the `Candidate Tracker` list.

#### Key Variables
-   `varTotal[KPI]`, `var[KPI]Counter` (Integer): A pair of variables is used for each time-based KPI (e.g., `varTotalTimeToFill`, `varTimeToFillCounter`) to maintain running totals and counts during the calculation loop.

#### High-Level Logic
1.  The flow is triggered by any change to a candidate record.
2.  It retrieves the parent `MPR Tracker` item.
3.  It then performs a `Get items` to fetch **all** "sibling" candidates for that same MPR to ensure its calculations are based on the complete and current dataset.
4.  **Count Aggregation:** It uses a series of `Filter array` actions to efficiently count the number of candidates in key stages (`Offer Accepted` for "Hired", `Interview Process Ongoing`, `Offer Extended`).
5.  **KPI Calculation:** It initializes multiple variables for KPI totals and counters. It then runs several distinct `Apply to each` loops over the full set of sibling candidates. Each loop is responsible for calculating one specific time-based KPI by:
    *   Checking if the required start and end dates for that KPI exist on the candidate item.
    *   Calculating the duration in days using the `div(sub(ticks(...)))` expression.
    *   Incrementing the appropriate total and counter variables.
6.  **Final Update:** It performs a single `Update item` action on the parent `MPR Tracker`. This action populates all the aggregate count fields (e.g., `PositionsFilled`) and the calculated average KPI fields (e.g., `AvgTimeToFill`), using a `if(greater(..., 0), ...)` expression to safely handle division by zero.

#### Detailed Step-by-Step Analysis
-   **Decoupled Calculation Loops:** While running multiple `Apply to each` loops over the same dataset may seem inefficient, it is a deliberate and robust design choice. It keeps the logic for each KPI calculation completely separate and modular. This makes it far easier to debug or modify the calculation for "Time to Fill" without any risk of breaking the "Time to Offer" calculation.
-   **Comprehensive Data Retrieval:** The key to this flow's accuracy is the `Get All Sibling Candidates` step. By re-querying the entire dataset on every run, it ensures that its calculations are always based on the absolute current state of the entire pipeline for that MPR, rather than incremental changes, which prevents data drift and synchronization issues.

#### Key Expressions & Formulas
-   **Safe Average Calculation:** `if(greater(variables('varTotalTimeToFillCounter'), 0), div(variables('varTotalTimeToFill'), variables('varTotalTimeToFillCounter')), null)`
-   **Date Difference in Days:** `div(sub(ticks(items('...')['DateOfferAcceptance']), ticks(items('...')['MPRApprovalDate'])), 864000000000)`

---

## 3. Core Requisition & Assignment Flows

These flows manage the primary lifecycle of the Manpower Requisition itself, from its birth in a form to its assignment to the HR team.

### 3.1. Flow: `MPR-01-InitiationandApproval`

-   **Filename:** `MPR-01-InitiationandApproval-41EB0FF3-D357-F011-BEC1-6045BD8936D0.json`
-   **Purpose:** The entry point for the entire recruitment process. This flow is responsible for capturing a new MPR, creating the master record, managing a dynamic multi-level approval process, and implementing the foundational security and SLA rules for the new requisition.

#### Trigger
-   **Type:** `OpenApiConnectionWebhook` (Microsoft Forms).
-   **Action:** `When a new response is submitted` to the "Manpower Requisition Form."

#### Key Variables
-   `varNewSequenceNymber` (Integer): Stores the calculated sequential number for the new `RequisitionID`.
-   `varApprovalAttachemnts` (Array): Used to collect and format file attachments for the `Start and wait for an approval` action. *(Note: Based on final implementation, this is prepared but the approval action uses an item link instead).*
-   `varRunnerDate` & `varDaysCounter` (String & Integer): Used exclusively within the "Business Day Calculator" `Scope` to calculate the SLA target date.

#### High-Level Logic
1.  A new form response triggers the flow, and the details are retrieved.
2.  The flow queries the `MPR Tracker` to find the highest existing sequence number for the requester's Business Unit to calculate the next number.
3.  It creates the new item in the `MPR Tracker` list with a uniquely formatted `RequisitionID` and a status of `MPR Form Submitted`.
4.  **SLA Target Date Calculation:** It immediately executes the "Business Day Calculator" `Scope` to determine the `TargetApprovalDate` based on the configured SLA days and updates the new item with this date and an `ApprovalSLAStatus` of `On Track`.
5.  **Security Provisioning:** It then executes the critical "Break Inheritance and Grant Access" pattern:
    *   It calls `Stop sharing an item or a file` to make the new MPR item private.
    *   Inside the VP loop it uses `Grant access to an item or a folder` to add the Requester, Hiring Manager, and the matched VP as collaborators on the record under the same permission level (`role:1073741826`, i.e., Edit).
    *   Immediately after granting access, it patches the item with the VP's email address and sets `VPApprovalStatus` to `Pending`, priming the approval SLA tracking logic.
6.  It retrieves the designated VP from the `Configuration` list and initiates the `Start_and_wait_for_an_approval` action.
7.  **Conditional Logic:** Based on the approval outcome, it follows one of two paths:
    *   **If Rejected:** It updates the status to `Rejected`, logs the approver's comments, and sends a notification to the requester. This notification includes a dynamically generated **pre-filled form link** to simplify the resubmission process. It also updates the original rejected MPR if the new submission is a "resubmission."
    *   **If Approved:** It logs the VP's approval and date, then immediately checks whether the `Grade` value is greater than `9`. Grades above that threshold trigger a second `Start and wait for an approval` with the EVP; grades at or below `9` skip the EVP path and directly mark the requisition as `MPR Approved`.
8.  **Finalization:** Once all necessary approvals are secured, it updates the final `Status` to `MPR Approved` and `MPRApprovalDate`, triggering the next flow in the sequence (`MPR-02a`).

#### Detailed Step-by-Step Analysis
-   **Item-Level Security Implementation:** This is a cornerstone of the flow's robustness. The sequence of `Stop sharing...` followed by a targeted `Grant access...` step ensures that only the requester, Hiring Manager, and the configuration-derived VP retain access immediately after creation.
-   **Status Priming for SLA Tracking:** After permissions are reassigned, the flow explicitly sets `VPApprovalStatus` to `Pending` and stamps the VP's email on the item. This drives downstream monitoring and reporting logic that looks for pending VP approvals.
-   **Business Day Calculator Scope:** This self-contained `Scope` is the engine for setting the SLA target date. It is a reusable pattern that correctly calculates a future date by skipping weekends, ensuring the SLA monitor will function correctly.
-   **Resubmission Handling:** The `Check_-_If_it_is_a_resubmission` condition adds a layer of business intelligence. By finding the original rejected MPR and creating a two-way link (`SupersededBy`), it provides an invaluable audit trail for tracking the history of a position request.
-   **Attachment Handling:** The flow robustly handles file uploads from the MS Form. It iterates through the files, gets their content from OneDrive, and uses the `Add attachment` action to copy them securely to the newly created SharePoint item.

#### Key Expressions & Formulas
-   **Requisition ID Generation:** A `concat()` expression that combines the "MPR-" prefix, a cleaned version of the Business Unit, and a `formatNumber(..., '000')` of the `varNewSequenceNymber`.
-   **Prefilled Form URL:** A complex `concat()` expression that chains together the base form URL with `&[QuestionID]=` and `encodeUriComponent(...)` for every single field from the original submission. This ensures all data is preserved for easy correction.

### 3.2. Flow: `MPR-02a-HRAssignment`

-   **Filename:** `MPR-02a-HRAssignment-42388670-258B-F011-B4CB-7C1E52273770.json`
-   **Purpose:** To act as the automated handoff between the approval and sourcing stages. It assigns the approved MPR based on business rules and provisions the necessary digital workspace for the HR team.
-   **Trigger:** `When an item is created or modified` on the `MPR Tracker` list.
-   **Trigger Condition:** `@equals(triggerBody()?['Status']?['Value'], 'MPR Approved')`. This makes the flow a highly efficient "listener" that only runs when `MPR-01` has successfully completed its job.

#### High-Level Logic
1.  The flow triggers when an MPR's status is set to `MPR Approved`.
2.  **Rule-Based Assignment:** It immediately enters a `Condition` block that checks the `BusinessUnit` of the MPR.
    *   If the unit is "TTE EC" or "TTE PS," it executes an `Update item` action that hard-codes the `AssignedTo/Claims` field to a specific user (`abc@xyz.ae`).
    *   If the unit is anything else (i.e., "TTE FM"), it assigns it to a different specific user (`def@xyz.ae`).
    *   The status is updated to `Assigned to HR`.
3.  **SLA Target Date Calculation:** It then executes the "Business Day Calculator" `Scope`, using the `MPRApprovalDate` as the start date, to calculate and set the `TargetSourcingDate`.
4.  **Security Provisioning:** It uses `Grant access to an item or a folder` to ensure the newly assigned HR Representative has `Contribute` access to that specific MPR item.
5.  **Workspace Provisioning:** This is a major function of this flow. It performs a series of `Create new folder` actions to build the standardized folder structure (e.g., `MPR-EC-024 - Senior Accountant/1. New CVs (Drop Files Here)`, etc.) in the `CV Intake` document library.
6.  **Final Notification:** It sends a detailed notification email to the assigned HR Representative, welcoming them to the assignment and providing direct links to both the MPR item in SharePoint and, crucially, the "New CVs" folder where they will upload their sourced candidates.

#### Detailed Step-by-Step Analysis
-   **Architectural Shift:** This flow represents a deliberate shift *away* from a flexible, user-driven assignment (via an Adaptive Card) to a rigid, high-speed, rule-based assignment. This decision prioritizes automation speed and consistency over administrative flexibility.
-   **Folder Name Sanitization:** The flow includes a `Compose` action that uses a nested `replace()` expression to remove characters that are illegal in SharePoint folder names (`/`, `\`, `:`, etc.) from the Job Title, ensuring the folder creation process is resilient to variations in user input.
-   **Hard-coded vs. Configuration:** The choice to hard-code the assigned user emails (`i:0#.f|membership|...`) directly into the `Update item` actions is a key design decision. While less flexible than looking up the names from the `Configuration` list, it is more direct and has fewer points of failure. This is a trade-off between flexibility and simplicity.

---

## 4. AI Ingestion & Hiring Manager Review Flows

This suite of three interconnected flows represents the most advanced and user-centric part of the system. They work together to automate CV data extraction and provide a best-in-class review experience for Hiring Managers.

### 4.1. Flow: `CVIngestion` (`MPR-08`)

-   **Filename:** `CVIngestion-277CEF83-5DA0-F011-BBD2-7C1E52511989.json`
-   **Purpose:** To act as the intelligent front door for all new candidates. This flow is a high-performance engine that triggers on a new CV file, orchestrates a call to a pro-code Azure Function for AI processing, and populates the SharePoint data backend.

#### Trigger
-   **Type:** `When a file is created (properties only)` (SharePoint).
-   **Trigger Condition:** A robust `and/or` expression ensures the flow only fires for files created in a folder path that ends with `1. new cvs (drop files here)`.
    `@and( not(equals(triggerOutputs()?['body/{Path}'], null)), or( endswith(toLower(trim(triggerOutputs()?['body/{Path}'])), '1. new cvs (drop files here)'), ... ) )`
    The trigger polls every minute, giving near-real-time ingestion without overwhelming SharePoint.

#### High-Level Logic
The flow is architected for maximum resilience using a **`Try / Catch / Finally`** pattern implemented with `Scope` controls.

0.  **Preparation Steps:** Before entering the `Try` scope the flow loads SLA configuration and primes state:
    *   `Get_Configuration` + `Filter_SLA_Days` read the `Configuration` list to pull the "SLA - Shortlisting Days" value.
    *   Three variables are initialized: `varRunnerDate` (candidate file creation date converted from UTC to Arabian Standard Time), `varDaysCounter` (integer countdown of remaining business days), and `varIsSuccess` (default `true`). An auxiliary `vrErrorMessage` string and placeholder text variables (`varCvText`, `varCvsSkills`) are also initialized for completeness.

1.  **Try Block (Main Process):**
    *   The flow gets the file content and extracts the `RequisitionID` from the folder path.
    *   It retrieves the parent `MPR Tracker` item to get essential context, like the `Job Title`.
    *   **The core action:** It makes a premium `HTTP` call to a dedicated Azure Function, passing a JSON payload with the `fileName`, `fileContent` (Base64 encoded), and `jobTitle`.
    *   Upon receiving a successful (HTTP 200) response, it uses `Parse JSON` to structure the rich data returned by the AI engine.
    *   The **`Get_Candidate_ID_and_Target_Sourcing_Date_Ready`** scope calculates the next sequential Candidate ID (e.g., `MPR-EC-024-C02`) by counting sibling candidates, then reuses the business-day engine to set `TargetShortlistingDate`.
    *   `Create_Candidate_for_the_CV` persists the structured profile, copies over recruiter / requester / hiring manager people fields, sets the SLA dates, and stores rich analytics such as confidence scores.
    *   The raw CV is attached to the candidate item (`Add_attachment`), giving HR a direct link back to the original file alongside the `CVSourceFileLink`.
    *   `Apply_to_each_entry_in_AI_Log` iterates through every AI call stage returned by the function and creates detailed audit rows (token usage, assistant, prompts, duration) in the `AI Log` list.
    *   Finally, it implements the item-level security pattern (`Stop sharing...` and `Grant access...`) on the newly created `Candidate Tracker` item and patches the parent MPR status to `CV Sourcing`.
2.  **Catch Block (Error Handling):**
    *   If any action in the `Try` block fails, execution jumps here.
    *   It sets a boolean variable `varIsSuccess` to `false`.
    *   It captures the complete error details using the `result('Try')` expression and stores them in a variable.
    *   It creates a log entry in the `AI Log` with a status of "Failed" and includes the detailed error message.
3.  **Finally Block (State Management):**
    *   This block **always** runs, regardless of success or failure.
    *   A `Condition` checks the value of `varIsSuccess`.
    *   Based on the flag, it uses a `Move file` action to move the source CV to either the `2. Under HM Review` folder (on success) or the `5. Failed to Process` folder (on failure). This is a critical step that prevents the flow from ever getting stuck in an infinite loop on a problematic file.

#### Detailed Step-by-Step Analysis
-   **Hybrid Architecture:** This flow is the perfect example of a hybrid low-code/pro-code solution. It uses Power Automate for what it excels at (triggers, state management, SharePoint integration) and offloads the complex, specialized task of document parsing and AI interaction to a pro-code Azure Function.
-   **Business Day Engine Reuse:** The same reusable business-day calculator pattern appears twice—first to derive `TargetShortlistingDate` for the new candidate during ingestion, and later (inside the hiring flows) to keep downstream SLAs aligned. Loading the SLA value from the `Configuration` list lets admins adjust timelines without redeploying the flow.
-   **Robust Error Handling:** The `Try/Catch/Finally` pattern is the most robust error handling mechanism available in Power Automate. It guarantees that every file is processed and its state is managed correctly, even in the event of an unexpected failure.
-   **Granular Audit Trail:** By looping over `aiCallLogs`, the flow captures token counts, model IDs, prompt text, and success flags for each assistant call—providing a forensic trail for troubleshooting AI behaviour and cost.
-   **Security Hardening:** Granting access explicitly to the HR Representative, Requester, VP, and Hiring Manager (after stripping inherited permissions) enforces least-privilege access on every candidate record, even when new stakeholders join mid-stream.

### 4.2. Flow: `MPR-SYS-SendHMReviewDigest`

-   **Filename:** `MPR-SYS-SendHMReviewDigest-A3A585E1-5DA0-F011-BBD2-7C1E52511989.json`
-   **Purpose:** To provide a best-in-class, consolidated review experience for Hiring Managers by sending a single, interactive digest of all candidates awaiting their review.
-   **Trigger:** `Recurrence` (Scheduled, e.g., daily at 9:00 AM).

#### High-Level Logic
1.  The flow triggers on its daily schedule.
2.  It performs a `Get items` on the `Candidate Tracker` list to find all candidates with `Status eq 'Pending HM Review'`.
3.  **Grouping Logic:** It then performs an efficient grouping operation to get a unique list of all Hiring Managers who have pending reviews. This is done with a `Select` action to extract the emails, followed by a `Compose` with a `union()` expression.
4.  **Main Loop:** It enters an `Apply to each` loop, iterating through each unique Hiring Manager.
5.  **Dynamic Card Construction:** Inside the loop:
    *   It uses a `Filter array` to get the subset of candidates belonging to the current manager.
    *   It initializes an empty array variable, `varCandidateCardJSON`.
    *   It enters a nested `Apply to each` loop to process each of the manager's pending candidates.
    *   Inside this inner loop, it uses `Append to array variable` to build a complex JSON object for each candidate's "cardlet," including their details and the sophisticated `Action.Submit` and `Action.ShowCard` buttons.
    *   It also proactively calculates and sets the `TargetShortlistingDate` for each candidate.
6.  **Final Composition & Sending:** After the inner loop, a final `Compose` action uses a `join()` expression to combine the array of cardlets into a single, valid Adaptive Card payload. It then uses the `Post card in a chat or channel` action to send this single, consolidated card to the manager.

#### Detailed Step-by-Step Analysis
-   **User Experience Focus:** This flow is architected entirely around providing an optimal user experience for the Hiring Manager, respecting their time by consolidating notifications.
-   **Advanced Card Logic:** The use of `Action.ShowCard` for the "Reject" action is a sophisticated pattern that allows for inline data capture (the rejection reason) without requiring the user to leave Teams. The `data` payload of the `Action.Submit` buttons is carefully constructed to pass all necessary information (`candidateID`, `decision`) to the receiving flow.
-   **The Handoff Mechanism:** A critical detail is that this flow uses `Post card in a chat or channel` and specifies a `cardTypeId`. This registers the card with the Teams bot framework, enabling the separate `MPRSystems-ProcessHMReviewCards` flow to be triggered by the response. This is the modern, robust alternative to the older `Action.OpenUrl` or `Wait for a response` patterns.

### 4.3. Flow: `MPRSystems-ProcessHMReviewCards` (`MPR-09`)

-   **Filename:** `MPRSystems-ProcessHMReviewCards-A2A585E1-5DA0-F011-BBD2-7C1E52511989.json`
-   **Purpose:** To act as the dedicated, secure webhook that receives and processes the decisions submitted by Hiring Managers from the interactive digest card.
-   **Trigger:** `When someone responds to an adaptive card` (`TeamsCardTrigger`). This trigger is specifically configured to listen for responses from cards with the `cardTypeId` of "cvShortlistCard."

#### High-Level Logic
1.  The trigger fires the instant a manager clicks a "Shortlist" or "Confirm Rejection" button on the card. The trigger body contains the full context of the interaction.
2.  A `Parse JSON` action extracts the `cardOutputs` (the `data` payload we defined).
3.  It performs a `Get item` on the `Candidate Tracker` list using the `candidateID` from the payload to retrieve the full candidate record.
4.  **"First Responder Wins" Logic:** A `Condition` checks if the `HMComments` field on the item is empty. This is a critical security and data integrity check to ensure that a decision is only processed **once** per candidate, preventing accidental duplicate submissions from the same card.
5.  If the check passes, a `Switch` on the `decision` property from the payload routes the logic.
6.  The flow then executes the appropriate `Update item` action on the `Candidate Tracker` to set the `Status` to `Shortlisted` or `Rejected` and logs the `RejectionReason`.
7.  Finally, it sends a simple confirmation message back to the manager who submitted the action, closing the loop.

---

## 5. Candidate & Interview Lifecycle Flows

Once a candidate is shortlisted, this suite of flows manages their journey through the interview, feedback, and final decision stages.

### 5.1. Flow: `MPR-03-CandidateLifecycleManagement` (Updated Logic)

-   **Filename:** `MPR-03-CandidateLifecycleManagement-1855A04B-BC67-F011-BEC2-7C1E52273770.json`
-   **Purpose:** To act as the central orchestrator for the candidate's journey post-shortlisting. It is a multi-purpose "router" flow that handles both the initial creation of a candidate record and the execution of user-driven commands from the HR Representative.

#### Trigger
-   **Type:** `When an item is created or modified` on the `Candidate Tracker` list.
-   **Trigger Condition (CRITICAL):** This flow uses a sophisticated compound `OR` condition to ensure it only runs when necessary:
    1.  `empty(triggerBody()?['CandidateID'])`: Fires for newly created candidates.
    2.  `not(equals(triggerBody()?['NextAction...'],'Waiting for Input'))`: Fires when the HR Rep selects a new command.
    3.  `equals(coalesce(triggerBody()?['Status/Value'], ''), 'Pending HM Review')`: Ensures the flow also reacts when a candidate moves back into Hiring Manager review, guaranteeing downstream SLA fields stay fresh even if the actionable command has not yet changed.

#### High-Level Logic
The flow's primary action is a `Condition` that routes execution down one of two main paths.

-   **Path A: "If Candidate ID is empty" (On Create)**
    *   This branch is responsible for initializing a new candidate record created by the AI Ingestion flow.
    *   It calculates and assigns a unique `CandidateID` (e.g., `MPR-EC-024-C01`).
    *   It copies key context (`Hiring Manager`, `Assigned HR Rep`) from the parent `MPR Tracker`.
    *   It sets item-level permissions on the new candidate record.
    *   It updates the parent `MPR Tracker` status to signal that shortlisting is in progress.

-   **Path B: "If Candidate ID exists" (On Modify)**
    *   This branch handles commands from the HR Rep. It contains a primary `Switch` on the `NextAction_Trigger` field.
    *   **Case: "Schedule Next Interview":** This is the core of the interview scheduling process.
        1.  It constructs a semi-colon delimited string of attendee emails for the calendar event.
        2.  It calls the `Create event (V4)` action to send calendar invites to the panel and the candidate.
        3.  **Sets SLA Target Date:** It runs the "Business Day Calculator" to set the `TargetFeedbackDate` on the new `Interview Schedule` item.
        4.  It creates a new log item in the **`Interview Schedule`** list, linking it to the candidate and recording the panel and dates.
        5.  **"Reset to Idle":** It performs a critical `Update item` action on the `Candidate Tracker` to clear the `NextAction_Trigger` and related fields, and sets the `Status` to `Interview Process Ongoing`.
    *   **Case: "Request Offer Approval":**
        1.  This block manages the formal approval for an offer letter.
        2.  It uses the `Get attachments` -> `Apply to each` -> `Get attachment content` pattern to prepare any attached offer letter documents.
        3.  It initiates a `Start and wait for an approval` action, routing it to the appropriate VP/EVP.
        4.  Approval moves the candidate into an `In VP Approval` state while the task is pending, and on success the flow patches the record to `Approved by VP`, stamping the decision date and updating the parent MPR to `VP Approval`. If the VP rejects the offer, the candidate remains flagged as `In VP Approval` and the HR Representative receives the rejection rationale via Teams, signalling that they must revise and resubmit manually.

#### Detailed Step-by-Step Analysis
-   **Proactive State Management:** A key feature of this flow is its proactive nature. When the HM Review process sets a candidate's status to `Shortlisted`, this flow's status-based `Switch` catches that change. It then immediately runs the "Business Day Calculator" to stamp a `TargetSchedulingDate` on the candidate, ensuring the SLA clock for the next stage starts automatically.

### 5.2. Flow: `MPR-04-TriggerPostInterviewActions`

-   **Filename:** `MPR-04-TriggerPostInterviewActions-1755A04B-BC67-F011-BEC2-7C1E52273770.json`
-   **Purpose:** A scheduled "agent" that runs daily to find recently completed interviews and proactively initiate the feedback collection process.
-   **Trigger:** `Recurrence` (Scheduled, daily).

#### High-Level Logic
1.  The flow triggers once a day.
2.  It performs a `Get items` on the **`Interview Schedule`** list with a timezone-aware filter to find all interviews that were completed on the previous day and whose `FeedbackStatus` is still `Pending`.
3.  It enters an `Apply to each` loop for each completed interview event.
4.  **Locking Mechanism:** The very first step inside the loop is a critical `Update item` that sets the `FeedbackStatus` to `Requests Sent`. This "locks" the record, guaranteeing that the flow will never send duplicate requests for the same interview.
5.  It then gets the parent `Candidate` details for context.
6.  It enters a nested `Apply to each` loop to iterate through each person on the `InterviewPanel`.
7.  **Feedback Slot Creation:** Inside this inner loop, it creates a new, unique, blank item in the **`Interview Feedback`** list for each interviewer, linking it back to the parent `Interview Schedule` event.
8.  It then sends a personalized email to that interviewer containing a dynamically generated hyperlink to the feedback form. This link includes the `ID` of the `Interview Feedback` item created in the previous step as a URL parameter.

#### Key Expressions & Formulas
-   **Trigger Query:** A complex `concat()` expression builds a date range query to find items where `NextInterviewDate` was between the start and end of the previous day, e.g., `...ge datetime'...' and NextInterviewDate le datetime'...'`.
-   **Prefilled Form URL:** `concat('https://forms.office.com/...', '&...ID=', outputs('Create_feedback_record')?['body/ID'], ...)` is used to pass the unique feedback record ID to the form.

### 5.3. Flow: `MPR-05-CaptureInterviewFeedback`

-   **Filename:** `MPR-05-CaptureInterviewFeedback-1655A04B-BC67-F011-BEC2-7C1E52273770.json`
-   **Purpose:** A dedicated "listener" that captures submitted feedback forms, logs the data, and synchronizes the status of the overall interview event.
-   **Trigger:** `When a new response is submitted` (Microsoft Forms).

#### High-Level Logic
1.  The flow triggers and gets the form response details. This includes the hidden `InterviewFeedbackID` field.
2.  It handles any file attachments uploaded with the form.
3.  It uses the `InterviewFeedbackID` to perform an `Update item` on the specific `Interview Feedback` record, populating it with the interviewer's `Recommendation` and `DetailedFeedback`.
4.  **Synchronization Logic:** This is the core of the flow.
    *   It gets the parent `Interview Schedule` item.
    *   It then performs another `Get items` on the `Interview Feedback` list, looking for any other feedback records linked to the same parent event where the `Recommendation` is still `null`.
    *   A `Condition` checks if this query returned zero results.
    *   **If all feedback is complete:** It updates the parent `Interview Schedule` item's `FeedbackStatus` to `Received` and sends a notification to the `AssignedHRRecruiter` informing them that the candidate is ready for their review and final decision.
5.  **Proactive SLA:** If all feedback is complete, it also calculates and sets the `TargetHRSelectionDate` on the parent `Candidate Tracker`, automatically starting the clock for the next stage.

### 5.4. Flow: `MPR-06-TransferInterviewFeedback...`

-   **Filename:** `MPR-06-TransferInterviewFeedbackBackToInterviewTra-1555A04B-BC67-F011-BEC2-7C1E52273770.json`
-   **Purpose:** A user-driven flow that allows the HR Rep to designate a specific piece of feedback as the "final word," which then formally updates the candidate's overall status.
-   **Trigger:** `When an item is created or modified` on the `Interview Feedback` list.
-   **Trigger Condition:** `@equals(triggerBody()?['TreatasFinalFeedback'], true)`.

#### High-Level Logic
1.  The flow triggers only when an HR Rep checks the "Treat as Final Feedback" box on a specific feedback record.
2.  It gets the parent `Interview Schedule` and `Candidate Record` for full context.
3.  It copies any attachments from the final feedback record to the parent `Interview Schedule` record, creating a consolidated file history.
4.  A `Switch` on the `Recommendation` from the final feedback determines the outcome.
5.  **If "Recommend to Proceed":** It updates the parent `Candidate Tracker` item's `Status` to `HR Selection` and proactively sets the `TargetOfferReleaseDate`.
6.  **If "Do Not Proceed":** It updates the parent `Candidate Tracker` item's `Status` to `Rejected`.
7.  If the feedback indicates another interview is needed (e.g., "Recommend to Proceed with Reservations"), it updates the `Status` to `Interview First Round Concluded` and sets a new `TargetSchedulingDate`, placing the candidate back into the scheduling loop.
---

## 6. Known Limitations & Design Considerations

This section documents key architectural decisions, trade-offs, and known limitations of the current solution. It is intended to provide context for future developers and administrators on *why* the system was built in a particular way.

### 6.1. General Architecture & Platform Constraints

-   **Standard Connectors Only:** The entire suite has been built using standard connectors available within a typical Microsoft 365 license. This was a deliberate choice to maximize accessibility and minimize licensing costs. Consequently, premium features like Child Flows were avoided in favor of a "State Machine" pattern using SharePoint status fields and modular, decoupled flows.
-   **Service Account Dependency:** The reliability of all flows is directly tied to the health of the service account used for its connections. A password change, multi-factor authentication (MFA) policy update, or license issue with the service account will cause all flows to fail. This is a standard operational dependency that requires proper IT governance.
-   **Polling Triggers & Latency:** Several critical flows (`MPR-02a`, `MPR-03`, `MPR-06`, `MPR-SYS-MonitorSLAs`, `MPR-SYS-UpdateMPRAggregates`) use polling triggers (`When an item is modified` or `Recurrence`). This means there is an inherent, variable delay (typically 1-5 minutes for item modifications, or up to the recurrence interval for scheduled flows) between an event occurring and the corresponding flow executing. The system is designed for **near-real-time**, not instantaneous, execution.
-   **API Call Limits:** All actions within the flows consume Power Platform API calls, which are subject to daily limits based on the service account's license. While the current design is efficient, a massive, sudden spike in activity (e.g., thousands of CVs uploaded in one day) could theoretically lead to throttling. The system is designed for typical enterprise volumes.

### 6.2. Flow-Specific Design Decisions

#### **MPR-01: Initiation and Approval**
-   **Attachment Handling:** The decision was made to provide a **link to the SharePoint item** in the approval notification rather than attaching files directly. This was a deliberate trade-off to ensure the approver always views the most current version of the item and its properties, and to avoid known reliability issues with PDF attachments in the Approvals connector. This requires the approver to perform an extra click.
-   **Resubmission UX:** When a request is rejected, the system generates a pre-filled link to the MS Form. This is a significant UX improvement but relies on a complex `concat()` expression that maps every form field. If the MS Form is ever modified (questions added or removed), this expression must be manually updated to match.

#### **MPR-02a: HR Assignment**
-   **Rule-Based vs. Interactive Assignment:** A key architectural decision was made to implement a **hard-coded, rule-based assignment** logic (based on Business Unit) instead of an interactive assignment via an Adaptive Card.
    *   **Pro:** This makes the assignment process instantaneous, fully automated, and highly reliable.
    *   **Con (Trade-off):** It reduces flexibility. If the assignment rules change (e.g., a new HR Rep takes over a business unit), a developer must edit and redeploy the `MPR-02a` flow. The business cannot reconfigure this themselves. This was chosen to prioritize speed and reliability over administrative flexibility.

#### **CVIngestion (`MPR-08`)**
-   **Azure Function Dependency:** This flow is critically dependent on an external Azure Function. If the function's API URL, security key (`code=...`), or the expected JSON contract (input or output) changes, this flow will fail. This requires coordinated maintenance between the Power Platform and Azure development environments.
-   **Error Handling:** The `Try/Catch/Finally` block provides robust error handling. However, it is a **"fail and move"** pattern. If the AI engine fails to process a CV, the flow will move the file to the "Failed" folder and notify an admin. It does not have an automatic retry mechanism for AI processing failures; this requires manual intervention.

#### **HM Review Flows (`MPR-SYS-SendHMReviewDigest` & `MPR-09`)**
-   **Modern Teams Trigger:** The solution uses the modern `TeamsCardTrigger` ("When someone responds to an adaptive card"). This is a robust and reliable pattern but creates a dependency on the `cardTypeId` specified in the sending flow. If this ID is ever changed, the trigger in the receiving flow must be updated to match.
-   **"First Responder Wins" Logic:** The `MPR-09` flow includes logic to check if a decision has already been made for a candidate before processing a new one. This prevents issues if a manager accidentally clicks a button twice but relies on a specific field (`HMComments`) being empty. This business rule must be maintained.

#### **SLA & KPI Flows (`MPR-SYS-MonitorSLAs` & `MPR-SYS-UpdateMPRAggregates`)**
-   **Business Day Logic:** All SLA calculations are based on a "Business Day Calculator" that excludes Saturdays and Sundays. It does **not** currently account for public holidays. This was a deliberate design choice to balance complexity and value for the initial release. Adding a dynamic holiday lookup is a potential future enhancement.
-   **Data Dependency:** The accuracy of all KPIs and SLAs is entirely dependent on the transactional flows (`MPR-01`, `MPR-03`, etc.) correctly populating the various `Date` and `Status` fields. An error in an upstream flow can lead to inaccurate analytics downstream.

---
_This document details the internal logic of each flow. For information on how end-users interact with the system, please see [04-User-Guides.md](./04-User-Guides.md)._