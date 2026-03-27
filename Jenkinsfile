def DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1384405075451187210/PNnpJr4Aw8VLW8H0IXpgQd9QZiY5ePJcJM0c2KTe-cW4grRSJREqW0_ZSjdqBll7LRb6'

// ฟังก์ชันสำหรับส่งข้อความไปยัง Discord
def sendDiscordNoti(String message) {
    sh """
    curl -H "Content-Type: application/json" \\
         -d '{"content": "${message}"}' \\
         ${DISCORD_WEBHOOK}
    """
}

def scmVars

node {
    try {
        stage('Checkout') {
            scmVars = checkout scm
            echo "Current branch: ${scmVars.GIT_BRANCH}"
            
            // ส่ง Noti แจ้งว่าเริ่มทำงาน
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
                
                // ส่ง Noti แจ้งว่า Deploy สำเร็จ (เฉพาะ branch master)
                sendDiscordNoti("✅ **[Jenkins]** Build & Deploy completed successfully for branch: `${scmVars.GIT_BRANCH}`!")
            } else {
                echo "Skipped."
                // ส่ง Noti แจ้งว่าทำงานเสร็จแต่ไม่ได้ Deploy
                sendDiscordNoti("ℹ️ **[Jenkins]** Pipeline finished for branch: `${scmVars.GIT_BRANCH}` (Skipped Build & Deploy)")
            }
        }
        
    } catch (Exception e) {
        // ส่ง Noti หากเกิดข้อผิดพลาด (Pipeline พัง)
        def branchName = scmVars?.GIT_BRANCH ?: 'unknown branch'
        sendDiscordNoti("❌ **[Jenkins]** Pipeline **FAILED** for branch: `${branchName}`\\n**Error:** ${e.getMessage()}")
        
        // Throw error กลับออกไปเพื่อให้ Jenkins ขึ้นสถานะ Failed
        throw e
    }
}