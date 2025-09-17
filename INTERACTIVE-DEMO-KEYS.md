# ⌨️ Interactive Demo - What to Type

## 🎯 Simple Answer: Just Press ENTER

When using the interactive demos (non-auto mode), you only need to press **one key**:

**Press `ENTER` (Return key) at each pause**

That's it! No other typing required.

## 🔄 Step-by-Step Example

Here's exactly what happens when you run `./run-demo.sh up startup`:

### 1. Initial Screen
```
🚀 AI Manufacturing Stack Startup Demo
=====================================

This demo will walk through starting up our complete
AI-powered manufacturing stack including:
• Ignition SCADA Gateway (with auto license acceptance)
• PostgreSQL databases for MES and vector storage
• LlamaIndex RAG service for AI responses
• RabbitMQ for message queuing
• MQTT broker for IoT communication
• Kong API Gateway for service orchestration
• Monitoring stack (Grafana, Prometheus, Netdata)
• Redis for caching

All services will auto-accept licenses and certificates!

…
```
**👆 PRESS `ENTER` HERE** to proceed to first step

### 2. First Step Description
```
# 🔍 First, let's verify our prerequisites are met:
# • Docker is installed and running
# • Required secrets are in place
# • Environment configuration is ready [1/11]:
```
**👆 PRESS `ENTER` HERE** to execute the command

### 3. Command Execution
```
> ./scripts/demo-preflight.sh

[preflight] Checking prerequisites...
[preflight] Docker version: Docker version 24.0.6
[preflight] OK
```
**👆 PRESS `ENTER` HERE** to go to next step

### 4. Next Step
```
# 📋 Let's examine our Docker Compose configuration
# to see what services we'll be starting: [2/11]:
```
**👆 PRESS `ENTER` HERE** to execute next command

...and so on for all 11 steps.

## 🎹 What Keys Do What

| Key | Action |
|-----|--------|
| `ENTER` (Return) | ✅ Proceed to next step or execute command |
| `Ctrl+C` | ❌ Exit the demo immediately |
| Any other key | ❌ Will cause error or unexpected behavior |

## 🚨 Important Notes

### ✅ DO Press ENTER When You See:
- `…` (ellipsis waiting cursor)
- Step descriptions ending with `[X/11]:`
- After command output completes

### ❌ DON'T Type:
- Words or letters
- Numbers
- Special characters
- Multiple keys at once

### 🔄 Rhythm of Interactive Demo
```
1. Read step description
2. Press ENTER
3. Watch command execute  
4. Press ENTER
5. Repeat 11 times
```

## 🎯 Quick Reference

### Interactive Commands That Need ENTER Presses
```bash
./run-demo.sh up startup        # 11 ENTER presses needed
./run-demo.sh up health         # 6 ENTER presses needed  
./run-demo.sh down shutdown     # 7 ENTER presses needed
./run-demo.sh down cleanup      # 7 ENTER presses needed + confirmation
```

### Auto Commands That Need NO Input
```bash
./run-demo.sh auto startup      # Zero input needed
./run-demo.sh auto health       # Zero input needed
./run-demo.sh auto shutdown     # Zero input needed
```

## 🎬 Pro Tips for Interactive Demos

### For Training Sessions
- **Pause at each step** to explain what's happening
- **Ask questions** between steps: "What do you think this command will do?"
- **Let participants read** the step descriptions aloud

### For Troubleshooting
- Use `--dry-run` to see all commands without executing:
  ```bash
  ./run-demo.sh up startup --dry-run
  ```
- Use `--continue-on-error` if you want to keep going despite failures:
  ```bash
  ./run-demo.sh up startup --continue-on-error
  ```

### For Different Speeds
- **Slow/Educational**: Press ENTER, explain, press ENTER, explain...
- **Medium**: Press ENTER, brief comment, press ENTER...  
- **Fast**: Just press ENTER rapidly to get through quickly

## 🆚 Interactive vs Auto Comparison

### Interactive Mode (ENTER presses)
```bash
./run-demo.sh up startup
```
**Best for:**
- Training sessions
- Detailed explanations
- Q&A during demo
- Controlling exact timing

### Auto Mode (no input)
```bash
./run-demo.sh auto startup  
```
**Best for:**
- Live presentations
- Recorded videos
- Unattended execution
- Smooth professional demos

## 🎯 Bottom Line

**In interactive mode, just press `ENTER` at each pause. That's the only key you need!**
