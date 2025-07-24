# 04: User Guides

## Introduction

Welcome to the user guide for the automated Manpower Requisition (MPR) system. This guide is designed to provide clear, step-by-step instructions for everyone who interacts with the recruitment process.

Please find the section relevant to your role. Our goal is to make this process as smooth and intuitive as possible.

### Table of Contents
1.  [Guide for Requesters (Hiring Managers)](#1-guide-for-requesters-hiring-managers)
2.  [Guide for Approvers (VP / EVP)](#2-guide-for-approvers-vp--evp)
3.  [Guide for the HR Manager](#3-guide-for-the-hr-manager)
4.  [Guide for the HR Representative](#4-guide-for-the-hr-representative)
5.  [Guide for Interviewers](#5-guide-for-interviewers)
6.  [Troubleshooting & Frequently Asked Questions (FAQ)](#6-troubleshooting--frequently-asked-questions-faq)

---

## 1. Guide for Requesters (Hiring Managers)

As a Requester, your primary role is to initiate a hiring request and stay informed of its progress.

### How to Submit a New Requisition

1.  **Open the Form:** Navigate to the [Manpower Requisition Form](https://forms.office.com/Pages/ResponsePage.aspx?id=MS7uvOIi7EaESeapIpgjYsZO1Rs2TDZHhwtflBPodP1UNVFRRlczMEdJTUIzM08xQkJKQ0w0WVVZUi4u) link.
2.  **Fill in Details:** Complete all fields accurately. This includes the **Job Title**, **Business Unit**, **Grade**, and a clear **Justification** for the new role.
3.  **Attach Documents (Optional):** If you have a detailed Job Description, you can attach it directly to the form.
4.  **Submit:** Click the **Submit** button.

> **What Happens Next?**
> The system will automatically create a new entry in the **MPR Tracker** and send it for approval. You will receive an email and a Teams message once a final decision (Approved or Rejected) has been made.

### How to Track Your Requisition's Status
You can view the real-time status of all your requisitions in the [MPR Tracker SharePoint List](https://algurguae.sharepoint.com/sites/IntegratedHRRecruitmentTracker/Lists/MPR%20Tracker/AllItems.aspx). The **Status** column will tell you exactly where it is in the process (e.g., "In VP Approval", "CV Sourcing", "Interview Scheduling").

---

## 2. Guide for Approvers (VP / EVP)

Your role is to provide strategic approval for new positions. You can do this from either Microsoft Teams or your email.

### How to Approve or Reject a Request

1.  **Receive Notification:** You will receive a notification in two places:
    *   An email with the subject "New MPR Approval Request..."
    *   A message from the "Approvals" app in Microsoft Teams.

    `[Screenshot placeholder: The approval card as it appears in Microsoft Teams]`

2.  **Review Details:** The notification will contain all the key details of the requisition. You can click the link to the SharePoint item to view the full request and any attachments.
3.  **Make a Decision:**
    *   Click **Approve** to authorize the position.
    *   Click **Reject** to deny the request.
4.  **Add Comments (Required for Rejection):** You can add comments to provide context for your decision. Comments are mandatory if you reject a request.
5.  **Submit:** Confirm your decision. The system will automatically record your response and move the process to the next step.

---

## 3. Guide for the HR Manager

Your primary interaction with the system is to assign approved requisitions to your team of recruiters.

### How to Assign a New Requisition

1.  **Receive Notification:** When an MPR is fully approved, you will receive an interactive "Adaptive Card" in a private chat with the Flow bot in Microsoft Teams.

    `[Screenshot placeholder: The HR Manager's assignment card in Teams]`

2.  **Review the Request:** The card will display the key details of the approved MPR.
3.  **Assign a Recruiter:** From the dropdown menu on the card, select the **HR Representative** you wish to assign to this requisition.
4.  **Submit:** Click the **Assign Representative** button.

> **What Happens Next?**
> The system will automatically update the MPR's status to **"CV Sourcing"**, assign the selected recruiter in SharePoint, and send a notification to them to begin work.

---

## 4. Guide for the HR Representative

You are the primary user of the system, managing the candidate pipeline from sourcing to final selection.

### Managing the Candidate Tracker
Your main workspace is the [Candidate Tracker SharePoint List](https://algurguae.sharepoint.com/sites/IntegratedHRRecruitmentTracker/Lists/Candidate%20Tracker/AllItems.aspx).

1.  **Adding a Candidate:** When you find a suitable candidate, click **+ New** to create a new item. Fill in the candidate's name and contact details, and be sure to select the correct parent **Requisition ID**. The system will automatically generate a unique **Candidate ID** for you.
2.  **Tracking Status:** The **Status** column shows the candidate's current position in the funnel (e.g., "Shortlisted", "Interview Process Ongoing"). This field is mostly updated automatically by the system.

### **Critical Task: Using the "Next Action (Trigger)" Field**

This dropdown field is how you command the automation to perform tasks for you. **After the system completes your requested action, it will automatically reset this field to "Waiting for Input."** This is your signal that the system is ready for its next command.

| When you want to...                | You must first fill in...                                   | Then, select this "Next Action"... | What the system will do for you                                                              |
| :--------------------------------- | :---------------------------------------------------------- | :--------------------------------- | :------------------------------------------------------------------------------------------- |
| **Schedule an interview**          | `NextInterviewTitle`, `NextInterviewDate`, `InterviewPanel` | **Schedule Next Interview**        | Creates calendar invites for the panel and logs the interview in the `Interview Tracker`.      |
| **Request approval for an offer**  | Attach the offer letter PDF to the candidate's list item.   | **Request Offer Approval**         | Starts a formal approval process with the VP/EVP for the attached offer letter.            |
| **(Other future actions)...**      | *(Relevant fields)*                                         | *(New action)*                     | *(New automated process)*                                                                    |

> **IMPORTANT:** Always fill in the required data fields *before* selecting an action from the "Next Action (Trigger)" dropdown. Forgetting to do so may cause the automation to fail.

---

## 5. Guide for Interviewers

Your role is to provide timely and structured feedback after interviewing a candidate.

### How to Submit Interview Feedback

1.  **Receive Calendar Invite:** You will receive a standard calendar invitation for the interview.
2.  **Receive Feedback Request:** On the day of the interview, the system will automatically send you an email with the subject "Action Required: Feedback for interview with..."
3.  **Open the Form:** Click the unique link in the email. This will take you to a pre-filled "Interview Feedback Form."
4.  **Provide Feedback:** Complete the form with your detailed assessment and select a **Recommendation** (e.g., "Recommend to Proceed").
5.  **Submit:** Click **Submit**. Your feedback is now captured and sent to the HR Representative.

---

## 6. Troubleshooting & Frequently Asked Questions (FAQ)

**Q: I submitted a request/action, but nothing has happened yet.**
**A:** Please allow 1-2 minutes for the system to process. Power Automate flows are fast, but not always instantaneous. If more than 5 minutes have passed, please contact the System Administrator.

**Q: The approval for my requisition was sent to the wrong VP.**
**A:** The approvers are stored in a central `Configuration` list. Please contact the System Administrator to have the list corrected. This is an administrative change and does not require editing the automation itself.

**Q: I selected an action from the "Next Action (Trigger)" dropdown, but the flow failed.**
**A:** The most common reason is that a required field was not filled out first (e.g., you selected "Schedule Next Interview" but did not add anyone to the `InterviewPanel` field). Please ensure all data is present and try again. If it continues to fail, take a screenshot and contact the System Administrator.

**Q: The system says a candidate's status is "Rejected," but I want to reconsider them.**
**A:** To maintain data integrity, the system does not allow reopening a rejected candidate's journey. It is better to create a new entry for the candidate and add a note referencing the previous application.

**Q: A flow run has failed, what should I do?**
**A:** Please do not attempt to re-run the flow yourself. Contact the **System Administrator** with the **Requisition ID** or **Candidate ID**, the approximate time of the failure, and a screenshot if possible. They can investigate the flow run history and resolve the issue.