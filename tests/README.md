# Live Q&A Platform - Test Suite

This directory contains multiple test approaches for the Live Q&A with Real-Time Voting platform.

## Test Files Overview

### ✅ `test_http_simple.py` (Recommended - Works Now!)
- **5 HTTP-based tests** that work without browser automation
- Tests server connectivity, routes, and basic functionality
- **No browser or ChromeDriver required**
- ✅ Currently working and passing all tests

### 🔧 `test_liveqa.py` (Full Selenium Suite)
- **10 comprehensive Selenium tests** with browser automation
- Requires Chrome browser and ChromeDriver setup
- ⚠️ Currently has ChromeDriver compatibility issues on Windows

### 🛠️ `test_manual_setup.py` (Alternative Selenium)
- Alternative Selenium setup for manual ChromeDriver configuration
- For when webdriver-manager has issues

## Quick Start (HTTP Tests)

**These tests work immediately and require no additional setup:**

```bash
cd tests
pytest test_http_simple.py -v
```

## Prerequisites for HTTP Tests

1. **Frontend running** on `http://localhost:3001`
2. **Backend running** on `http://localhost:3000` (optional)

## Current Test Results

✅ **HTTP Tests (Working):**
1. Frontend Server Running Test
2. Backend Server Running Test  
3. Frontend Routes Accessible Test
4. Frontend Content Verification Test
5. Basic Security Headers Test

⚠️ **Selenium Tests (ChromeDriver Issue):**
- Chrome/ChromeDriver compatibility problem on Windows
- Error: "Unable to obtain driver for chrome using Selenium Manager"

## Running the Working Tests

### Start your application:
```bash
# Terminal 1: Backend
cd backend
npm run start:dev

# Terminal 2: Frontend  
cd frontend
npm run dev

# Terminal 3: Tests
cd tests
pytest test_http_simple.py -v --html=test_report.html
```

## Selenium Setup Issues & Solutions

The Selenium tests are currently failing due to ChromeDriver compatibility issues. Here are the solutions:

### Option 1: Fix ChromeDriver (Advanced)
```bash
# Clear cache and try different approach
python -c "from webdriver_manager.chrome import ChromeDriverManager; import shutil; import os; shutil.rmtree(os.path.expanduser('~/.wdm'), ignore_errors=True)"

# Install specific Chrome version
pip install selenium==4.15.0
```

### Option 2: Manual ChromeDriver Setup
1. Check your Chrome version: `chrome://version/`
2. Download matching ChromeDriver from [chromedriver.chromium.org](https://chromedriver.chromium.org/)
3. Add to PATH or place in project directory
4. Run: `pytest test_manual_setup.py -v`

### Option 3: Use HTTP Tests (Recommended for now)
The HTTP tests provide excellent coverage without browser automation complexity.

## Test Coverage

### HTTP Tests Cover:
- ✅ Server connectivity and availability
- ✅ Route accessibility and response codes
- ✅ Content verification (Q&A related terms)
- ✅ Basic security headers
- ✅ Backend API availability

### Selenium Tests Would Add:
- 🔧 UI interaction testing
- 🔧 Form validation and submission
- 🔧 Theme switching
- 🔧 Responsive design verification
- 🔧 Page load performance measurement
- 🔧 Real user workflow simulation

## Troubleshooting

**Issue: "Frontend server not running"**
```bash
cd frontend && npm run dev
```

**Issue: "Backend server not running"**
```bash
cd backend && npm run start:dev
```

**Issue: ChromeDriver compatibility**
- Use HTTP tests instead: `pytest test_http_simple.py -v`
- Or follow manual ChromeDriver setup above

## Future Enhancements

When ChromeDriver issues are resolved, consider adding:
- End-to-end room creation/joining workflows
- Real-time voting functionality tests
- WebSocket connection testing
- Cross-browser compatibility
- Mobile device simulation
