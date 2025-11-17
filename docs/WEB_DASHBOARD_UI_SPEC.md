# Web Dashboard UI/UX Specification
## Distributed Compute Marketplace

**Version:** 1.0
**Last Updated:** 2025-11-17
**Designer:** AI Assistant
**Target Users:** Technical users, researchers, developers

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Color Palette & Typography](#color-palette--typography)
4. [Screen-by-Screen Breakdown](#screen-by-screen-breakdown)
5. [Component Library](#component-library)
6. [User Flows](#user-flows)
7. [Responsive Design](#responsive-design)
8. [Accessibility](#accessibility)

---

## Overview

### Purpose
A modern, intuitive web dashboard for managing distributed compute jobs, monitoring cluster resources, and tracking credit usage.

### Tech Stack Recommendation
- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS + shadcn/ui components
- **State Management:** Zustand or React Query
- **Charts:** Recharts or Chart.js
- **Real-time:** WebSocket connection for live updates
- **Routing:** React Router v6

### Key Features
- Real-time job monitoring
- Interactive node map/cluster visualization
- Drag-and-drop job submission
- Credit usage analytics
- Mobile-responsive design

---

## Design Principles

### 1. **Clarity Over Complexity**
- Show most important information first
- Hide advanced options behind "Advanced" toggles
- Use progressive disclosure

### 2. **Speed & Responsiveness**
- Sub-200ms page loads
- Optimistic UI updates
- Skeleton loaders for async data

### 3. **Visual Hierarchy**
- Use size, color, spacing to guide attention
- Primary actions are prominent (large, colorful buttons)
- Secondary actions are subtle (text links, ghost buttons)

### 4. **Feedback & Status**
- Always show loading states
- Clear success/error messages
- Real-time status indicators

---

## Color Palette & Typography

### Colors

**Primary Palette:**
```css
--primary-50:  #eff6ff   /* Lightest blue - backgrounds */
--primary-100: #dbeafe   /* Light blue - hover states */
--primary-500: #3b82f6   /* Main blue - primary buttons */
--primary-600: #2563eb   /* Dark blue - button hover */
--primary-900: #1e3a8a   /* Darkest blue - text */
```

**Status Colors:**
```css
--success: #10b981   /* Green - completed jobs */
--warning: #f59e0b   /* Amber - pending jobs */
--error: #ef4444     /* Red - failed jobs */
--info: #06b6d4      /* Cyan - running jobs */
--neutral: #6b7280   /* Gray - idle states */
```

**Background:**
```css
--bg-primary: #ffffff     /* White - main background */
--bg-secondary: #f9fafb   /* Light gray - cards */
--bg-tertiary: #f3f4f6    /* Lighter gray - hover */
--bg-dark: #111827        /* Dark mode background */
```

### Typography

**Font Family:**
- **UI Text:** Inter, system-ui, sans-serif
- **Monospace:** 'JetBrains Mono', 'Fira Code', monospace (for code/IDs)

**Font Sizes:**
```css
--text-xs: 0.75rem    /* 12px - labels, captions */
--text-sm: 0.875rem   /* 14px - body text */
--text-base: 1rem     /* 16px - default */
--text-lg: 1.125rem   /* 18px - section headers */
--text-xl: 1.25rem    /* 20px - card titles */
--text-2xl: 1.5rem    /* 24px - page titles */
--text-3xl: 1.875rem  /* 30px - hero text */
```

---

## Screen-by-Screen Breakdown

### Screen 1: Login/Landing Page

#### Layout
```
┌─────────────────────────────────────────────────────────┐
│                    NAVBAR (Transparent)                 │
│  Logo                              [Login] [Sign Up]    │
└─────────────────────────────────────────────────────────┘
│                                                           │
│              ╔═══════════════════════════╗               │
│              ║   HERO SECTION            ║               │
│              ║                           ║               │
│              ║   Share Computing Power   ║  (text-3xl)   │
│              ║   Among Friends           ║  (text-3xl)   │
│              ║                           ║               │
│              ║   Distributed compute     ║  (text-lg)    │
│              ║   marketplace for teams   ║  (text-lg)    │
│              ║                           ║               │
│              ║   [Get Started →]         ║  (primary btn)│
│              ║   [View Demo]             ║  (ghost btn)  │
│              ╚═══════════════════════════╝               │
│                                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Icon 1  │  │ Icon 2  │  │ Icon 3  │  │ Icon 4  │    │
│  │Fast     │  │Secure   │  │Scalable │  │Fair     │    │
│  │4x Speed │  │Isolated │  │Auto-    │  │Credit   │    │
│  │         │  │Sandbox  │  │Scale    │  │System   │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│                                                           │
│              Live Marketplace Stats                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ 52 Nodes     │ │ 416 Cores    │ │ 1.2K Jobs    │    │
│  │ Online       │ │ Available    │ │ Today        │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                           │
│                    FOOTER                                 │
└───────────────────────────────────────────────────────────┘
```

#### Details

**Hero Section:**
- **Background:** Gradient from primary-50 to primary-100
- **Animation:** Subtle floating particles (representing distributed nodes)
- **CTA Button:** Large (h-14), rounded-lg, shadow-lg, hover:scale-105 transition

**Stats Cards:**
- **Size:** w-48, h-32
- **Background:** White with subtle shadow
- **Number:** text-3xl, font-bold, primary-600
- **Label:** text-sm, text-gray-600
- **Icon:** Top-right corner, 24x24px, primary-300

**Features Section:**
- **Icons:** 48x48px, primary-500 color
- **Title:** text-xl, font-semibold
- **Description:** text-sm, text-gray-600, 2-3 lines max

---

### Screen 2: Dashboard Home (Authenticated)

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR (240px)   │           MAIN CONTENT AREA                │
│                    │                                             │
│  Logo              │  ┌───────────────────────────────────────┐ │
│                    │  │ Welcome back, Alice! 👋               │ │
│  ┌──────────────┐  │  │ Credit Balance: 1,245 credits         │ │
│  │ Dashboard    │  │  └───────────────────────────────────────┘ │
│  │ (active)     │  │                                             │
│  └──────────────┘  │  Quick Actions:                             │
│  │ Jobs         │  │  [Submit Job] [Browse Nodes] [Buy Credits] │
│  │ Nodes        │  │                                             │
│  │ Marketplace  │  │  ┌──── Job Status ────┐ ┌── Cluster ───┐  │
│  │ Credits      │  │  │ ┌─────────────────┐│ │  Node Map     │  │
│  │ Analytics    │  │  │ │ Active: 3       ││ │  [Map Visual] │  │
│  │ Settings     │  │  │ │ Pending: 1      ││ │  52 nodes     │  │
│  ├──────────────┤  │  │ │ Completed: 145  ││ │  Online       │  │
│  │ [+ New Job]  │  │  │ │ Failed: 2       ││ │               │  │
│  │              │  │  │ └─────────────────┘│ └───────────────┘  │
│  │ User: Alice  │  │  └─────────────────────┘                   │
│  │ [Logout]     │  │                                             │
│  └──────────────┘  │  Recent Jobs:                               │
│                    │  ┌─────────────────────────────────────────┐│
│                    │  │ ID  │ Name       │ Status  │ Progress   ││
│                    │  ├─────┼────────────┼─────────┼────────────┤│
│                    │  │ 123 │ Pi Est.    │Running  │ ████░ 80%  ││
│                    │  │ 122 │ Data Proc  │Complete │ █████ 100% ││
│                    │  │ 121 │ ML Train   │Running  │ ██░░░ 40%  ││
│                    │  └─────────────────────────────────────────┘│
│                    │                                             │
│                    │  Credit Usage (Last 30 Days):               │
│                    │  [Line Chart: credits over time]            │
│                    │                                             │
└─────────────────────────────────────────────────────────────────┘
```

#### Component Details

**Sidebar:**
- **Width:** 240px fixed
- **Background:** bg-secondary (light gray)
- **Active State:** primary-500 left border (4px), bg-primary-50
- **Hover State:** bg-tertiary
- **Logo:** 32x32px + "Compute Market" text
- **User Section:** At bottom, shows avatar + name + balance

**Welcome Card:**
- **Height:** 80px
- **Background:** Gradient primary-500 to primary-600
- **Text Color:** White
- **Credits:** Large text (text-2xl), font-bold
- **Emoji:** Adds friendly touch

**Quick Actions:**
- **Buttons:** Horizontal row, equal width
- **Primary Action:** "Submit Job" - primary color, larger
- **Secondary Actions:** Outlined buttons

**Job Status Card:**
- **Size:** 300px x 200px
- **Background:** White, shadow-md, rounded-lg
- **Status Items:** Icon + Number + Label
  - Active: Blue circle icon, info color
  - Pending: Yellow clock icon, warning color
  - Completed: Green checkmark, success color
  - Failed: Red X, error color

**Cluster Map:**
- **Size:** 400px x 200px
- **Visual:** Scatter plot of nodes
  - Online nodes: Green dots
  - Offline nodes: Gray dots
  - Node size indicates CPU cores
- **Interactive:** Hover shows node details tooltip

**Recent Jobs Table:**
- **Columns:** ID, Name, Status, Progress
- **Row Height:** 48px
- **Hover:** bg-tertiary
- **Progress Bar:** Colored based on status
  - Running: Blue animated gradient
  - Complete: Green solid
  - Failed: Red solid
- **Click:** Navigate to job detail page

**Credit Usage Chart:**
- **Type:** Line chart with area fill
- **X-axis:** Days (last 30)
- **Y-axis:** Credits spent
- **Color:** Primary gradient
- **Tooltip:** Shows exact amount on hover

---

### Screen 3: Job Submission Page

#### Layout
```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR  │  MAIN CONTENT                                │
│           │                                               │
│           │  Submit New Job                               │
│           │  ═══════════════                              │
│           │                                               │
│           │  Choose Template or Custom Job:               │
│           │  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│           │  │ Monte   │ │ Data    │ │ Custom  │        │
│           │  │ Carlo π │ │ Process │ │ Job     │        │
│           │  │         │ │         │ │         │        │
│           │  │ [Use]   │ │ [Use]   │ │ [Use]   │        │
│           │  └─────────┘ └─────────┘ └─────────┘        │
│           │                                               │
│           │  ┌─── Job Configuration ───────────────────┐ │
│           │  │                                          │ │
│           │  │ Docker Image: *                          │ │
│           │  │ ┌──────────────────────────────────────┐ │ │
│           │  │ │ python:3.11-slim              ▼     │ │ │
│           │  │ └──────────────────────────────────────┘ │ │
│           │  │                                          │ │
│           │  │ Resources per Chunk:                     │ │
│           │  │ CPU Cores: [2] ─────●────── (slider)     │ │
│           │  │ RAM (GB):  [4] ─────●────── (slider)     │ │
│           │  │                                          │ │
│           │  │ Parallelization:                         │ │
│           │  │ Total Chunks: [4] ──●────── (slider)     │ │
│           │  │                                          │ │
│           │  │ Advanced Options: [+ Show]               │ │
│           │  │                                          │ │
│           │  │ ┌─ Cost Estimate ──────────────────────┐│ │
│           │  │ │ Total Credits: 224 cr                ││ │
│           │  │ │ Est. Duration: 30 minutes            ││ │
│           │  │ │ Nodes Needed:  4 nodes               ││ │
│           │  │ └──────────────────────────────────────┘│ │
│           │  │                                          │ │
│           │  │ [Cancel]              [Submit Job →]     │ │
│           │  └──────────────────────────────────────────┘ │
│           │                                               │
└─────────────────────────────────────────────────────────┘
```

#### Details

**Template Cards:**
- **Size:** 200px x 180px each
- **Layout:** Grid, 3 columns
- **Hover:** Scale 1.05, shadow-lg
- **Content:**
  - Icon: 48x48px at top
  - Title: text-lg, font-semibold
  - Description: text-sm, 2 lines
  - "Use" button: primary color, full-width

**Configuration Form:**
- **Padding:** p-6
- **Field Spacing:** mb-4 between fields
- **Labels:** text-sm, font-medium, text-gray-700
- **Required Fields:** Red asterisk (*)

**Docker Image Dropdown:**
- **Height:** h-12
- **Border:** border-gray-300, rounded-md
- **Options:** Approved images only
  - python:3.11-slim
  - ubuntu:22.04
  - alpine:3.19
  - (custom input with validation)

**Sliders:**
- **Track:** bg-gray-200, h-2
- **Thumb:** bg-primary-500, w-4, h-4, rounded-full
- **Value Display:** Above slider, font-mono
- **Range Labels:** Left (min) and right (max)
- **Step Indicators:** Small dots on track

**Advanced Options (Collapsed):**
- Initially hidden
- Click "+ Show" to expand
- Contains:
  - Priority (1-10)
  - Sandbox Level (Trusted/Standard/Paranoid)
  - Encryption Key (optional)
  - Affinity Rules
  - Tags

**Cost Estimate Box:**
- **Background:** primary-50
- **Border:** primary-200, 2px
- **Icon:** Calculator icon, primary-500
- **Updates:** Real-time as user adjusts sliders
- **Layout:**
  - 3 rows: Credits, Duration, Nodes
  - Icon + Label + Value (right-aligned, bold)

**Action Buttons:**
- **Cancel:** Ghost button, left side
- **Submit:** Primary button, right side, large
  - Disabled state: Gray, cursor-not-allowed
  - Enabled: primary-500, hover:primary-600
  - Loading state: Spinner + "Submitting..."

---

### Screen 4: Job Detail Page

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR  │  Job #123: Monte Carlo Pi Estimation                │
│           │  ═══════════════════════════════════════             │
│           │                                                       │
│           │  [← Back to Jobs]              Status: ⚡ Running     │
│           │                                                       │
│           │  ┌─── Overview ─────────────────────────────────────┐│
│           │  │ Owner: Alice                                     ││
│           │  │ Docker Image: python:3.11-slim                   ││
│           │  │ Created: 2025-11-17 10:30 AM                     ││
│           │  │ Priority: 5                                      ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  ┌─── Progress ────────────────────────────────────┐ │
│           │  │ Completed: 3/4 chunks (75%)                     │ │
│           │  │ ████████████████░░░░░░                          │ │
│           │  │                                                 │ │
│           │  │ Est. Completion: 5 minutes                      │ │
│           │  │ Elapsed Time: 25 minutes                        │ │
│           │  └─────────────────────────────────────────────────┘ │
│           │                                                       │
│           │  ┌─── Chunk Status ───────────────────────────────┐  │
│           │  │                                                 │  │
│           │  │ ┌─────┬──────────┬─────────┬──────────────────┐│  │
│           │  │ │ #   │ Node     │ Status  │ Progress         ││  │
│           │  │ ├─────┼──────────┼─────────┼──────────────────┤│  │
│           │  │ │ 0   │ Node-42  │ ✅ Done  │ 100%             ││  │
│           │  │ │ 1   │ Node-17  │ ✅ Done  │ 100%             ││  │
│           │  │ │ 2   │ Node-8   │ ✅ Done  │ 100%             ││  │
│           │  │ │ 3   │ Node-23  │ ⚡ Run.  │ ████░░░░ 65%     ││  │
│           │  │ └─────┴──────────┴─────────┴──────────────────┘│  │
│           │  │                                                 │  │
│           │  │ [View Logs] [Download Results]                 │  │
│           │  └─────────────────────────────────────────────────┘  │
│           │                                                       │
│           │  ┌─── Real-Time Logs ─────────────────────────────┐  │
│           │  │ [Chunk 3] 2025-11-17 10:55:23                  │  │
│           │  │ Estimating Pi with 25M samples...               │  │
│           │  │ Progress: 65% complete                          │  │
│           │  │ Intermediate result: π ≈ 3.14158                │  │
│           │  │ ▌ (blinking cursor)                             │  │
│           │  └─────────────────────────────────────────────────┘  │
│           │                                                       │
│           │  Actions:                                             │
│           │  [⏸️ Pause Job] [❌ Cancel Job] [📊 View Analytics]   │
│           │                                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Details

**Status Badge:**
- **Position:** Top-right corner
- **Size:** px-4 py-2
- **Variants:**
  - Pending: Yellow background, clock icon
  - Running: Blue background, lightning icon, pulse animation
  - Completed: Green background, checkmark icon
  - Failed: Red background, X icon
  - Cancelled: Gray background, stop icon

**Progress Bar:**
- **Total Height:** 24px
- **Background:** gray-200
- **Fill:** Gradient based on status
  - Running: Blue gradient with shimmer animation
  - Complete: Green solid
- **Percentage:** Overlaid text, centered, white, font-semibold
- **Border:** rounded-lg

**Chunk Status Table:**
- **Striped Rows:** Alternate bg-gray-50
- **Hover:** bg-gray-100
- **Status Icons:**
  - ✅ Green checkmark (completed)
  - ⚡ Blue lightning (running) - animated pulse
  - ⏳ Yellow hourglass (pending)
  - ❌ Red X (failed)
- **Progress Column:** Mini progress bars, 100px width
- **Click Row:** Expand to show chunk details

**Real-Time Logs Terminal:**
- **Background:** #1e1e1e (VS Code dark theme)
- **Font:** 'JetBrains Mono', monospace, 12px
- **Text Color:** #d4d4d4 (light gray)
- **Timestamp:** #569cd6 (blue)
- **Auto-scroll:** Scroll to bottom on new log
- **Blinking Cursor:** Shows live updates
- **Max Height:** 300px, scrollable

**Action Buttons:**
- **Pause:** Warning color (amber)
  - Changes to "Resume" when paused
- **Cancel:** Destructive color (red)
  - Shows confirmation dialog
- **Analytics:** Info color (cyan)
  - Opens modal with detailed metrics

**WebSocket Connection:**
- Status indicator: Small dot in corner
  - Green: Connected, receiving updates
  - Yellow: Connecting...
  - Red: Disconnected, retrying...

---

### Screen 5: Marketplace/Browse Nodes

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR  │  Resource Marketplace                                │
│           │  ═════════════════════                               │
│           │                                                       │
│           │  ┌─── Filters ────────────────┐                      │
│           │  │ Min CPU Cores: [0] ──●──   │  52 nodes found      │
│           │  │ Min RAM (GB):  [0] ──●──   │                      │
│           │  │ Offer Type:    [All  ▼]    │  Sort by: [Price ▼] │
│           │  │ Region:        [All  ▼]    │                      │
│           │  │ [Reset Filters]            │  View: [Grid][List]  │
│           │  └────────────────────────────┘                      │
│           │                                                       │
│           │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│           │  │ Node-42  │ │ Node-17  │ │ Node-8   │            │
│           │  │──────────│ │──────────│ │──────────│            │
│           │  │ 🟢 Online│ │ 🟢 Online│ │ 🔴 Busy  │            │
│           │  │          │ │          │ │          │            │
│           │  │ 8 cores  │ │ 4 cores  │ │ 16 cores │            │
│           │  │ 16 GB    │ │ 8 GB     │ │ 32 GB    │            │
│           │  │ 500 GB   │ │ 250 GB   │ │ 1 TB     │            │
│           │  │          │ │          │ │          │            │
│           │  │ 💰 FREE  │ │ 50 cr/hr │ │ 80 cr/hr │            │
│           │  │          │ │          │ │          │            │
│           │  │ Alice's  │ │ Bob's    │ │ Charlie's│            │
│           │  │ Desktop  │ │ Laptop   │ │ Server   │            │
│           │  │          │ │          │ │          │            │
│           │  │ ⭐⭐⭐⭐⭐ │ │ ⭐⭐⭐⭐   │ │ ⭐⭐⭐⭐⭐  │            │
│           │  │ 99% up   │ │ 95% up   │ │ 100% up  │            │
│           │  │          │ │          │ │          │            │
│           │  │ [Select] │ │ [Select] │ │ [Busy]   │            │
│           │  └──────────┘ └──────────┘ └──────────┘            │
│           │                                                       │
│           │  [Load More...]                                       │
│           │                                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Details

**Filter Panel:**
- **Position:** Top-left, sticky
- **Size:** 280px x auto
- **Sliders:** Same style as job submission
- **Dropdowns:** h-10, rounded-md
- **Reset Button:** Text button, primary color, underline on hover

**Results Header:**
- **Count:** "52 nodes found" - bold, text-lg
- **Sort Dropdown:** Options: Price, CPU, RAM, Rating, Availability
- **View Toggle:**
  - Grid icon + List icon
  - Active state: primary-500 background

**Node Cards (Grid View):**
- **Size:** 220px x 380px
- **Spacing:** gap-4 between cards
- **Layout:** 3-4 columns depending on screen width
- **Background:** White, shadow-md, hover:shadow-xl
- **Border Radius:** rounded-lg

**Card Sections:**
1. **Status Badge** (top-right):
   - 🟢 Online: Green, pulse animation
   - 🔴 Busy: Red, no animation
   - ⚪ Offline: Gray

2. **Resources** (center):
   - Icon + Number + Unit
   - CPU: 🖥️ icon
   - RAM: 💾 icon
   - Storage: 💿 icon

3. **Pricing** (prominent):
   - Large text-2xl for price
   - "FREE" in success color
   - Credits/hour in neutral color

4. **Owner Info**:
   - Small avatar (32x32px)
   - Name truncated if long

5. **Rating** (bottom):
   - 5-star display (filled vs outline)
   - Uptime percentage below
   - Tooltip: "Based on 42 jobs"

6. **Action Button**:
   - Full-width at bottom
   - "Select" - primary color
   - "Busy" - disabled, gray
   - "Offline" - disabled, gray

**List View (Alternative):**
- Table layout with columns
- Same information, more compact
- Better for comparing many nodes

---

### Screen 6: Credit Management

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR  │  Credit Management                                   │
│           │  ══════════════════                                  │
│           │                                                       │
│           │  Current Balance:                                     │
│           │  ┌──────────────────────────────────────────────────┐│
│           │  │                                                   ││
│           │  │          💰 1,245 CREDITS                         ││
│           │  │                                                   ││
│           │  │   [Buy More Credits]  [Withdraw]                 ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  Quick Stats (Last 30 Days):                         │
│           │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│           │  │ Earned   │ │ Spent    │ │ Net      │            │
│           │  │ +2,450   │ │ -1,205   │ │ +1,245   │            │
│           │  └──────────┘ └──────────┘ └──────────┘            │
│           │                                                       │
│           │  ┌─── Usage Chart ─────────────────────────────────┐ │
│           │  │                                                  │ │
│           │  │    [Line/Bar Chart showing credits over time]   │ │
│           │  │                                                  │ │
│           │  │    Green line: Credits earned (providing nodes) │ │
│           │  │    Blue line: Credits spent (running jobs)      │ │
│           │  │                                                  │ │
│           │  └──────────────────────────────────────────────────┘ │
│           │                                                       │
│           │  Transaction History:                                 │
│           │  ┌──────┬────────┬────────┬───────┬─────────────────┐│
│           │  │ Date │ Type   │ Amount │ Job   │ Balance After   ││
│           │  ├──────┼────────┼────────┼───────┼─────────────────┤│
│           │  │ Nov17│ Earned │ +50 cr │ #125  │ 1,245 cr        ││
│           │  │ Nov17│ Spent  │ -224cr │ #123  │ 1,195 cr        ││
│           │  │ Nov16│ Earned │ +100cr │ #121  │ 1,419 cr        ││
│           │  │ Nov16│ Bonus  │ +200cr │ N/A   │ 1,319 cr        ││
│           │  │ Nov15│ Spent  │ -56 cr │ #120  │ 1,119 cr        ││
│           │  └──────┴────────┴────────┴───────┴─────────────────┘│
│           │                                                       │
│           │  [Export CSV] [View All Transactions]                │
│           │                                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Details

**Balance Display:**
- **Background:** Gradient from primary-500 to primary-600
- **Text Color:** White
- **Amount:** text-4xl, font-bold, tabular-nums
- **Icon:** Gold coin emoji or SVG icon
- **Animation:** Count-up animation on page load

**Quick Stats Cards:**
- **Size:** Equal width, h-24
- **Earned:** Green accent
- **Spent:** Red accent
- **Net:** Blue accent
- **Icon:** Trending up/down arrow
- **Number:** text-2xl, font-semibold

**Usage Chart:**
- **Type:** Dual-axis line chart
- **Timeframe Selector:** Tabs for 7d / 30d / 90d / 1y
- **Legend:** Top-right corner
- **Tooltip:** Shows exact values on hover
- **Export:** Download chart as PNG button

**Transaction Table:**
- **Pagination:** 10 rows per page
- **Sort:** Click column headers to sort
- **Row Hover:** bg-gray-50
- **Amount Coloring:**
  - Positive (earned): success color, "+" prefix
  - Negative (spent): error color, "-" prefix
- **Date Format:** "Nov 17" or "2 hours ago"
- **Job Link:** Clickable, opens job detail

**Action Buttons:**
- **Buy Credits:** Opens payment modal
- **Withdraw:** Convert credits to money (if supported)
- **Export CSV:** Downloads transaction history

---

### Screen 7: Analytics Dashboard

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR  │  Analytics & Insights                                │
│           │  ════════════════════                                │
│           │                                                       │
│           │  Date Range: [Last 30 Days ▼]     [Custom Range]    │
│           │                                                       │
│           │  ┌─── Overview ─────────────────────────────────────┐│
│           │  │ Jobs Submitted: 145                              ││
│           │  │ Success Rate: 98.6%                              ││
│           │  │ Avg. Completion Time: 23.5 min                   ││
│           │  │ Total Compute Hours: 342 hrs                     ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  ┌─── Job Performance ──────────────────────────────┐│
│           │  │ [Bar Chart: Jobs by Status]                      ││
│           │  │                                                   ││
│           │  │ ████████████ Completed (143)                     ││
│           │  │ ██ Pending (2)                                   ││
│           │  │ ░ Failed (2)                                     ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  ┌─── Resource Usage ───────────────────────────────┐│
│           │  │ [Pie Chart: Credits by Job Type]                ││
│           │  │                                                   ││
│           │  │ 45% Data Processing                              ││
│           │  │ 30% ML Training                                  ││
│           │  │ 25% Monte Carlo                                  ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  ┌─── Cost Breakdown ──────────────────────────────┐ │
│           │  │ [Table: Top 5 most expensive jobs]              │ │
│           │  │                                                  │ │
│           │  │ Job #125: ML Training - 850 credits             │ │
│           │  │ Job #123: Data Proc - 450 credits               │ │
│           │  │ Job #121: Monte Carlo - 224 credits             │ │
│           │  └──────────────────────────────────────────────────┘ │
│           │                                                       │
│           │  [📥 Download Report] [📧 Email Report]              │
│           │                                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Details

**Date Range Selector:**
- **Presets:** Last 7 days, Last 30 days, Last 90 days, This year
- **Custom:** Date picker for start/end dates
- **Apply Button:** Fetches new data

**Overview Metrics:**
- **Layout:** 2x2 grid
- **Each Metric:**
  - Icon (24x24px)
  - Label (text-sm, gray)
  - Value (text-2xl, bold, primary)
  - Trend indicator: +12% ↑ (green if positive)

**Charts:**
- **Responsive:** Resize with container
- **Interactive:** Hover tooltips
- **Accessible:** Color-blind safe palette
- **Animation:** Smooth transitions on data change

**Bar Chart (Job Performance):**
- **Horizontal Bars:** Easier to read labels
- **Colors:** Match status colors
- **Count Display:** At end of each bar

**Pie Chart (Resource Usage):**
- **Donut Style:** Center shows total
- **Legend:** Right side
- **Hover:** Highlight segment, show percentage

**Cost Breakdown Table:**
- **Top 5:** Most expensive jobs
- **Columns:** Job ID, Name, Credits, Date
- **Sparkline:** Mini cost trend chart per job

**Export Options:**
- **Download Report:** PDF with all charts
- **Email Report:** Send to user's email
- **Schedule:** Set up recurring reports (weekly/monthly)

---

### Screen 8: Settings Page

#### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR  │  Settings                                            │
│           │  ════════                                            │
│           │                                                       │
│           │  ┌─ TABS ─────────────────────────────────────────┐ │
│           │  │ [Profile] [Security] [Notifications] [Advanced]│ │
│           │  └──────────────────────────────────────────────────┘ │
│           │                                                       │
│           │  Profile Settings                                     │
│           │  ───────────────────                                  │
│           │                                                       │
│           │  ┌──────────────────────────────────────────────────┐│
│           │  │ Avatar:  [👤 Photo]  [Upload New]               ││
│           │  │                                                   ││
│           │  │ Username:                                         ││
│           │  │ ┌──────────────────────────────────────────────┐ ││
│           │  │ │ alice                                        │ ││
│           │  │ └──────────────────────────────────────────────┘ ││
│           │  │                                                   ││
│           │  │ Email:                                            ││
│           │  │ ┌──────────────────────────────────────────────┐ ││
│           │  │ │ alice@example.com                            │ ││
│           │  │ └──────────────────────────────────────────────┘ ││
│           │  │                                                   ││
│           │  │ Display Name:                                     ││
│           │  │ ┌──────────────────────────────────────────────┐ ││
│           │  │ │ Alice Johnson                                │ ││
│           │  │ └──────────────────────────────────────────────┘ ││
│           │  │                                                   ││
│           │  │ Timezone:                                         ││
│           │  │ ┌──────────────────────────────────────────────┐ ││
│           │  │ │ America/New_York (UTC-5)            ▼       │ ││
│           │  │ └──────────────────────────────────────────────┘ ││
│           │  │                                                   ││
│           │  │ [Cancel]                    [Save Changes]       ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
│           │  Notifications (when switched to that tab)           │
│           │  ────────────────                                     │
│           │  ┌──────────────────────────────────────────────────┐│
│           │  │ Email Notifications:                             ││
│           │  │ ☑ Job completed                                  ││
│           │  │ ☑ Job failed                                     ││
│           │  │ ☐ Weekly summary                                 ││
│           │  │                                                   ││
│           │  │ Webhook URL (optional):                          ││
│           │  │ ┌──────────────────────────────────────────────┐ ││
│           │  │ │ https://myapp.com/webhook                    │ ││
│           │  │ └──────────────────────────────────────────────┘ ││
│           │  │                                                   ││
│           │  │ [Test Webhook] [Save]                            ││
│           │  └──────────────────────────────────────────────────┘│
│           │                                                       │
└─────────────────────────────────────────────────────────────────┘
```

#### Details

**Tab Navigation:**
- **Style:** Underline tabs
- **Active:** primary-500 underline (2px), font-semibold
- **Inactive:** text-gray-600, hover:text-gray-900

**Form Fields:**
- **Labels:** text-sm, font-medium, mb-1
- **Inputs:** h-12, rounded-md, border-gray-300
- **Focus State:** ring-2, ring-primary-500

**Avatar Upload:**
- **Current:** 96x96px circle
- **Hover:** Overlay with "Change" text
- **Click:** File picker (accepts .jpg, .png, max 5MB)

**Checkboxes:**
- **Size:** w-5, h-5
- **Checked:** primary-500 background, white checkmark
- **Label:** ml-2, text-sm

**Save Button:**
- **State Management:**
  - Default: primary-500
  - Unsaved Changes: Enabled
  - No Changes: Disabled (gray)
  - Saving: Spinner + "Saving..."
  - Success: Green ✓ + "Saved!" (2 sec)

---

## Component Library

### Reusable Components

#### 1. **Button**

Variants:
```jsx
<Button variant="primary">Submit</Button>      // Blue solid
<Button variant="secondary">Cancel</Button>    // Gray outline
<Button variant="destructive">Delete</Button>  // Red solid
<Button variant="ghost">More</Button>          // Transparent
```

Sizes:
```jsx
<Button size="sm">Small</Button>     // h-8, text-sm
<Button size="md">Medium</Button>    // h-10, text-base (default)
<Button size="lg">Large</Button>     // h-12, text-lg
```

#### 2. **Card**

```jsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content goes here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

Styles:
- Background: white
- Border: border-gray-200, 1px
- Shadow: shadow-sm
- Radius: rounded-lg
- Padding: p-6

#### 3. **Badge**

```jsx
<Badge variant="success">Completed</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
<Badge variant="info">Running</Badge>
```

Styles:
- Size: px-3 py-1
- Font: text-xs, font-medium
- Radius: rounded-full

#### 4. **Table**

```jsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Column 1</TableHead>
      <TableHead>Column 2</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data 1</TableCell>
      <TableCell>Data 2</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### 5. **Modal/Dialog**

```jsx
<Dialog>
  <DialogTrigger>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    <div>Dialog body</div>
    <DialogFooter>
      <Button>Cancel</Button>
      <Button variant="primary">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

## User Flows

### Flow 1: First-Time User Onboarding

```
1. Land on homepage
   ↓
2. Click "Get Started"
   ↓
3. Registration form (username, email, password)
   ↓
4. Email verification (optional)
   ↓
5. Welcome screen with tutorial
   ↓
6. Choose action:
   - Submit first job (guided wizard)
   - Register node (step-by-step guide)
   - Browse marketplace (quick tour)
```

### Flow 2: Submitting a Job

```
1. Click "Submit Job" button
   ↓
2. Choose template or custom
   ↓
3. Fill configuration form
   ↓
4. Review cost estimate
   ↓
5. Click "Submit"
   ↓
6. Confirmation toast
   ↓
7. Redirect to job detail page
   ↓
8. Real-time progress updates via WebSocket
```

### Flow 3: Monitoring Job Progress

```
1. Navigate to "Jobs" page
   ↓
2. See list of jobs with statuses
   ↓
3. Click on running job
   ↓
4. View real-time progress
   - Overall progress bar
   - Chunk status table
   - Live logs
   ↓
5. Optional actions:
   - Pause job
   - Cancel job
   - View analytics
   ↓
6. Job completes
   ↓
7. Notification (email/webhook)
   ↓
8. Download results button appears
```

---

## Responsive Design

### Breakpoints

```css
--mobile: 320px - 767px
--tablet: 768px - 1023px
--desktop: 1024px - 1439px
--large: 1440px+
```

### Layout Changes by Breakpoint

**Mobile (< 768px):**
- Hide sidebar (convert to hamburger menu)
- Single column layouts
- Stack cards vertically
- Reduce chart complexity
- Bottom navigation bar for main actions

**Tablet (768px - 1023px):**
- Collapsible sidebar (icon-only mode)
- 2-column card grids
- Simplified tables (hide non-essential columns)

**Desktop (1024px+):**
- Full sidebar
- 3-4 column card grids
- Full tables
- Multi-panel layouts

---

## Accessibility

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text: Minimum 4.5:1 ratio
- Large text (18pt+): Minimum 3:1 ratio
- UI components: Minimum 3:1 ratio

**Keyboard Navigation:**
- All interactive elements focusable
- Logical tab order
- Skip links for main content
- Escape key closes modals/dropshots

**Screen Reader Support:**
- Semantic HTML (nav, main, aside)
- ARIA labels for icons
- ARIA live regions for dynamic content
- Alt text for images

**Focus Indicators:**
- Visible focus ring: 2px, primary-500
- Never remove outline without replacement

**Motion:**
- Respect prefers-reduced-motion
- Disable animations for users with motion sensitivity

---

## Implementation Notes

### State Management

```typescript
// Global State (Zustand)
interface AppState {
  user: User | null;
  jobs: Job[];
  nodes: Node[];
  credits: number;
  websocketConnected: boolean;
}

// Job State
interface JobState {
  jobs: Record<number, Job>;
  activeJobId: number | null;
  filters: JobFilters;
}
```

### WebSocket Integration

```typescript
// Connect on mount
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/jobs/123');

  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    updateJobProgress(update);
  };

  return () => ws.close();
}, [jobId]);
```

### Real-Time Updates

```typescript
// Optimistic UI updates
const submitJob = async (jobData) => {
  // 1. Immediately add to UI (optimistic)
  const tempJob = { ...jobData, id: 'temp-' + Date.now(), status: 'pending' };
  addJob(tempJob);

  // 2. Submit to server
  const response = await api.post('/jobs', jobData);

  // 3. Replace temp with real data
  replaceJob(tempJob.id, response.data);
};
```

---

## Design System Checklist

✅ Color palette defined
✅ Typography scale established
✅ Spacing system (4px grid)
✅ Component library documented
✅ Responsive breakpoints
✅ Accessibility guidelines
✅ Animation principles
✅ Dark mode support (future)

---

## Next Steps for Implementation

1. **Setup Project**
   - Create React app with TypeScript
   - Install Tailwind CSS + shadcn/ui
   - Configure routing

2. **Build Component Library**
   - Implement base components (Button, Card, etc.)
   - Create Storybook for component showcase
   - Write component tests

3. **Implement Pages**
   - Start with authentication flow
   - Build dashboard home
   - Add job submission
   - Implement real-time job monitoring

4. **Connect to API**
   - Setup Axios/Fetch wrapper
   - Implement WebSocket client
   - Add error handling
   - Implement retry logic

5. **Testing**
   - Unit tests (Jest + React Testing Library)
   - E2E tests (Playwright/Cypress)
   - Accessibility audit (aXe)

6. **Deploy**
   - Build production bundle
   - Deploy to Vercel/Netlify
   - Setup CI/CD

---

**End of UI Specification**

This document provides a complete blueprint for building the web dashboard. Developers can use this as a reference to implement the exact UI/UX described above.
