# 🎯 Demo Scripts Interaction Guide

## What Happens Between Steps?

### 🔄 Interactive Mode (Original Go Demos)

When you run the original Go-based demos (`./demo-stack-up --startup`), here's exactly what happens:

```
🚀 AI Manufacturing Stack Startup Demo
=====================================

This demo will walk through starting up our complete
AI-powered manufacturing stack including:
• Ignition SCADA Gateway (with auto license acceptance)
• PostgreSQL databases for MES and vector storage
...

All services will auto-accept licenses and certificates!

… ← **WAITS HERE FOR ENTER KEY**
```

**What you need to do:**
1. **Press ENTER** to proceed to the first step
2. Read the step description
3. **Press ENTER** again to execute the command
4. **Press ENTER** again to proceed to the next step
5. Repeat for each of the 11 steps

### 📋 Step-by-Step Breakdown

Each demo step follows this pattern:

```
# 🔍 First, let's verify our prerequisites are met:
# • Docker is installed and running
# • Required secrets are in place
# • Environment configuration is ready [1/11]:

> ./scripts/demo-preflight.sh
← **PRESS ENTER HERE to execute the command**

[Command executes and shows output]

← **PRESS ENTER HERE to go to next step**
```

### 🚨 Why It Hangs

The demo framework **intentionally pauses** at each step waiting for:
- **ENTER** to proceed to the next step description
- **ENTER** to execute the command  
- **ENTER** to continue after command completion

This is **designed for interactive presentations** where you want to:
- Explain each step to your audience
- Control the timing
- Answer questions between steps
- Show command output before proceeding

## 🎯 Solutions for Different Use Cases

### 1. 🎤 **Live Presentation Mode** (Recommended)

Use the **new auto-running script** that doesn't require interaction:

```bash
# Fully automatic with nice presentation effects
./demo-stack-auto.sh startup

# Fast mode without typewriter effects  
DEMO_NO_TYPEWRITER=1 ./demo-stack-auto.sh startup

# Custom timing
DEMO_STEP_DELAY=1 DEMO_COMMAND_DELAY=0.5 ./demo-stack-auto.sh startup
```

**Perfect for:**
- Live presentations
- Recorded demos
- Continuous integration
- Unattended execution

### 2. 🎓 **Interactive Training Mode**

Use the original Go demos when you want to:
- Train team members step-by-step
- Explain each component in detail
- Allow questions between steps
- Control exact timing

```bash
# Interactive mode - you control each step
./demo-stack-up --startup

# Automatic mode - runs all steps with 1s delay
./demo-stack-up --startup --auto

# Dry run - shows commands without executing
./demo-stack-up --startup --dry-run
```

### 3. ⚡ **Quick Testing Mode**

For rapid testing and CI/CD:

```bash
# Fastest possible execution
DEMO_NO_TYPEWRITER=1 DEMO_STEP_DELAY=0 DEMO_COMMAND_DELAY=0 ./demo-stack-auto.sh startup

# Or use the original with auto mode
./demo-stack-up --startup --auto --immediate
```

## 🎬 Recommended Usage by Scenario

### 📊 **Conference Presentation**
```bash
# Start with dramatic effect, then speed up
./demo-stack-auto.sh startup

# Quick health check
DEMO_NO_TYPEWRITER=1 ./demo-stack-auto.sh health

# Fast shutdown at end
DEMO_NO_TYPEWRITER=1 ./demo-stack-auto.sh shutdown
```

### 🏫 **Training Workshop**
```bash
# Interactive mode - explain each step
./demo-stack-up --startup
# Press ENTER at each pause to explain to students

# Let them try the health check
./demo-stack-up --health
```

### 🔧 **Development/Testing**
```bash
# Fast automated execution
DEMO_NO_TYPEWRITER=1 DEMO_STEP_DELAY=0 ./demo-stack-auto.sh startup
```

### 📹 **Recording a Video**
```bash
# Smooth automatic execution with good timing
DEMO_STEP_DELAY=3 DEMO_COMMAND_DELAY=1 ./demo-stack-auto.sh startup
```

## 🎛️ Customization Options

### Auto Demo Script Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_STEP_DELAY` | `2` | Seconds to wait between steps |
| `DEMO_COMMAND_DELAY` | `1` | Seconds before executing commands |
| `DEMO_TYPEWRITER_SPEED` | `0.03` | Seconds per character for typewriter effect |
| `DEMO_NO_TYPEWRITER` | `0` | Set to `1` to disable typewriter effect |
| `DEMO_CONTINUE_ON_ERROR` | `0` | Set to `1` to continue if commands fail |

### Go Demo Framework Options

| Option | Description |
|--------|-------------|
| `--auto` | Run automatically with 1s delays |
| `--immediate` | Skip typewriter animation |
| `--dry-run` | Show commands without executing |
| `--auto-timeout 3s` | Set delay between auto steps |
| `--continue-on-error` | Continue if steps fail |
| `--skip-steps 2` | Skip first N steps |

## 🚀 Quick Reference

### For Presentations (No Interaction Required)
```bash
./demo-stack-auto.sh startup     # Auto-running startup
./demo-stack-auto.sh health      # Auto health check  
./demo-stack-auto.sh shutdown    # Auto shutdown
```

### For Training (Interactive)
```bash
./demo-stack-up --startup        # Press ENTER between steps
./demo-stack-up --health         # Press ENTER between steps
./demo-stack-down --shutdown     # Press ENTER between steps
```

### For Testing (Fast)
```bash
DEMO_NO_TYPEWRITER=1 DEMO_STEP_DELAY=0 ./demo-stack-auto.sh startup
```

## 🎯 The Bottom Line

**For your presentation, use:**
```bash
./demo-stack-auto.sh startup
```

This will run completely automatically with nice visual effects and no interaction required. Perfect for live demos where you want to focus on explaining the technology rather than pressing keys!
