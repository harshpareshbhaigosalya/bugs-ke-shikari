# 💰 Expense Management System

### 🧠 With Machine Learning Expense Prediction

---

## 🚀 Overview

Managing company expenses manually is time-consuming, error-prone, and lacks transparency. Our project automates the **expense reimbursement and approval process** while integrating **Machine Learning** to **predict next month’s total expenses** based on past data.

---

## 🧩 Problem Statement

Companies often face difficulties in:

* Defining and managing **multi-level approval flows**.
* Handling **manual reimbursements** prone to human error.
* Maintaining **transparent records** of submitted and approved expenses.
* Estimating **future financial expenditures** for planning.

Our system solves all of these through automation, smart approvals, and ML-based forecasting.

---

## ⚙️ Core Features

### 🔐 Authentication & User Management

* On signup, a **Company** (with country-based currency) and **Admin** user are automatically created.
* The **Admin** can:

  * Create **Employees** and **Managers**.
  * Assign or modify user roles.
  * Define **managerial relationships** for workflow.

---

### 🧾 Expense Submission (Employee Role)

Employees can:

* Submit expense claims with details like amount, category, description, and date.
* Submit in different currencies — automatically converted to company currency.
* View their **expense history** (Approved / Rejected / Pending).

---

### 👨‍💼 Approval Workflow (Manager/Admin Role)

* Multi-level approval support (Manager → Finance → Director).
* Expense moves stepwise — each approver approves or rejects before the next sees it.
* Managers can:

  * View pending approvals.
  * Approve/Reject with comments.

---

### ⚖️ Conditional Approval Flow

Supports flexible rules:

* **Percentage rule** – e.g., if 60% of approvers approve → Expense is approved.
* **Specific approver rule** – e.g., CFO approval auto-approves expense.
* **Hybrid rule** – Combine both rules for complex approval needs.

---

### 🔍 OCR-Based Receipt Scanning

* Employees can upload a **receipt image**.
* The system uses **OCR** (Optical Character Recognition) to automatically extract details:

  * Amount
  * Date
  * Description
  * Vendor name
  * Category

---

## 🤖 Machine Learning Feature — Expense Prediction

We integrated an **ML model** that predicts **next month’s total expense** for each company or employee.

### 📊 Model Highlights

* Trained using historical expense data.
* Features considered:

  * Expense category trends.
  * Average monthly spend.
  * Currency conversion rates.
  * Time-series forecasting.
* Outputs:

  * Predicted total expense for the next month.
  * Category-wise forecast.

This allows **budget planning** and **decision-making** before the next financial cycle.

---

## 🧠 Tech Stack

**Frontend:** React.js / HTML / CSS
**Backend:** Node.js / Express.js
**Database:** MongoDB
**ML Model:** Python (Pandas, Scikit-learn, NumPy, Matplotlib)
**APIs:** REST API Integration for currencies & OCR
**Version Control:** Git + GitHub

---

## 👥 Roles & Permissions

| Role         | Permissions                                                                 |
| ------------ | --------------------------------------------------------------------------- |
| **Admin**    | Create company, manage users & roles, view all expenses, override approvals |
| **Manager**  | Approve/Reject team expenses, escalate, view team expenses                  |
| **Employee** | Submit expenses, view expense history, check approval status                |

---

## 🧾 Future Enhancements

* Integration with payment gateways for direct reimbursements.
* Expense analytics dashboard with insights and ML visualizations.
* Automated alerts for expense overspending.

---

Would you like me to make this **GitHub-ready (formatted with badges, emoji headers, and markdown sections)** — or keep it **simple and minimal for quick upload**?
