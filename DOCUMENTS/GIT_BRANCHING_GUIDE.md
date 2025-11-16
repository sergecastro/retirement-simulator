# GIT BRANCHING GUIDE FOR PARALLEL DEVELOPMENT
## Step-by-Step Instructions for Non-Programmers

**Created:** November 15, 2025
**Purpose:** Safe parallel development without breaking production

---

## WHAT IS GIT BRANCHING?

Think of your code like a tree:
- **master branch** = The main trunk (your production code)
- **feature branch** = A side branch (your experimental code)

You can grow the side branch without touching the trunk. When the side branch is strong enough, you can graft it back.

---

## COMMANDS YOU NEED TO KNOW

### 1. Check Current Status
```bash
git status
```
**What it does:** Shows which branch you're on and what files changed.

### 2. See All Branches
```bash
git branch
```
**What it does:** Lists all branches. Current branch has a * next to it.

### 3. Create New Branch
```bash
git checkout -b feature/sidebar-architecture
```
**What it does:** Creates AND switches to new branch in one command.

### 4. Switch Between Branches
```bash
git checkout master              # Go back to production
git checkout feature/sidebar-architecture  # Go to new development
```
**What it does:** Switches your entire codebase to that branch's version.

### 5. Save Your Work
```bash
git add .
git commit -m "Description of what you changed"
```
**What it does:** Saves a checkpoint of your current work.

---

## THE SAFE WORKFLOW

### BEFORE YOU START (Do Once)

**Step 1: Tag Current Production**
```bash
git tag v1.0-pre-sidebar
```
This creates a "bookmark" of your current working code. If anything goes wrong, you can always return here.

**Step 2: Create Feature Branch**
```bash
git checkout -b feature/sidebar-architecture
```
Now you're on the new branch. All changes happen here.

---

### DAILY WORKFLOW

**Morning: Start Work**
```bash
git checkout feature/sidebar-architecture
git status  # Make sure you're on right branch
```

**During Day: Save Progress**
```bash
git add .
git commit -m "Added sidebar component to app.py"
```

**If You Need to Check Production:**
```bash
git stash  # Temporarily saves your uncommitted work
git checkout master
# ... check production ...
git checkout feature/sidebar-architecture
git stash pop  # Brings back your uncommitted work
```

**End of Day: Save Everything**
```bash
git add .
git commit -m "End of day: sidebar navigation 50% complete"
```

---

## RUNNING TWO VERSIONS SIMULTANEOUSLY

### Terminal 1: Production (Port 8501)
```bash
git checkout master
streamlit run app.py --server.port 8501
```
Open browser: http://localhost:8501

### Terminal 2: New Development (Port 8502)
```bash
git checkout feature/sidebar-architecture
streamlit run app.py --server.port 8502
```
Open browser: http://localhost:8502

**Now you can compare them side-by-side!**

---

## WHAT CLAUDE CODE WILL DO FOR YOU

Since you mentioned you're not comfortable with Git commands, here's what I (Claude Code) can do:

### I WILL DO:
1. ✅ Create the feature branch for you
2. ✅ Make all code changes on that branch
3. ✅ Commit changes with proper messages
4. ✅ Ensure we never touch master accidentally
5. ✅ Tag releases before major changes

### YOU WILL DO:
1. ✅ Test the application (both versions)
2. ✅ Report bugs or issues
3. ✅ Approve changes before we proceed
4. ✅ Provide feedback on UI/UX

### WE WILL DO TOGETHER:
1. ✅ Review each phase before moving forward
2. ✅ Decide when to merge to production
3. ✅ Plan each week's priorities

---

## EMERGENCY ROLLBACK

If something goes terribly wrong:

**Option 1: Abandon Feature Branch**
```bash
git checkout master  # Go back to production
# Feature branch changes are isolated, production is safe
```

**Option 2: Reset to Tagged Version**
```bash
git checkout v1.0-pre-sidebar
# Goes back to exact state before we started
```

**Option 3: Start Fresh**
```bash
git checkout master
git branch -D feature/sidebar-architecture  # Delete bad branch
git checkout -b feature/sidebar-architecture  # Start over
```

---

## VISUAL REPRESENTATION

```
TIME →

Nov 15 (Today)
    |
    master ────────────────────────────────────→ (Production stays stable)
    |
    └─── v1.0-pre-sidebar (TAG)
         |
         └─── feature/sidebar-architecture ───→ (All new work here)
                    |
                    ├── Phase 1: Sidebar Shell
                    ├── Phase 2: Healthcare Hub
                    ├── Phase 3: Scenario Studio
                    └── (Future phases...)
```

---

## CLAUDE CODE'S COMMITMENT

When you tell me to "create the Git branch," I will:

1. Run `git status` to verify we're on master
2. Run `git tag v1.0-pre-sidebar` to bookmark production
3. Run `git checkout -b feature/sidebar-architecture` to create new branch
4. Confirm success with `git branch` showing the new branch

**You will see:**
```
* feature/sidebar-architecture
  master
```

The * means we're on the new branch. All changes from this point forward affect ONLY this branch.

---

## LET'S START NOW

Would you like me to:

1. **Create the branch now?** (I'll run the Git commands)
2. **Wait until after Sunday?** (Keep production stable for friend testing)
3. **Run the test suite first?** (Validate our safety net)

**My recommendation:** Let's run the test suite first to ensure we have a safety net, THEN create the branch after your Sunday deadline.

**Command to run tests:**
```bash
cd C:\Users\serge\Desktop\retirement-simulator-dev\retirement-simulator\family_retirement_no_OCR
python -m pytest tests/test_simulation_core.py -v
```

Say "run tests" and I'll execute it for you!

---

*Guide prepared by Claude Code*
*For: Serge (Project Owner)*
*Date: November 15, 2025*
