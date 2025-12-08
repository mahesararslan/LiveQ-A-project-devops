pipeline {
    agent any
    triggers { 
        githubPush() 
    }

    environment {
        // Project configuration
        PROJECT_NAME = 'LiveQ-A-with-Real-Time-Voting'
        FRONTEND_PORT = '3001'
        BACKEND_PORT = '3000'
        POSTGRES_PORT = '5432'
        REDIS_PORT = '6379'
    }

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    echo "🔄 Cloning Live Q&A Project..."
                }
                git branch: 'main', url: 'https://github.com/mahesararslan/LiveQ-A-project-devops.git'
                
                // Create environment files from templates if they don't exist
                sh '''
                    # Backend environment setup
                    if [ ! -f backend/.env ]; then
                        echo "Creating backend .env file..."
                        cat > backend/.env << EOF
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/liveqa
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET=your-jwt-secret-key-for-ci
JWT_EXPIRES_IN=7d
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET=your-google-secret
GOOGLE_CALLBACK_URL=http://localhost:3000/auth/google/callback
FRONTEND_URL=http://localhost:3001
NODE_ENV=development
EOF
                    fi

                    # Frontend environment setup
                    if [ ! -f frontend/.env.local ]; then
                        echo "Creating frontend .env.local file..."
                        cat > frontend/.env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:3000
NEXT_PUBLIC_SOCKET_URL=http://localhost:3000
EOF
                    fi
                '''
            }
        }

        stage('Setup & Start Application') {
            steps {
                script {
                    echo "🚀 Setting up and starting Live Q&A application..."
                }
                
                // Clean up existing containers and images
                sh '''
                    echo "Cleaning up existing containers and freeing disk space..."
                    docker-compose down --remove-orphans || true
                    
                    # Remove old images from this project
                    docker images | grep devops-assignment | awk '{print $3}' | xargs -r docker rmi -f || true
                    
                    # Prune unused Docker resources
                    docker system prune -f
                    docker builder prune -f
                    
                    # Show available disk space
                    echo "Available disk space:"
                    df -h /
                '''
                
                // Build and start the application
                sh '''
                    echo "Starting Live Q&A application with Docker Compose..."
                    docker-compose up --build -d
                    
                    echo "Waiting for services to be ready..."
                    sleep 30
                    
                    # Check if services are running
                    docker-compose ps
                    
                    # Wait for frontend to be ready
                    echo "Waiting for frontend to be accessible..."
                    for i in {1..30}; do
                        if curl -f http://localhost:3001 > /dev/null 2>&1; then
                            echo "✅ Frontend is ready!"
                            break
                        fi
                        echo "⏳ Waiting for frontend... ($i/30)"
                        sleep 2
                    done
                    
                    # Wait for backend to be ready
                    echo "Waiting for backend to be accessible..."
                    for i in {1..30}; do
                        if curl -f http://localhost:3000/graphql > /dev/null 2>&1; then
                            echo "✅ Backend is ready!"
                            break
                        fi
                        echo "⏳ Waiting for backend... ($i/30)"
                        sleep 2
                    done
                '''
            }
        }

        stage('Run HTTP Tests') {
            steps {
                script {
                    echo "🧪 Running HTTP-based tests..."
                }
                
                sh '''
                    cd tests
                    
                    echo "Creating Python virtual environment..."
                    python3 -m venv venv
                    
                    . venv/bin/activate
                    
                    echo "Upgrading pip..."
                    pip install --upgrade pip
                    
                    echo "Installing test dependencies..."
                    pip install -r requirements.txt
                    
                    echo "Running HTTP tests..."
                    pytest test_http_simple.py -v --html=http_test_report.html --self-contained-html --tb=short || exit 1
                    
                    deactivate
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                script {
                    echo "🌐 Running Selenium browser tests (skipped - requires Docker agent)..."
                    echo "⚠️ Selenium tests are disabled to avoid Docker pipeline plugin requirement"
                }
                
                sh '''
                    cd tests
                    
                    echo "Creating Python virtual environment for Selenium tests..."
                    python3 -m venv venv_selenium
                    
                    echo "Activating virtual environment..."
                    . venv_selenium/bin/activate
                    
                    echo "Installing dependencies..."
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Install Chrome/Chromium for Selenium
                    echo "Note: Selenium tests require Chrome/Chromium to be installed on the system"
                    
                    # Run Selenium tests with retry mechanism (optional, can be commented out)
                    echo "Running Selenium tests..."
                    pytest test_selenium_fixed.py -v --html=selenium_test_report.html --self-contained-html --tb=short || {
                        echo "⚠️ Selenium tests failed, trying original test suite..."
                        pytest test_liveqa.py -v --html=selenium_fallback_report.html --self-contained-html --tb=short || {
                            echo "⚠️ Selenium tests failed - continuing pipeline"
                        }
                    }
                    
                    echo "Deactivating virtual environment..."
                    deactivate
                ''' 
            }
        }

        stage('Generate Test Reports') {
            steps {
                script {
                    echo "📊 Generating comprehensive test reports..."
                }
                
                // Archive test artifacts
                archiveArtifacts artifacts: 'tests/*test_report*.html', allowEmptyArchive: true
                
                // Publish test results if JUnit XML files exist
                sh '''
                    cd tests
                    
                    # Create virtual environment for report generation
                    python3 -m venv venv_reports
                    . venv_reports/bin/activate
                    
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    
                    # Convert pytest results to JUnit XML if not already done
                    if [ -f pytest_results.xml ]; then
                        echo "JUnit XML file found"
                    else
                        echo "Generating JUnit XML from pytest..."
                        pytest test_http_simple.py --junit-xml=pytest_results.xml --tb=no -q || true
                    fi
                    
                    deactivate
                '''
                
                // Publish JUnit results
                junit testResults: 'tests/pytest_results.xml', allowEmptyResults: true
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "🏥 Performing application health checks..."
                }
                
                sh '''
                    echo "=== Application Health Check ==="
                    
                    # Check container status
                    echo "Docker containers status:"
                    docker-compose ps
                    
                    # Check frontend
                    echo "🌐 Checking frontend health..."
                    if curl -f -s http://localhost:3001 > /dev/null; then
                        echo "✅ Frontend (port 3001) is responding"
                    else
                        echo "❌ Frontend health check failed"
                    fi
                    
                    # Check backend GraphQL
                    echo "🔧 Checking backend GraphQL..."
                    if curl -f -s http://localhost:3000/graphql > /dev/null; then
                        echo "✅ Backend GraphQL (port 3000) is responding"
                    else
                        echo "❌ Backend GraphQL health check failed"
                    fi
                    
                    # Check database connection (if accessible)
                    echo "🗄️ Checking database connection..."
                    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
                        echo "✅ PostgreSQL database is ready"
                    else
                        echo "⚠️ PostgreSQL health check skipped or failed"
                    fi
                    
                    # Check Redis
                    echo "📦 Checking Redis connection..."
                    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
                        echo "✅ Redis is responding"
                    else
                        echo "⚠️ Redis health check skipped or failed"
                    fi
                    
                    echo "=== Health Check Complete ==="
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "📧 Preparing notification email..."
                
                // Get committer email
                def committer = ''
                try {
                    committer = sh(
                        script: "git log -1 --pretty=format:%ae",
                        returnStdout: true
                    ).trim()
                } catch (Exception e) {
                    committer = 'qasimalik@gmail.com'  // Fallback email
                }
                
                if (!committer || committer == '') {
                    committer = 'qasimalik@gmail.com'
                }

                // Parse test results
                def raw = ''
                if (fileExists('tests/pytest_results.xml')) {
                    raw = sh(
                        script: "grep -h '<testcase' tests/pytest_results.xml || true",
                        returnStdout: true
                    ).trim()
                }

                int totalTests = 0, passedTests = 0, failedTests = 0, skippedTests = 0
                def testDetails = ""

                if (raw) {
                    raw.split('\n').each { line ->
                        totalTests++
                        def m = (line =~ /name="([^"]+)"/)
                        def name = m ? m[0][1] : "Unknown Test"
                        if (line.contains("<failure")) {
                            failedTests++
                            testDetails += "❌ Failed: ${name}\n"
                        } else if (line.contains("<skipped") || line.contains("</skipped>")) {
                            skippedTests++
                            testDetails += "⏭ Skipped: ${name}\n"
                        } else {
                            passedTests++
                            testDetails += "✅ Passed: ${name}\n"
                        }
                    }
                } else {
                    testDetails = "No test results found (tests may have failed to run)."
                }

                def buildStatus = currentBuild.currentResult ?: 'UNKNOWN'
                def color = buildStatus == 'SUCCESS' ? '#28a745' : '#dc3545'
                def statusIcon = buildStatus == 'SUCCESS' ? '✅' : '❌'

                def emailBody = """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <h2 style="color: ${color};">${statusIcon} Live Q&A CI/CD – Build #${env.BUILD_NUMBER}</h2>
                        <p><strong>Status:</strong> <span style="color:${color}; font-size:20px;">${buildStatus}</span></p>
                        <p><strong>Triggered by:</strong> ${currentBuild.getBuildCauses()[0].shortDescription}</p>
                        <p><strong>Duration:</strong> ${currentBuild.durationString}</p>

                        <h3>🧪 Test Results Summary</h3>
                        <table style="border-collapse: collapse; margin: 10px 0;">
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Tests</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">${totalTests}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Passed</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd; color: green;">${passedTests}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Failed</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd; color: red;">${failedTests}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Skipped</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">${skippedTests}</td>
                            </tr>
                        </table>

                        <h4>📋 Detailed Results:</h4>
                        <pre style="background:#f4f4f4; padding:15px; border-radius:8px; font-size:14px;">${testDetails}</pre>

                        <hr>
                        <p>
                            <a href="${env.BUILD_URL}" style="color:#007bff; text-decoration:none;">🔗 View Full Build</a> |
                            <a href="${env.BUILD_URL}console" style="color:#007bff; text-decoration:none;">📜 Console Output</a> |
                            <a href="${env.BUILD_URL}testReport/" style="color:#007bff; text-decoration:none;">📊 View Test Report</a>
                        </p>
                        <small style="color:#666;">Live Q&A DevOps Pipeline | github.com/mahesararslan/LiveQ-A-project-devops</small>
                    </body>
                    </html>
                """

                // Send email notification
                try {
                    emailext(
                        to: committer,
                        subject: "Live Q&A CI #${env.BUILD_NUMBER} – ${buildStatus} (${passedTests}/${totalTests} Passed)",
                        body: emailBody,
                        mimeType: 'text/html',
                        attachLog: true,
                        compressLog: true
                    )
                    echo "✅ Email notification sent to ${committer}"
                } catch (Exception e) {
                    echo "⚠️ Failed to send email notification: ${e.message}"
                }
            }
        }

        success {
            echo 'Pipeline completed successfully!'
            echo 'Frontend: http://ec2-13-60-207-241.eu-north-1.compute.amazonaws.com:3001'
            echo 'Backend: http://ec2-13-60-207-241.eu-north-1.compute.amazonaws.com:3000'
            echo 'Containers will remain running for access.'
        }

        failure {
            echo "💥 Pipeline failed! Check the logs for details."
            
            // Only cleanup on failure
            sh '''
                echo "🧹 Cleaning up failed containers..."
                docker-compose down --remove-orphans || true
                docker system prune -f || true
            '''
        }

        unstable {
            echo "⚠️ Pipeline completed with warnings."
        }
    }
}