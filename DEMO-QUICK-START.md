# 🚀 Demo Scripts - Quick Start Guide

## 🎯 TL;DR - What You Need to Know

### The Problem You Encountered
When you ran `./run-demo.sh up startup --immediate`, it **hung waiting for you to press ENTER**. This is because the original Go-based demos are designed for **interactive presentations** where you control each step.

### ✅ The Solution - Use Auto Mode

**For your presentation, use this command:**
```bash
./run-demo.sh auto startup
```

**This will:**
- ✅ Run completely automatically (no ENTER key presses needed)
- ✅ Show nice visual effects and step-by-step progress
- ✅ Auto-accept all Ignition licenses and certificates
- ✅ Complete in about 3-5 minutes depending on your system

## 🎬 Complete Presentation Flow

### 1. Start the Demo
```bash
./run-demo.sh auto startup
```
**Takes:** 3-5 minutes  
**Interaction:** None required  
**Result:** Full stack running with all services

### 2. Verify Everything Works
```bash
./run-demo.sh auto health
```
**Takes:** 30 seconds  
**Interaction:** None required  
**Result:** Confirmation all services are healthy

### 3. Show Your Audience the Running Stack
- **Ignition Gateway:** https://localhost:9043
- **Grafana Dashboards:** http://localhost:3000
- **Real-time Monitoring:** http://localhost:19999

### 4. Clean Shutdown After Demo
```bash
./run-demo.sh auto shutdown
```
**Takes:** 1 minute  
**Interaction:** None required  
**Result:** Clean shutdown, data preserved

## 🔄 What Happens Between Steps

### Interactive Mode (Original - Requires ENTER)
```
Step 1 Description
← PRESS ENTER HERE
> Command executes
← PRESS ENTER HERE  
Step 2 Description
← PRESS ENTER HERE
> Next command executes
...and so on for 11 steps
```

### Auto Mode (New - No Interaction)
```
Step 1 Description
> Command executes automatically
[2 second pause]
Step 2 Description  
> Next command executes automatically
[2 second pause]
...continues automatically through all steps
```

## 🎛️ Speed Controls

### Normal Presentation Speed
```bash
./run-demo.sh auto startup
```

### Fast Mode (for testing)
```bash
DEMO_FAST_MODE=1 ./run-demo.sh auto startup
```

### Super Fast Mode (for CI/testing)
```bash
DEMO_NO_TYPEWRITER=1 DEMO_STEP_DELAY=0 ./demo-stack-auto.sh startup
```

## 🚨 License Acceptance - Automatic!

**All licenses are automatically accepted:**
- ✅ `ACCEPT_IGNITION_EULA=Y` in docker-compose.yml
- ✅ Self-signed certificates auto-trusted
- ✅ No popup dialogs or manual steps
- ✅ Perfect for presentations

## 🎯 Bottom Line

**Use this for your presentation:**
```bash
./run-demo.sh auto startup
```

**It will run completely hands-free and show your audience a professional, smooth demo of the entire AI manufacturing stack starting up with automatic license acceptance.**
