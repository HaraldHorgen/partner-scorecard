# ChannelPRO™ — User Guide

**Partner Revenue Optimizer**
Version 4 — Multi-Tenant

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Client Intake](#2-client-intake)
3. [Step 1 — Scoring Criteria](#3-step-1--scoring-criteria)
4. [Step 2 — Score a Partner](#4-step-2--score-a-partner)
5. [Step 3 — Partner Assessment](#5-step-3--partner-assessment)
6. [Step 4 — Partner Classification](#6-step-4--partner-classification)
7. [Import Data](#7-import-data)
8. [Partner List](#8-partner-list)
9. [Ask ChannelPRO™ (AI Assistant)](#9-ask-channelpro-ai-assistant)
10. [Break-even — Program Costs](#10-break-even--program-costs)
11. [Break-even — Detailed Analysis](#11-break-even--detailed-analysis)
12. [Revenue Recovery](#12-revenue-recovery)
13. [Administration](#13-administration)
14. [Scoring Reference](#14-scoring-reference)
15. [FAQ & Troubleshooting](#15-faq--troubleshooting)

---

## 1. Getting Started

### Logging In

Open the ChannelPRO™ URL in your browser. You will see the login screen with the York Group logo.

| Field    | Default Value   |
|----------|-----------------|
| Username | `admin`         |
| Password | `admin`         |

> **Important:** Change the default admin password immediately after your first login via **Admin — Manage Users**.

After signing in you will see the sidebar with navigation tabs on the left and the main content area on the right.

### User Roles

| Role   | Access                                                                 |
|--------|------------------------------------------------------------------------|
| Admin  | All pages, all clients, user management, tenant switching              |
| Client | All scoring/analysis pages scoped to their assigned client (tenant)    |

### Recommended Workflow

Follow the steps in order for the best experience:

```
Client Intake → Step 1 (Criteria) → Step 2 (Score) → Step 3 (Assess) → Step 4 (Classify)
```

You can also bulk-import partner data via **Import Data** at any point after Step 1.

### Sidebar Navigation

The sidebar contains:

- **Logo & branding** at the top
- **Your name and role** badge
- **Active Client** selector (admin only — switch between tenants)
- **Page navigation** radio buttons
- **Category filter** (filters visible metrics on Steps 1 & 2)
- **Partners Scored** section showing a clickable partner list with grades
- **Sign Out** button

---

## 2. Client Intake

**Purpose:** Capture your company profile so ChannelPRO™ can personalize the scoring experience.

### What to Enter

**Contact Information**
- Client company name, website URL, phone
- Primary project manager name and email
- City and country
- Company logo URL (optional — displayed in the header)

**Business Profile**
- Company size (employee count range)
- Industry verticals served (select all that apply)
- Solution delivery model (On-premise, SaaS/PaaS, IaaS/VM, Device)

**Target Customers**
- Target company size range
- Average first-year transaction value

**Channel Information**
- Services as a percentage of license/subscription revenue
- Number of resellers / channel partners
- Percentage of revenues from indirect channels
- Discount tiers offered to partners
- Partner designations (e.g., `Gold, Silver, Bronze`) — these become the **Tier** options in Step 2

### Saving

Click **Next → Step 1** to save and proceed, or revisit this page later to update.

---

## 3. Step 1 — Scoring Criteria

**Purpose:** Define how partner performance is measured. Configure the 1–5 scoring thresholds for each of the 29 metrics.

### The 29 Metrics

Metrics are organized into six categories:

| Category               | Metrics                                                              |
|------------------------|----------------------------------------------------------------------|
| Revenue & Growth       | Annual revenues, YoY growth, Net-new logo revenues, % SaaS, Net expansion, Total revenues |
| Sales Performance      | Deal size (new & renewals), Time to close, Registered deals, Win/loss ratio, Partner opps %, Frequency |
| Retention & Satisfaction | Renewal rate, Customer satisfaction, Communication with vendor      |
| Enablement & Support   | MDF utilization, Sales org quality, Certifications, Sales support calls, Tech support calls |
| Strategic Fit          | Dedication vs competitors, Dedication vs other vendors, Geo coverage, Vertical coverage |
| Risk & Governance      | Management quality, Known litigation, Export control & IP, Financial strength |

Use the **category filter** in the sidebar to focus on one group at a time.

### Metric Types

- **Quantitative** (18 metrics) — Scored by numeric ranges. Enter the Min and Max values for each score level (1–5). Example: Annual revenues of $0–$50K = score 1, $750K+ = score 5.
- **Qualitative** (11 metrics) — Scored by descriptive text. Edit the descriptor for each level. Example: Communication score 1 = "Unresponsive — hard to reach", score 5 = "Exemplary — weekly touchpoints, exec visits".

### Enabling / Disabling Metrics

Each metric has an **Include in scoring** checkbox. Uncheck it to exclude a metric from all partner scorecards. Disabled metrics appear greyed out with an "EXCLUDED" badge.

### Auto-Calculate from Partner Data

If you have already imported partner data (see [Import Data](#7-import-data)), an **Auto-Calculate** section appears at the bottom:

1. Click **Recalculate Benchmarks**
2. ChannelPRO™ analyzes all partner raw values using quintile analysis
3. Scoring ranges are automatically adjusted to reflect your actual partner distribution
4. All partners are re-scored with the new ranges

### Saving

- **Save Criteria** — saves your changes (white button)
- **Next → Step 2** — saves and navigates forward (red button)

> All changes apply retroactively — existing partners are immediately re-scored.

---

## 4. Step 2 — Score a Partner

**Purpose:** Enter partner details and score each metric. Scores are calculated in real time as you fill in values.

### Partner Details

Fill in the top section:

| Field             | Notes                                        |
|-------------------|----------------------------------------------|
| Partner name      | Required. Must be unique.                    |
| Year              | Year the partnership began                   |
| Tier              | Dropdown populated from Client Intake tiers  |
| Partner Discount  | e.g., "20%"                                  |
| City / Country    | Partner location                             |
| PAM Name / Email  | Partner Account Manager contact              |

### Scoring Metrics

For each enabled metric:

- **Quantitative metrics** — Enter a numeric value (e.g., `250000` for revenue). The score (1–5) is calculated automatically based on your Step 1 ranges and displayed as a colored badge on the right.
- **Qualitative metrics** — Select a descriptor from the dropdown. The corresponding score appears on the right.

**Hint rows** below each metric show the scoring ranges for quick reference.

### Live Summary

Four summary cards update in real time as you score:

| Card         | Shows                                  |
|--------------|----------------------------------------|
| Total        | Sum of all metric scores               |
| Scored       | How many metrics have been scored      |
| Score %      | Total as a percentage of max possible  |
| Grade        | Letter grade (A through D)             |

### Submitting

- **New partner:** Click **Submit & Start New Partner**. The form clears for the next partner.
- **Editing:** When you open an existing partner (from Step 3, Partner List, or the sidebar), the form loads their data. Click **Save Changes** to update, or **Cancel Edit** to discard.

---

## 5. Step 3 — Partner Assessment

**Purpose:** View all scored partners in an interactive heatmap table. Filter, sort, compare, and export.

### The Assessment Table

The table displays every partner with their metric scores in a color-coded grid:

| Score | Color        | Meaning       |
|-------|-------------|---------------|
| 1     | Soft red    | Poor          |
| 2     | Soft amber  | Below average |
| 3     | Soft gold   | Average       |
| 4     | Soft green  | Good          |
| 5     | Clear green | Excellent     |
| —     | Grey        | Not scored    |

**Key features:**

- **Column groups** — Metrics are grouped under their category headers (Revenue & Growth, Sales Performance, etc.)
- **Pinned columns** — Partner name stays on the left; Total, Score %, and Grade stay on the right while you scroll horizontally
- **Sorting** — Click any column header to sort ascending/descending
- **Filtering** — Use the filter row below headers to type-to-filter or use dropdown filters
- **Row selection** — Click a row to select a partner, then click **Open Scorecard** to edit

### Opening a Partner Scorecard

Two ways to jump to Step 2 for editing:

1. Click a row in the table, then click **Open Scorecard**
2. Use the **Select a partner** dropdown below the table

### Downloads

| Button           | Format                                           |
|------------------|--------------------------------------------------|
| Download Excel   | `.xlsx` with colored heatmap cells               |
| Download CSV     | Plain `.csv` for use in other tools              |

---

## 6. Step 4 — Partner Classification

**Purpose:** Classify partners into strategic quadrants based on configurable criteria.

### The Four Quadrants

| Quadrant | Name                        | Default Criteria                              |
|----------|-----------------------------|-----------------------------------------------|
| Q1       | Strategic / Underperforming | High total revenue, low vendor revenue & growth |
| Q2       | Top Performers              | High revenue, high growth, high new logos      |
| Q3       | Growth Potential             | High revenue, low growth, mid new logos        |
| Q4       | Long Tail                   | Does not match Q1–Q3 (auto-assigned)          |

### Configuring Criteria

For Q1, Q2, and Q3, you can set up to **6 criteria** each. Each criterion is a metric + level combination:

| Level | Meaning              |
|-------|----------------------|
| High  | Score of 4 or 5      |
| Mid   | Score of exactly 3   |
| Low   | Score of 1 or 2      |
| Any   | Any score above 0    |

**First match wins** — partners are tested against Q1 first, then Q2, then Q3. The first quadrant whose criteria are all satisfied claims the partner. Unmatched partners go to Q4.

Click **Save & Classify** to apply.

### Results

After classification:

- **Quadrant summary cards** — show the count and member list for each quadrant
- **Full Classification Table** — lists every partner with their quadrant, total score, and percentage

### Downloads

| Button         | Format                                          |
|----------------|-------------------------------------------------|
| Download Excel | `.xlsx` with quadrant-colored rows              |
| Download CSV   | Plain `.csv`                                    |
| Download JSON  | Raw `{partner: quadrant}` mapping               |

---

## 7. Import Data

**Purpose:** Bulk-import partners from a CSV file exported from your CRM, ERP, or PRM system.

### Step-by-Step

**1. Upload your CSV**

Click the file uploader and select a `.csv` file. A preview of the first 5 rows appears.

**2. Map the Partner Name column**

Select which CSV column contains the partner/company name. This field is **required**.

**3. Map Partner Details**

Map optional columns like Year, Tier, Discount, City, Country, PAM Name, and PAM Email. ChannelPRO™ auto-matches common column names.

**4. Map Scoring Metrics**

For each enabled metric, select the corresponding CSV column. Auto-matching finds likely matches. **Unmapped fields** are highlighted with a red bar underneath.

- **Quantitative metrics:** Raw values from CSV are automatically scored using your Step 1 ranges.
- **Qualitative metrics:** Values must match one of your Step 1 descriptors exactly to auto-score.
- **Unmapped metrics** are left blank for manual scoring later.

**5. Review the mapping summary**

The summary shows how many metrics are mapped. Warning banners highlight any unmapped fields.

**6. Click Import Partners**

A progress bar shows the import status. For each row:
- If the partner name already exists, the partner is **updated**
- If the partner name is new, the partner is **created**

### After Import

- A results panel shows Created / Updated / Error counts
- An imported data preview table shows each partner with their raw values and computed scores
- If errors occurred, you can download an error report CSV

### Recalculate Benchmarks

After importing, expand **Recalculate Scoring Benchmarks** to auto-adjust your Step 1 ranges based on the actual distribution of partner data.

---

## 8. Partner List

**Purpose:** Quick-access view of all partners with inline editing and manual partner creation.

### Viewing Partners

A summary table shows: Partner, Tier, PAM, City, Total Score, Percentage, and Grade. Partners are sorted by total score (highest first).

### Editing a Partner

1. Select a partner from the dropdown
2. Click **Edit Scorecard**
3. Update details or metric scores in the inline form
4. Click **Save Changes**

### Adding a Partner Manually

1. Expand **Add New Partner**
2. Fill in the partner name (required) and optional details
3. Click **Add Partner**
4. The partner is created with blank metric scores — go to Step 2 to score them

### Deleting a Partner

Select a partner and click **Delete Partner**. A confirmation dialog appears.

> You can also delete partners from the sidebar's **Partners Scored** section using the trash icon next to each name.

---

## 9. Ask ChannelPRO™ (AI Assistant)

**Purpose:** Ask natural-language questions about your partner data. Powered by Anthropic's Claude AI.

### Requirements

An **Anthropic API key** is required. Set it in one of two ways:
- **Recommended:** Set `ANTHROPIC_API_KEY` in your Render environment variables
- **Fallback:** Paste it into the text field that appears on the page

### What You Can Ask

| Type of question         | Example                                                                  |
|--------------------------|--------------------------------------------------------------------------|
| Filtering & search       | "Which partners have MDF utilization below 40%?"                        |
| Multi-criteria analysis  | "Show me partners with both a low close rate and long sales cycle"      |
| Comparison               | "Compare the top 5 partners by revenue vs their customer satisfaction"  |
| Score updates            | "Set Partner X's renewal rate score to 4"                                |
| Recommendations          | "Which partners should we invest more in?"                               |

### Response Types

The AI can respond with:
- **Text answers** — analysis, recommendations, explanations
- **Data tables** — filtered/sorted partner data
- **Charts** — bar charts, pie charts, horizontal bar charts
- **Score updates** — proposed changes with a confirmation dialog

### Confirming Score Updates

When the AI suggests score changes, a confirmation panel appears showing each proposed change (partner, metric, new score, reason). Click **Apply Updates** to save or **Cancel** to discard.

### Conversation History

The chat is **multi-turn** — ask follow-up questions to refine results. Click **Clear chat** to start a fresh conversation.

---

## 10. Break-even — Program Costs

**Purpose:** Calculate your total partner program costs and the break-even cost per partner.

### Entering Costs

Costs are organized into predefined sections:

| Section                          | Example Items                                     |
|----------------------------------|---------------------------------------------------|
| Personnel and Overhead           | Partner manager salaries, social charges, office   |
| Infrastructure and Technology    | PRM software, integrations, security               |
| Marketing and Promotion          | Co-marketing, MDF, SEO, events                     |
| Technical and Sales Support      | Technical support, pre-sales, social charges        |
| Training and Certification       | Product training, sales training, cert programs     |
| Legal and Compliance             | Contracts, compliance, dispute resolution           |
| Travel and Meetings              | Face-to-face meetings, joint sales calls            |
| Performance Metrics & Reporting  | Performance tools, reporting                        |
| Scaling and Expansion            | Recruitment, onboarding, marketing                  |

Enter the annual dollar amount for each cost item. You can also **add custom cost categories** using the expander at the top.

### Program Parameters

| Parameter                | Purpose                                      |
|--------------------------|----------------------------------------------|
| Number of partners       | Used to calculate break-even per partner     |
| Support calls (annual)   | Total inbound support calls across all partners |
| Avg minutes per call     | Average duration for cost-per-minute calculation |

### Results Dashboard

After saving, a summary dashboard shows:

- **Total Program Costs** — sum of all cost items
- **Break-even per Partner** — total costs divided by number of partners
- **Support Cost Metrics** — cost per call and cost per minute

A breakdown table shows each cost section's dollar amount and percentage of total.

---

## 11. Break-even — Detailed Analysis

**Purpose:** Upload per-partner cost data (revenue, support calls) for granular cost-vs-revenue analysis.

### CSV Requirements

Your CSV must contain these columns (names are auto-matched):

| Column       | Required | Description                           |
|--------------|----------|---------------------------------------|
| Partner      | Yes      | Partner company name                  |
| Revenues     | Yes      | Annual revenue from this partner      |
| # of calls   | Yes      | Number of support calls received      |
| Time spent   | No       | Total minutes spent on support        |

If **Time spent** is missing, ChannelPRO™ estimates it using: `calls x avg minutes per call`.

### Analysis Output

**Metrics row:** Cost per minute, cost per call, average minutes per call.

**Partner cost table** with columns:
- Partner name, Revenues, % of total revenues
- Number of calls, % of total calls
- Time spent, % of total support time
- Support cost, % of total cost

**Visualizations** (three tabs):
1. **Support Cost vs Revenue** — grouped bar chart (top 15 partners)
2. **Cost Distribution** — donut charts showing support cost and revenue distribution
3. **Cost / Revenue Ratio** — color-coded bar chart identifying partners whose support costs are disproportionately high relative to revenue

### Downloads

Export the full analysis as CSV or formatted Excel.

---

## 12. Revenue Recovery

**Purpose:** Identify non-performing "Long Tail" partners and calculate how much margin you could recapture by adjusting their discount rates.

### How It Works

1. Set a **Net-New Logo Revenue threshold** (default: $50,000). Partners with net-new revenue below this threshold are flagged as non-performing.
2. Set a **Proposed baseline margin** (default: 10%). This is the reduced margin rate you would apply to non-performing partners.
3. ChannelPRO™ compares each flagged partner's current margin cost against the proposed margin cost and calculates the **recapture opportunity**.

### Reading the Results

**Summary cards** show:
- Number of non-performing partners
- Current total margin cost for those partners
- Proposed total margin cost at the baseline rate
- **Total potential recapture** — the savings opportunity

**Detail table** lists every flagged partner with:
- Annual revenue and current margin %
- Current margin cost (in dollars)
- Proposed margin % and cost
- Recapture amount (current minus proposed)
- Net-new logo revenue (showing why they were flagged)

### Download

Click **Download Report (CSV)** to export the full detail table.

---

## 13. Administration

### Manage Users

**Admin — Manage Users** lets you:

- **View all users** with their roles and tenant assignments
- **Change passwords** for any user
- **Delete users** (except the default admin)
- **Create new users** — specify username, display name, password, role, and tenant ID
- **Set partner limits** per tenant (e.g., max 50 partners for a trial account; 0 = unlimited)

### All Clients Overview

**Admin — All Clients** provides a bird's-eye view:

- **Summary dashboard** — total clients, total partners, criteria completion rate
- **Break-even overview** — aggregated program costs across all clients
- **Per-client detail** — expandable cards showing:
  - Contact information
  - Partner table with scores and grades
  - Break-even metrics (if configured)
  - Individual CSV download
- **Cross-client Excel export** — one workbook with a sheet per client

The **currently active** client is highlighted with an ACTIVE badge and auto-expanded.

### Switching Clients

Admins can switch between clients using the **Active Client** dropdown in the sidebar. Switching clients reloads all data (criteria, partners, configuration) for the selected tenant.

---

## 14. Scoring Reference

### Grade Scale

| Grade | Score %  | Color  |
|-------|----------|--------|
| A     | 90–100%  | Green  |
| B+    | 80–89%   | Green  |
| B     | 70–79%   | Green  |
| C+    | 60–69%   | Gold   |
| C     | 50–59%   | Orange |
| D     | 0–49%    | Red    |

### Score Colors (Assessment Table)

| Score | Background   | Meaning       |
|-------|-------------|---------------|
| 1     | Soft red    | Critical      |
| 2     | Soft amber  | Below average |
| 3     | Soft gold   | Average       |
| 4     | Soft green  | Good          |
| 5     | Clear green | Excellent     |

### Classification Levels

| Level | Score Range | Used In       |
|-------|------------|---------------|
| High  | 4 or 5     | Q1–Q3 criteria |
| Mid   | 3          | Q1–Q3 criteria |
| Low   | 1 or 2     | Q1–Q3 criteria |
| Any   | 1–5        | Q1–Q3 criteria |

---

## 15. FAQ & Troubleshooting

**Q: I changed the scoring criteria but my partners still have old scores.**
A: Scores update automatically when you save criteria. If something looks off, go to Step 1 and click **Save Criteria** again — all partners will be re-scored.

**Q: How do I delete all partners and start fresh?**
A: In the sidebar, expand **Partners Scored**, scroll to the bottom, and click **Delete All Partners**. Confirm when prompted.

**Q: Can I import data from Excel?**
A: Save your Excel file as CSV first (File → Save As → CSV), then use **Import Data**.

**Q: The AI assistant asks for an API key.**
A: Set the `ANTHROPIC_API_KEY` environment variable in your Render dashboard, then redeploy the service. Alternatively, paste the key directly into the text field for the current session.

**Q: What happens if I import a partner that already exists?**
A: The existing partner is **updated** with the new data. Existing scores for unmapped metrics are preserved.

**Q: How is the break-even per partner calculated?**
A: Total Program Costs (from all cost sections) divided by the Number of Partners you entered.

**Q: Can two partners have the same name?**
A: No. Partner names must be unique. The import process uses the name as the matching key for updates.

**Q: What does "Long Tail" mean in classification?**
A: Partners that don't match any of the Q1–Q3 criteria are automatically placed in Q4 (Long Tail). These are typically partners with lower scores across the board.

---

*ChannelPRO™ is a product of York Group. For support, contact your account representative.*
