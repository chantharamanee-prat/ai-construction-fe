// 1. เปลี่ยนจากการใช้ def เป็น env.DISCORD_WEBHOOK
env.DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1384405075451187210/PNnpJr4Aw8VLW8H0IXpgQd9QZiY5ePJcJM0c2KTe-cW4grRSJREqW0_ZSjdqBll7LRb6'

def sendDiscordNoti(String message) {
    // 2. เรียกใช้ตัวแปรผ่าน env.DISCORD_WEBHOOK
    sh """
    curl -H "Content-Type: application/json" \\
         -d '{"content": "${message}"}' \\
         ${env.DISCORD_WEBHOOK}
    """
}

def scmVars

node {
    try {
        stage('Checkout') {
            scmVars = checkout scm
            echo "Current branch: ${scmVars.GIT_BRANCH}"
            
            sendDiscordNoti("🚀 **[Jenkins]** Started pipeline for branch: `${scmVars.GIT_BRANCH}`")
        }
        
        stage('Build') {
            if (scmVars.GIT_BRANCH.endsWith('/master') || scmVars.GIT_BRANCH == 'master') {
                sh 'docker build -t yolo-server-api -f Dockerfile .'
                sh 'docker build -t yolo-server-web -f web/Dockerfile web/'
            } else {
                echo "Skipped."
            }
        }
        
        stage('Deploy Docker') {
            if (scmVars.GIT_BRANCH.endsWith('/master') || scmVars.GIT_BRANCH == 'master') {
                sh 'docker compose down'
                sh 'docker compose up -d'
                
                sendDiscordNoti("✅ **[Jenkins]** Build & Deploy completed successfully for branch: `${scmVars.GIT_BRANCH}`!")
            } else {
                echo "Skipped."
                sendDiscordNoti("ℹ️ **[Jenkins]** Pipeline finished for branch: `${scmVars.GIT_BRANCH}` (Skipped Build & Deploy)")
            }
        }
        
    } catch (Exception e) {
        def branchName = scmVars?.GIT_BRANCH ?: 'unknown branch'
        sendDiscordNoti("❌ **[Jenkins]** Pipeline **FAILED** for branch: `${branchName}`\\n**Error:** ${e.getMessage()}")
        
        throw e
    }
}